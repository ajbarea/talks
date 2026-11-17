#!/usr/bin/env python3
"""Generate complete rehearsal TTS audio and synced WebVTT subtitles for a talk.

Features:
- Local Kokoro speech synthesis via keryx (or optional edge-tts fallback).
- Slide-by-slide synthesis with slide change chimes.
- W3C-compliant WebVTT subtitle cue generation with period timestamp separators.
- Automatic slide script resolution and figure extraction.

Usage:
    python3 scripts/tts.py federated-agents-step-one
    python3 scripts/tts.py federated-agents-step-one --voice am_michael
    python3 scripts/tts.py federated-agents-step-one --engine edge-tts --voice en-GB-SoniaNeural
    python3 scripts/tts.py federated-agents-step-one --no-chime
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_EDGE_VOICE = "en-GB-SoniaNeural"
DEFAULT_EDGE_RATE = "+6%"
DEFAULT_KERYX_VOICE = "bf_emma"


def get_duration(file_path: str | pathlib.Path) -> float:
    """Return the duration in seconds of an audio file using ffprobe."""
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(file_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def format_vtt_ts(seconds: float) -> str:
    """Format seconds into W3C WebVTT timestamp (HH:MM:SS.mmm)."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def parse_script_text(raw_text: str) -> list[tuple[str, str]]:
    """Extract slide titles and clean spoken narration lines from script markdown."""
    slides: list[tuple[str, str]] = []
    curr_title = ""
    curr_lines: list[str] = []

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            if curr_lines:
                slides.append((curr_title, " ".join(curr_lines)))
                curr_lines = []
            curr_title = line[3:].strip()
            continue
        # Skip markdown top headings or HTML comment lines
        if line.startswith("#") or line.startswith("<!--") or line.endswith("-->"):
            continue
        # Strip click markers (▶) and collapse multiple whitespace
        cleaned = line.replace("▶", "").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned:
            curr_lines.append(cleaned)

    if curr_lines:
        slides.append((curr_title, " ".join(curr_lines)))

    return slides


