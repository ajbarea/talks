#!/usr/bin/env python3
"""Generate complete TTS audio and synced subtitles for a talk.

Features:
- Slide-by-slide concurrent synthesis (no timeouts or dropped lines).
- British Sonia voice (en-GB-SoniaNeural) at +6% rate by default.
- Gentle audio chime between slide transitions so listeners know when to turn the slide.
- Exact WebVTT subtitle cue generation.

Usage:
    python3 scripts/tts.py federated-agents-step-one
    python3 scripts/tts.py federated-agents-step-one --rate +10%
    python3 scripts/tts.py federated-agents-step-one --no-chime
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_VOICE = "en-GB-SoniaNeural"
DEFAULT_RATE = "+6%"


def get_duration(file_path: str | pathlib.Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(file_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def format_vtt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def extract_slides(talk_name: str) -> list[tuple[str, str]]:
    script_runner = ROOT / "scripts" / "script_length.py"
    res = subprocess.run(
        [sys.executable, str(script_runner), talk_name, "--print"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Error resolving script for {talk_name}:\n{res.stderr}")

    slides: list[tuple[str, str]] = []
    curr_title = ""
    curr_lines: list[str] = []

    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            if curr_lines:
                slides.append((curr_title, " ".join(curr_lines)))
                curr_lines = []
            curr_title = line
            continue
        if line.startswith("#") or line.startswith("<!--") or line.endswith("-->"):
            continue
        cleaned = line.replace("▶", "").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned:
            curr_lines.append(cleaned)

    if curr_lines:
        slides.append((curr_title, " ".join(curr_lines)))

    return slides


def generate_chime(output_path: pathlib.Path) -> None:
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
        "-b:a",
        "48k",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


async def synthesize_all_slides(
    slides: list[tuple[str, str]],
    voice: str,
    rate: str,
    temp_dir: pathlib.Path,
    concurrency: int = 5,
) -> None:
    try:
        import edge_tts
    except ImportError:
        print("Error: edge-tts is required. Run with `uv run --with edge-tts python3 ...`", file=sys.stderr)
        sys.exit(1)

    sem = asyncio.Semaphore(concurrency)

    async def synth_one(idx: int, text: str) -> None:
        out_file = temp_dir / f"slide_{idx:02d}.mp3"
        async with sem:
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(str(out_file))

    tasks = [synth_one(i, text) for i, (_, text) in enumerate(slides, 1)]
    await asyncio.gather(*tasks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("talk", help="Name of the talk directory")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="TTS voice (default: %(default)s)")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speech rate (default: +6%%)")
    parser.add_argument("--no-chime", action="store_true", help="Do not play audio chime on slide transition")
    parser.add_argument("--out", help="Output MP3 filename (default: <talk>/talk.mp3)")
    args = parser.parse_args()

    talk_dir = ROOT / args.talk
    if not talk_dir.is_dir():
        print(f"Error: talk directory '{args.talk}' not found at {talk_dir}", file=sys.stderr)
        return 1

    slides = extract_slides(args.talk)
    if not slides:
        print(f"Error: No slides found for {args.talk}", file=sys.stderr)
        return 1

    # Save spoken text reference
    spoken_text = "\n\n".join(text for _, text in slides)
    (talk_dir / "spoken_script.txt").write_text(spoken_text + "\n", encoding="utf-8")

    out_mp3 = pathlib.Path(args.out) if args.out else talk_dir / "talk.mp3"
    out_vtt = out_mp3.with_suffix(".vtt")

    with tempfile.TemporaryDirectory() as tmp_d:
        tmp_dir = pathlib.Path(tmp_d)
        print(f"Synthesizing {len(slides)} slides with '{args.voice}' (rate: {args.rate})...")
        asyncio.run(synthesize_all_slides(slides, args.voice, args.rate, tmp_dir))

        # Build silence and chime assets
        silence_03 = tmp_dir / "silence_03.mp3"
        silence_04 = tmp_dir / "silence_04.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=24000:cl=mono",
                "-t",
                "0.3",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "48k",
                str(silence_03),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=24000:cl=mono",
                "-t",
                "0.4",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "48k",
                str(silence_04),
            ],
            check=True,
            capture_output=True,
        )

        chime_file = tmp_dir / "chime.mp3"
        if not args.no_chime:
            generate_chime(chime_file)
            # Also keep a copy in the talk directory for reference
            shutil.copy(chime_file, talk_dir / "slide_chime.mp3")

        # Assemble concatenation list and build VTT
        concat_list = tmp_dir / "concat_list.txt"
        vtt_entries = ["WEBVTT", ""]
        current_time = 0.0

        transition_dur = 0.0
        if not args.no_chime:
            transition_dur = get_duration(silence_03) + get_duration(chime_file) + get_duration(silence_04)
        else:
            transition_dur = get_duration(silence_03)

        with open(concat_list, "w") as cl:
            for idx, (title, text) in enumerate(slides, 1):
                if idx > 1:
                    if not args.no_chime:
                        cl.write(f"file '{silence_03}'\n")
                        cl.write(f"file '{chime_file}'\n")
                        cl.write(f"file '{silence_04}'\n")
                    else:
                        cl.write(f"file '{silence_03}'\n")

                slide_file = tmp_dir / f"slide_{idx:02d}.mp3"
                dur = get_duration(slide_file)

                start_ts = format_vtt_ts(current_time)
                end_ts = format_vtt_ts(current_time + dur)
                vtt_entries.append(str(idx))
                vtt_entries.append(f"{start_ts} --> {end_ts}")
                vtt_entries.append(f"{title}\n{text}")
                vtt_entries.append("")

                current_time += dur + transition_dur
                cl.write(f"file '{slide_file}'\n")

        # Concatenate audio
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(out_mp3)],
            check=True,
            capture_output=True,
        )

        out_vtt.write_text("\n".join(vtt_entries) + "\n", encoding="utf-8")

        total_dur = get_duration(out_mp3)
        print(f"✓ Created: {out_mp3} ({total_dur:.1f}s / {total_dur / 60:.1f}m)")
        print(f"✓ Created: {out_vtt}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
