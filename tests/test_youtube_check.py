"""The upload-package lint passes the model description, fires on each rule, and reads the watch page."""

import importlib.util
import io
import json
import pathlib

import pytest
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("talks_youtube_check", ROOT / "videos" / "youtube_check.py")
assert _spec and _spec.loader
yc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(yc)

MODEL = (ROOT / "videos" / "youtube-director" / "references" / "example-description.txt").read_text()
GOOD = """Why does a robot drift when its wheels slip?

I drive a Webots e-puck through three mazes and compare odometry with the true pose.

00:00 Introduction
00:12 Odometry
01:40 Wrap-up

Code: https://github.com/example/robots
More videos: https://youtube.com/@AJBarea

#robotics #webots
"""


def problems(text: str, **kw) -> list[str]:
    return [p for _, p in yc.check_description(text, **kw)]


def test_the_model_and_a_minimal_description_pass() -> None:
    assert yc.check_description(MODEL, duration=332, ai=True) == []
    assert yc.check_description(GOOD, duration=200) == []


def test_every_committed_description_passes() -> None:
    assert yc.main([]) == 0


@pytest.mark.parametrize(
    ("old", "new", "fires"),
    [
        ("00:00 Introduction", "00:05 Introduction", "start at 0:00"),
        ("00:12 Odometry\n", "", "at least 3"),
        ("00:12 Odometry", "00:09 Odometry", "lasts 9 s"),
        ("00:00 Introduction\n00:12 Odometry", "00:00 Introduction 00:12 Odometry", "own line"),
        ("robots\n", "robots https://x.org\n", "link"),
        ("#robotics #webots", "#a #b #c #d #e #f #g #h #i", "9 hashtags"),
        ("three mazes", "three <mazes>", "< and >"),
        ("Why does a robot drift when its wheels slip?", "https://example.org", "hook sentence"),
        ("Why does a robot drift when its wheels slip?", "Why " * 40, "hook is"),
        ("#robotics", "#robotics " + "x" * 5000, "bytes"),
    ],
)
def test_each_rule_fires(old: str, new: str, fires: str) -> None:
    assert old in GOOD
    assert any(fires in p for p in problems(GOOD.replace(old, new, 1))), problems(GOOD.replace(old, new, 1))


def test_glued_chapters_inside_prose_fire() -> None:
    glued = GOOD.replace("00:00 Introduction\n00:12 Odometry\n01:40", "See 00:00 Introduction 00:12 Odometry 01:40")
    assert any("own line" in p for p in problems(glued))


def test_last_chapter_needs_ten_seconds_before_the_end() -> None:
    assert any("last chapter lasts 5 s" in p for p in problems(GOOD, duration=105))


def test_ai_narration_needs_the_disclosure_line() -> None:
    assert any("AI avatar" in p for p in problems(GOOD, ai=True))
    assert problems(GOOD + "\nAn AI avatar of me narrates this video.\n", ai=True) == []


def test_url_fragments_and_crlf_are_not_problems() -> None:
    text = GOOD.replace("Code: https://github.com/example/robots", "Docs: https://example.org/page#section-2")
    assert yc.check_description(text.replace("\n", "\r\n")) == []


def _bar(*marks: tuple[str, int]) -> dict:
    chaps = [{"chapterRenderer": {"title": {"simpleText": t}, "timeRangeStartMillis": s * 1000}} for t, s in marks]
    markers = [{"key": "DESCRIPTION_CHAPTERS", "value": {"chapters": chaps}}]
    bar = {"multiMarkersPlayerBarRenderer": {"markersMap": markers}}
    return {"playerOverlays": {"playerOverlayRenderer": {"decoratedPlayerBarRenderer": {"x": {"playerBar": bar}}}}}


