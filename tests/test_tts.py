"""Unit tests for talk rehearsal audio generation and WebVTT captioning."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("talks_tts", ROOT / "scripts" / "tts.py")
assert spec and spec.loader
tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tts)


def test_format_vtt_ts_produces_w3c_period_format() -> None:
    assert tts.format_vtt_ts(0.0) == "00:00:00.000"
    assert tts.format_vtt_ts(14.04) == "00:00:14.040"
    assert tts.format_vtt_ts(75.5) == "00:01:15.500"
    assert tts.format_vtt_ts(3665.123) == "01:01:05.123"
    # Never commas
    assert "," not in tts.format_vtt_ts(12.345)


def test_format_vtt_ts_handles_negative_values() -> None:
    assert tts.format_vtt_ts(-5.0) == "00:00:00.000"


def test_parse_script_text_extracts_clean_narration() -> None:
    sample = """# Deck Title

<!-- Comment line that should be skipped -->

## 1. Welcome

Hi, I am AJ.
Today we talk about Sphragis.

## 2. Six Parts

Six parts.
▶ The bigger problem, and ▶ where this connects.
<!-- another comment -->

## 3. Empty Slide
"""
    slides = tts.parse_script_text(sample)
    assert len(slides) == 2
    assert slides[0][0] == "1. Welcome"
    assert slides[0][1] == "Hi, I am AJ. Today we talk about Sphragis."
    assert slides[1][0] == "2. Six Parts"
    assert slides[1][1] == "Six parts. The bigger problem, and where this connects."
    assert "▶" not in slides[1][1]
    assert "<!--" not in slides[1][1]


def test_build_vtt_cues_includes_chime_sound_effects() -> None:
    slides = [
        ("1. Intro", "Welcome everyone."),
        ("2. Background", "Here is the context."),
    ]
    durations = [5.0, 8.0]
    chime_dur = 0.45
    vtt = tts.build_vtt_cues(slides, durations, chime_dur=chime_dur, include_chime=True)

    assert vtt.startswith("WEBVTT\n")
    # Slide 1 cue
    assert "1\n00:00:00.000 --> 00:00:05.000\nWelcome everyone." in vtt
    # Chime sound effect cue
    assert "2\n00:00:05.300 --> 00:00:05.750\n[Slide change chime]" in vtt
    # Slide 2 cue
    assert "3\n00:00:06.150 --> 00:00:14.150\nHere is the context." in vtt


def test_build_vtt_cues_without_chime() -> None:
    slides = [
        ("1. Intro", "Welcome everyone."),
        ("2. Background", "Here is the context."),
    ]
    durations = [4.0, 6.0]
    vtt = tts.build_vtt_cues(slides, durations, chime_dur=0.0, include_chime=False)

    assert "[Slide change chime]" not in vtt
    assert "1\n00:00:00.000 --> 00:00:04.000\nWelcome everyone." in vtt
    assert "2\n00:00:04.300 --> 00:00:10.300\nHere is the context." in vtt


def test_detect_engine_resolves_expected_defaults() -> None:
    assert tts.detect_engine("keryx", None) == "keryx"
    assert tts.detect_engine("edge-tts", None) == "edge-tts"
    assert tts.detect_engine("auto", "en-GB-SoniaNeural") == "edge-tts"
    assert tts.detect_engine("auto", "en-US-GuyNeural") == "edge-tts"
