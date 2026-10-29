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


@pytest.mark.parametrize("pointer", ["Same as Segment 1.", "Back to the Segment 2 desk.", "As in segment S1."])
def test_a_pointer_to_another_segment_is_flagged(pointer: str) -> None:
    text = GOOD.replace("A desk at night, warm lamp from the left.", pointer)
    assert any("say it in full" in p for p in problems(text))


@pytest.mark.parametrize("span, ok", [("0:00 – 0:10", True), ("0:00 – 0:11", False), ("1:05 - 1:05", False)])
def test_a_clip_runs_one_to_ten_seconds(span: str, ok: bool) -> None:
    text = GOOD.replace("0:00 – 0:10", span)
    assert (not any("segment runs" in p for p in problems(text))) is ok


def test_a_heading_without_a_span_is_flagged() -> None:
    assert "heading has no (m:ss – m:ss) span" in problems(GOOD.replace(" (0:00 – 0:10)", ""))


@pytest.mark.parametrize("words, ok", [(22, True), (23, False)])
def test_a_spoken_line_must_leave_a_second_spare(words: int, ok: bool) -> None:
    line = " ".join(["word"] * words)
    text = GOOD.replace("Say you give your agent fifty rules. It breaks one. Here's why.", line)
    assert (not any("spoken line needs" in p for p in problems(text))) is ok


def test_a_spoken_line_is_timed_against_a_shorter_clip() -> None:
    text = GOOD.replace("0:00 – 0:10", "0:00 – 0:03")
    assert any("it has 2 s" in p for p in problems(text))


def test_a_file_without_segments_fails() -> None:
    assert problems("# Just a title\n") == ["no '### Segment N (m:ss – m:ss)' headings found"]


def test_main_reports_a_failing_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "script.md"
    bad.write_text(GOOD.replace("'context rot'", '"context rot"'), encoding="utf-8")
    assert cs.main([str(bad)]) == 1
    assert f"{bad}:" in capsys.readouterr().err


def test_a_number_takes_a_word_per_two_digits() -> None:
    assert cs.spoken_seconds("2025") == cs.spoken_seconds("twenty twenty-five")
    assert cs.spoken_seconds("In 2025") == 3 * 60 / cs.WORDS_PER_MINUTE


@pytest.mark.parametrize("heading", ["### Segmnet 2 (0:10 – 0:20): Typo", "**Segment 2 (0:10 – 0:20): Bold**"])
def test_a_heading_that_does_not_parse_is_flagged(heading: str) -> None:
    text = GOOD + "\n" + heading + '\n\n* **Visual Overlay:** A "quoted" card.\n'
    assert any("looks like a segment heading" in p for p in problems(text))


def second(span: str) -> str:
    seg = GOOD.split("### ", 1)[1].split("---", 1)[0].replace("Segment 1 (0:00 – 0:10)", f"Segment 2 ({span})")
    return seg.replace("At 0:04", "At " + span.split(" – ")[0])


@pytest.mark.parametrize("span, ok", [("0:10 – 0:20", True), ("0:12 – 0:20", False), ("0:08 – 0:18", False)])
def test_segments_in_a_cut_run_back_to_back(span: str, ok: bool) -> None:
    text = GOOD.replace("---", "---\n\n### " + second(span) + "\n---", 1)
    assert (not any("the one before ends" in p for p in problems(text))) is ok


def test_a_new_cut_may_start_again_at_zero() -> None:
    text = GOOD.replace("---", "---\n\n### " + second("0:00 – 0:10").replace("Segment 2", "Segment S1") + "\n---", 1)
    assert problems(text) == []


@pytest.mark.parametrize("at, ok", [("At 0:10", True), ("At 0:11", False), ("at 0:12", False), ("At 3:00 PM", True)])
def test_a_gesture_time_falls_inside_its_segment(at: str, ok: bool) -> None:
    text = GOOD.replace("At 0:04", at)
    assert (not any("falls outside this segment" in p for p in problems(text))) is ok


@pytest.mark.parametrize(
    "form",
    [
        "* **Environment & Lighting**: A desk at night.",
        "* Environment & Lighting: A desk at night.",
        "- Environment: A desk.",
    ],
)
def test_every_label_form_is_read(form: str) -> None:
    text = GOOD.replace("* **Environment & Lighting:** A desk at night, warm lamp from the left.", form)
    assert problems(text) == []


def test_a_bullet_starting_with_a_time_is_not_a_field() -> None:
    text = GOOD.replace("At 0:04, leans in.", "Leans back.\n* At 0:04: leans in.")
    assert problems(text) == []


def test_double_quotes_before_the_first_field_are_flagged() -> None:
    text = GOOD.replace("\n\n* **Environment", '\n\nThe card says "hi".\n* **Environment', 1)
    assert any("outside the spoken line" in p for p in problems(text))


def test_scene_headings_count_as_segments() -> None:
    assert problems(GOOD.replace("### Segment 1", "### Scene 1")) == []


def test_curly_quotes_around_the_spoken_line_pass() -> None:
    text = GOOD.replace('"Say you give', "“Say you give").replace("Here's why.\"", "Here's why.”")
    assert problems(text) == []


def test_a_heading_ends_a_segment() -> None:
    text = GOOD.replace("---\n\n## Audio Prompt", "## Audio Prompt")
    assert problems(text) == []


def test_main_fails_with_no_scripts(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cs, "HERE", tmp_path)
    assert cs.main([]) == 1


def test_main_fails_on_a_missing_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cs.main([str(tmp_path / "nope.md")]) == 1
    assert "no such file" in capsys.readouterr().err