def extract_slides(talk_name: str, root: pathlib.Path = ROOT) -> list[tuple[str, str]]:
    """Resolve and extract slides for a talk, filling template figures if available."""
    script_runner = root / "scripts" / "script_length.py"
    if script_runner.is_file():
        res = subprocess.run(
            [sys.executable, str(script_runner), talk_name, "--print"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return parse_script_text(res.stdout)

    # Fallback to reading the raw script.md directly
    script_path = root / talk_name / "script.md"
    if not script_path.is_file():
        raise FileNotFoundError(f"Could not find talk script at {script_path}")
    return parse_script_text(script_path.read_text(encoding="utf-8"))


def find_keryx_command() -> list[str] | None:
    """Find a runnable keryx command capable of --out file synthesis."""
    if "KERYX_BIN" in os.environ:
        return [os.environ["KERYX_BIN"]]

    # Check sibling checkout
    sibling_keryx = ROOT.parent / "keryx"
    if sibling_keryx.is_dir() and (sibling_keryx / "pyproject.toml").is_file() and shutil.which("uv"):
        return ["uv", "run", "--project", str(sibling_keryx), "keryx"]

    # Check PATH binary
    which_keryx = shutil.which("keryx")
    if which_keryx:
        return [which_keryx]

    return None


def detect_engine(
    requested_engine: str | None = None,
    requested_voice: str | None = None,
) -> str:
    """Determine whether to use keryx or edge-tts."""
    if requested_engine and requested_engine != "auto":
        return requested_engine.lower()

    if requested_voice and (
        "Neural" in requested_voice or requested_voice.startswith(("en-US-", "en-GB-", "es-", "fr-"))
    ):
        return "edge-tts"

    if find_keryx_command() is not None:
        return "keryx"

    return "edge-tts"


def to_wav(src: pathlib.Path, dst: pathlib.Path) -> pathlib.Path:
    """Re-encode SRC as 24 kHz mono 16-bit WAV at DST, the one format the join takes."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True,
        capture_output=True,
    )
    return dst


def generate_chime(output_path: pathlib.Path) -> None:
    """Generate a gentle two-tone slide transition chime via ffmpeg."""
    filter_str = (
        "sine=f=587.33:d=0.25[n1];"
        "sine=f=880.00:d=0.45[n2];"
        "[n1]afade=t=in:st=0:d=0.005,afade=t=out:st=0.08:d=0.17,volume=1.0[a1];"
        "[n2]afade=t=in:st=0:d=0.005,afade=t=out:st=0.10:d=0.35,volume=1.0,adelay=140|140[a2];"
        "[a1][a2]amix=inputs=2:duration=longest,volume=4.0,alimiter=limit=0.85"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        filter_str,
        "-ar",
        "24000",
        "-ac",
        "1",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def synthesize_keryx_slides(
    slides: list[tuple[str, str]],
    voice: str | None,
    temp_dir: pathlib.Path,
    cmd_base: list[str],
) -> list[pathlib.Path]:
    """Synthesize each slide with keryx say --out."""
    output_files: list[pathlib.Path] = []
    for idx, (_, text) in enumerate(slides, 1):
        out_file = temp_dir / f"slide_{idx:02d}.wav"
        cmd = [*cmd_base, "say", "--out", str(out_file)]
        if voice:
            cmd.extend(["--voice", voice])
        cmd.append(text)
        subprocess.run(cmd, check=True, capture_output=True)
        output_files.append(out_file)
    return output_files


async def synthesize_edge_slides(
    slides: list[tuple[str, str]],
    voice: str,
    rate: str,
    temp_dir: pathlib.Path,
    concurrency: int = 5,
) -> list[pathlib.Path]:
    """Synthesize each slide with edge-tts."""
    try:
        import edge_tts
    except ImportError:
        print("Error: edge-tts is required. Run with `uv run --with edge-tts python3 ...`", file=sys.stderr)
        sys.exit(1)

    sem = asyncio.Semaphore(concurrency)
    output_files: list[pathlib.Path] = [temp_dir / f"slide_{i:02d}.mp3" for i in range(1, len(slides) + 1)]

    async def synth_one(idx: int, text: str, out_file: pathlib.Path) -> None:
        async with sem:
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(str(out_file))

    tasks = [
        synth_one(i, text, out_file)
        for i, ((_, text), out_file) in enumerate(zip(slides, output_files, strict=True), 1)
    ]
    await asyncio.gather(*tasks)
    return output_files


def build_vtt_cues(
    slides: list[tuple[str, str]],
    slide_durations: list[float],
    chime_dur: float,
    lead_silence: float = 0.3,
    trail_silence: float = 0.4,
    include_chime: bool = True,
) -> str:
    """Build a W3C-compliant WebVTT subtitle track."""
    vtt_lines: list[str] = ["WEBVTT", ""]
    current_time = 0.0
    cue_idx = 1

    for idx, ((_, text), dur) in enumerate(zip(slides, slide_durations, strict=True), 1):
        if idx > 1 and include_chime:
            current_time += lead_silence
            chime_start = format_vtt_ts(current_time)
            chime_end = format_vtt_ts(current_time + chime_dur)
            vtt_lines.append(str(cue_idx))
            vtt_lines.append(f"{chime_start} --> {chime_end}")
            vtt_lines.append("[Slide change chime]")
            vtt_lines.append("")
            cue_idx += 1
            current_time += chime_dur + trail_silence
        elif idx > 1 and not include_chime:
            current_time += lead_silence

        start_ts = format_vtt_ts(current_time)
        end_ts = format_vtt_ts(current_time + dur)
        vtt_lines.append(str(cue_idx))
        vtt_lines.append(f"{start_ts} --> {end_ts}")
        vtt_lines.append(text)
        vtt_lines.append("")
        cue_idx += 1
        current_time += dur

    return "\n".join(vtt_lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("talk", help="Name of the talk directory")
    parser.add_argument(
        "--engine",
        choices=["auto", "keryx", "edge-tts"],
        default="auto",
        help="TTS engine (default: auto)",
    )
    parser.add_argument(
        "--voice",
        help="Voice name (default: bf_emma for keryx, en-GB-SoniaNeural for edge-tts)",
    )
    parser.add_argument("--rate", default=DEFAULT_EDGE_RATE, help="Speech rate for edge-tts (default: +6%%)")
    parser.add_argument("--no-chime", action="store_true", help="Do not play audio chime on slide transition")
    parser.add_argument("--out", help="Output audio filename (default: <talk>/talk.mp3)")
    args = parser.parse_args(argv)

    talk_dir = ROOT / args.talk
    if not talk_dir.is_dir():
        print(f"Error: talk directory '{args.talk}' not found at {talk_dir}", file=sys.stderr)
        return 1

    slides = extract_slides(args.talk, ROOT)
    if not slides:
        print(f"Error: No slides found for {args.talk}", file=sys.stderr)
        return 1

    engine = detect_engine(args.engine, args.voice)
    voice = args.voice
    if not voice:
        voice = DEFAULT_KERYX_VOICE if engine == "keryx" else DEFAULT_EDGE_VOICE

    # Save spoken text reference
    spoken_text = "\n\n".join(f"## {title}\n{text}" for title, text in slides)
    (talk_dir / "spoken_script.txt").write_text(spoken_text + "\n", encoding="utf-8")

    out_audio = pathlib.Path(args.out) if args.out else talk_dir / "talk.mp3"
    out_vtt = out_audio.with_suffix(".vtt")

    with tempfile.TemporaryDirectory() as tmp_d:
        tmp_dir = pathlib.Path(tmp_d)
        print(f"Synthesizing {len(slides)} slides with {engine} ({voice})...")

        if engine == "keryx":
            cmd_base = find_keryx_command()
            if not cmd_base:
                print("Error: keryx requested but not available", file=sys.stderr)
                return 1
            slide_files = synthesize_keryx_slides(slides, voice, tmp_dir, cmd_base)
        else:
            slide_files = asyncio.run(synthesize_edge_slides(slides, voice, args.rate, tmp_dir))

        # The concat demuxer copies streams, so every piece must share one format:
        # edge-tts writes MP3 and the chime and silences are WAV.
        slide_files = [to_wav(f, tmp_dir / f"slide_{i:03d}.wav") for i, f in enumerate(slide_files, 1)]
        slide_durations = [get_duration(f) for f in slide_files]

        # Prepare silence assets
        silence_03 = tmp_dir / "silence_03.wav"
        silence_04 = tmp_dir / "silence_04.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.3", str(silence_03)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.4", str(silence_04)],
            check=True,
            capture_output=True,
        )

        chime_file = tmp_dir / "chime.wav"
        chime_dur = 0.0
        if not args.no_chime:
            generate_chime(chime_file)
            chime_file = to_wav(chime_file, tmp_dir / "chime_24k.wav")
            chime_dur = get_duration(chime_file)
            shutil.copy(chime_file, talk_dir / "slide_chime.wav")

        # Assemble concatenation list for ffmpeg concat demuxer
        concat_list = tmp_dir / "concat_list.txt"
        with open(concat_list, "w", encoding="utf-8") as cl:
            for idx, slide_file in enumerate(slide_files, 1):
                if idx > 1:
                    if not args.no_chime:
                        cl.write(f"file '{silence_03}'\n")
                        cl.write(f"file '{chime_file}'\n")
                        cl.write(f"file '{silence_04}'\n")
                    else:
                        cl.write(f"file '{silence_03}'\n")
                cl.write(f"file '{slide_file}'\n")

        # Concatenate audio into final file
        codec_args = ["-c:a", "libmp3lame", "-b:a", "128k"] if out_audio.suffix == ".mp3" else []
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), *codec_args, str(out_audio)],
            check=True,
            capture_output=True,
        )

        # Generate synced WebVTT
        vtt_content = build_vtt_cues(
            slides=slides,
            slide_durations=slide_durations,
            chime_dur=chime_dur,
            lead_silence=0.3,
            trail_silence=0.4,
            include_chime=not args.no_chime,
        )
        out_vtt.write_text(vtt_content, encoding="utf-8")

        total_dur = get_duration(out_audio)
        print(f"✓ Created: {out_audio} ({total_dur:.1f}s / {total_dur / 60:.1f}m)")
        print(f"✓ Created: {out_vtt}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
