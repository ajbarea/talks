"""The video-script lint passes every committed script and fires on each rule it enforces."""

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("talks_check_script", ROOT / "videos" / "check_script.py")
assert _spec and _spec.loader
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

GOOD = """# Video Script: Test

### Segment 1 (0:00 – 0:10): Hook

* **Environment & Lighting:** A desk at night, warm lamp from the left.
* **Avatar (Wardrobe & Physicality):** Charcoal t-shirt. At 0:04, leans in.
* **Visual Overlay:** A card reads 'context rot' and code `print('hi')`.
* **Spoken Script:**
  "Say you give your agent fifty rules. It breaks one. Here's why."
* **Vocal Direction:** Relaxed; stress 'fifty'.

---

## Audio Prompt

Music with "quotes" here is not a segment, so it is not checked.
"""


def problems(text: str) -> list[str]:
    return [message for _, message in cs.check(text)]


def test_a_complete_segment_passes() -> None:
    assert cs.check(GOOD) == []


@pytest.mark.parametrize("script", sorted((ROOT / "videos").glob("*/script.md")), ids=lambda p: p.parent.name)
def test_every_committed_script_passes(script: pathlib.Path) -> None:
    """Runs what `make videos-check` runs, so CI fails a script that breaks a rule."""
    assert cs.check(script.read_text(encoding="utf-8")) == []


def test_main_checks_every_script_by_default() -> None:
    assert cs.main([]) == 0


@pytest.mark.parametrize(
    "label, field",
    [
        ("**Environment & Lighting:**", "Environment & Lighting"),
        ("**Avatar (Wardrobe & Physicality):**", "Avatar (Wardrobe & Physicality)"),
        ("**Visual Overlay:**", "Visual Overlay"),
        ("**Vocal Direction:**", "Vocal Direction"),
    ],
)
def test_each_missing_field_is_named(label: str, field: str) -> None:
    text = "\n".join(line for line in GOOD.splitlines() if label not in line)
    assert f"missing {field}" in problems(text)


def test_an_empty_field_counts_as_missing() -> None:
    text = GOOD.replace("A card reads 'context rot' and code `print('hi')`.", "")
    assert "missing Visual Overlay" in problems(text)


def test_a_missing_spoken_line_is_named() -> None:
    text = "\n".join(line for line in GOOD.splitlines() if "Spoken Script" not in line and "fifty rules" not in line)
    assert "missing Spoken Script" in problems(text)


@pytest.mark.parametrize("quote", ['"context rot"', "“context rot”"])
def test_double_quotes_outside_the_spoken_line_are_flagged(quote: str) -> None:
    text = GOOD.replace("'context rot'", quote)
    assert any("double quotes in Visual Overlay" in p for p in problems(text))


def test_double_quotes_in_a_continuation_line_are_flagged() -> None:
    text = GOOD.replace("leans in.", 'leans in.\n  The shirt reads "AJ".')
    assert any("double quotes in Avatar" in p for p in problems(text))


def test_double_quotes_in_the_heading_are_flagged() -> None:
    text = GOOD.replace("): Hook", '): "Hook"')
    assert any("heading get voiced" in p for p in problems(text))


def test_a_second_quoted_span_is_flagged() -> None:
    text = GOOD.replace("It breaks one.", 'It breaks one." "Again.')
    assert any("exactly one double-quoted span" in p for p in problems(text))


def test_a_direction_inside_the_spoken_quotes_is_flagged() -> None:
    text = GOOD.replace("It breaks one.", "It breaks one. [pause]")
    assert any("[direction]" in p for p in problems(text))


def test_a_pointer_to_another_segment_is_flagged() -> None:
    text = GOOD.replace("A desk at night, warm lamp from the left.", "Same as Segment 1.")
    assert any("say it in full" in p for p in problems(text))


@pytest.mark.parametrize("span, ok", [("0:00 – 0:10", True), ("0:00 – 0:11", False), ("1:05 - 1:05", False)])
def test_a_clip_runs_one_to_ten_seconds(span: str, ok: bool) -> None:
    text = GOOD.replace("0:00 – 0:10", span)
    assert (not any("segment runs" in p for p in problems(text))) is ok


def test_a_heading_without_a_span_is_flagged() -> None:
    assert "heading has no (m:ss – m:ss) span" in problems(GOOD.replace(" (0:00 – 0:10)", ""))


@pytest.mark.parametrize("words, ok", [(25, True), (26, False)])
def test_a_spoken_line_over_ten_seconds_is_flagged(words: int, ok: bool) -> None:
    line = " ".join(["word"] * words)
    text = GOOD.replace("Say you give your agent fifty rules. It breaks one. Here's why.", line)
    assert (not any("spoken line needs" in p for p in problems(text))) is ok


def test_a_spoken_line_is_timed_against_a_shorter_clip() -> None:
    text = GOOD.replace("0:00 – 0:10", "0:00 – 0:03")
    assert any("the clip has 3 s" in p for p in problems(text))


def test_a_file_without_segments_fails() -> None:
    assert problems("# Just a title\n") == ["no '### Segment N (m:ss – m:ss)' headings found"]


def test_main_reports_a_failing_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "script.md"
    bad.write_text(GOOD.replace("'context rot'", '"context rot"'), encoding="utf-8")
    assert cs.main([str(bad)]) == 1
    assert f"{bad}:" in capsys.readouterr().err