def _page(description: str, marks: list[tuple[str, int]], label: str = "") -> bytes:
    data = _bar(*marks)
    if label:
        made = {"howThisWasMadeSectionViewModel": {"bodyHeader": {"content": label}}}
        data["engagementPanels"] = [{"items": [made]}]
    player = {"videoDetails": {"title": "T", "shortDescription": description, "lengthSeconds": "200"}}
    scripts = f"var ytInitialPlayerResponse = {json.dumps(player)};", f"var ytInitialData = {json.dumps(data)};"
    return "".join(f"<script>{s}</script>" for s in scripts).encode()


def _jpeg(shade: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (480, 360), (shade, shade, shade)).save(buf, "JPEG")
    return buf.getvalue()


def _fake(page: bytes, shown: int, frames: tuple[int, int, int] = (10, 120, 240)):
    def get(url: str) -> bytes:
        if "watch?v=" in url:
            return page
        name = url.rsplit("/", 1)[1].removesuffix(".jpg")
        return _jpeg(shown if name == "hqdefault" else frames[int(name[-1]) - 1])

    return get


def _results(get, **kw) -> dict[str, tuple[bool, str]]:
    return {name: (ok, detail) for name, ok, detail in yc.verify("vid", get=get, **kw)}


def test_a_finished_upload_passes_live() -> None:
    marks = [("Introduction", 0), ("Odometry", 12), ("Wrap-up", 100)]
    r = _results(_fake(_page(GOOD + "\nAn AI avatar of me narrates.\n", marks, "Made with AI"), shown=60), ai=True)
    assert all(ok for ok, _ in r.values()), r
    assert r["thumbnail"][1] == "custom"


def test_live_catches_lost_chapters_missing_label_and_auto_thumbnail() -> None:
    r = _results(_fake(_page(GOOD + "\nAn AI avatar of me narrates.\n", []), shown=120), ai=True)
    assert r["chapters"] == (False, "0 on the scrub bar, 3 in the description")
    assert r["AI label"][0] is False
    assert r["thumbnail"] == (False, "auto frame 2")
    assert _results(_fake(_page(GOOD, []), shown=120), auto_thumbnail=True)["thumbnail"][0] is True


def test_a_label_without_the_disclosure_line_fails() -> None:
    marks = [("Introduction", 0), ("Odometry", 12), ("Wrap-up", 100)]
    r = _results(_fake(_page(GOOD, marks, "Made with AI"), shown=60), ai=True)
    assert r["AI label"][0] is True
    assert r["description"][0] is False


def test_ai_label_follows_the_flag_not_the_wording() -> None:
    marks = [("Introduction", 0), ("Odometry", 12), ("Wrap-up", 100)]
    talk = GOOD + "\nA talk about AI-generated code.\n"
    assert _results(_fake(_page(talk, marks), shown=60))["AI label"][0] is True
    assert _results(_fake(_page(GOOD, marks, "Made with AI"), shown=60))["AI label"][0] is False


def test_talking_about_ai_is_not_a_disclosure() -> None:
    assert any("AI-narrated" in p for p in problems(GOOD + "\nA talk about AI-generated code.\n", ai=True))
    assert not problems(GOOD + "\nAn AI avatar of me narrates this video.\n", ai=True)


def test_descending_chapters_say_so() -> None:
    text = GOOD.replace("00:12 Odometry", "00:12 Odometry\n00:05 Back")
    assert any("must go up" in p for p in problems(text))


def test_live_takes_an_id_that_starts_with_a_dash(monkeypatch) -> None:
    seen = {}
    monkeypatch.setattr(yc, "verify", lambda v, ai, auto: seen.setdefault("id", v) and [])
    assert yc.main(["--live=-Pe9a4knLwc"]) == 0
    assert seen["id"] == "-Pe9a4knLwc"


def test_scrub_bar_chapters_are_counted_once() -> None:
    data = _bar(("A", 0), ("B", 20))
    data["playerOverlays"]["copy"] = _bar(("A", 0), ("B", 20))
    assert yc.page_facts(data, {})["chapters"] == [("A", 0), ("B", 20)]
