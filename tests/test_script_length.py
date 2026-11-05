"""Each capped talk's spoken script fits its cap, and the measure counts what it says it counts."""

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("talks_script_length", ROOT / "scripts" / "script_length.py")
assert _spec and _spec.loader
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)


def deck(talk: str, faq: str = "") -> str:
    return f'<section><h2>A</h2><aside class="notes">{talk}</aside></section><section id="faq"></section>{faq}'


@pytest.mark.parametrize("talk", sorted(sl.CAP_MINUTES))
def test_the_spoken_script_fits_its_cap(talk: str) -> None:
    """Runs what `make script-length` runs; its first line says how far over a failing talk is."""
    assert sl.main([talk]) == 0


def test_faq_notes_are_not_spoken() -> None:
    faq = '<section class="backup"><aside class="notes">one two three</aside></section>'
    assert sl.words(deck("Hello there.", faq)) == 2


def test_the_talk_also_ends_at_a_backup_slide_without_an_faq_index() -> None:
    html = '<section><aside class="notes">Spoken here.</aside></section>'
    html += '<section class="backup"><aside class="notes">Not spoken.</aside></section>'
    assert sl.words(html) == 2


def test_every_branch_counts_and_glued_branches_stay_separate_words() -> None:
    notes = '<span data-if="readings.x">It held.</span><span data-unless="readings.x">It failed.</span>'
    assert sl.words(deck(notes)) == 4
    assert sl.words(deck('<span data-if="a">It held.</span>Then we go')) == 5


def test_a_bound_figure_counts_as_one_word_whatever_its_text() -> None:
    notes = 'OpenStack reads <span data-value="readings.team_openstack"></span>; Wikimedia too.'
    assert sl.words(deck(notes)) == 5
    held = 'It reads <span data-value="readings.x">nought point <span>four</span> two</span> now.'
    assert sl.words(deck(held)) == 4
    assert sl.words(deck('a <b data-value="readings.x">four two</b> c')) == 3
    assert sl.words(deck('up <span data-value="readings.x"></span>% today')) == 3


def test_block_tags_end_a_word() -> None:
    assert sl.words(deck("<ul><li>One.</li><li>Two.</li></ul>first<br>second<p>third</p>")) == 5


def test_entities_and_tags_inside_a_word_do_not_split_it() -> None:
    assert sl.words(deck("It&#39;s <b>wo</b>rking &amp; fine")) == 4


def test_a_script_over_its_cap_fails(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "long-talk").mkdir()
    (tmp_path / "long-talk" / "index.html").write_text(deck("word " * 15), encoding="utf-8")
    monkeypatch.setattr(sl, "ROOT", tmp_path)
    monkeypatch.setattr(sl, "CAP_MINUTES", {"long-talk": 0.1})
    assert sl.main(["long-talk"]) == 1
    monkeypatch.setattr(sl, "CAP_MINUTES", {"long-talk": 0.2})
    assert sl.main(["long-talk"]) == 0


SCRIPT = """# A talk: the script

<!-- a comment {not.counted} is not spoken -->

## 1. Title

Hello there, {readings.n} people.

## 2. Point

{if readings.ok}It held.{/if}{unless readings.ok}It failed.{/unless} Done.
"""


def test_script_md_counts_spoken_words_each_figure_and_every_branch() -> None:
    # Hello there, FIGURE people. (4) + It held. It failed. Done. (5); headings and comments excluded.
    assert sl.script_words(SCRIPT) == 9


def test_script_md_sections_follow_the_headings() -> None:
    assert [h for h, _ in sl.sections(SCRIPT)] == ["1. Title", "2. Point"]


def test_talk_slides_stop_at_the_first_backup_slide() -> None:
    html = '<section><section></section></section><section class="closing"></section>'
    html += '<section class="backup divider"></section><section class="backup"></section>'
    assert sl.talk_slides(html) == 2
    assert sl.talk_slides('<section></section><section id="faq"></section><section></section>') == 1


def test_render_fills_figures_and_keeps_the_branch_that_holds() -> None:
    out = sl.render(SCRIPT, {"readings": {"n": 1200, "ok": False}})
    assert "Hello there, 1,200 people." in out
    assert "It failed." in out and "It held." not in out


def test_check_finds_a_section_count_off_the_slides_and_missing_data(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    talk = tmp_path / "a-talk"
    (talk / "data").mkdir(parents=True)
    (talk / "data" / "d.js").write_text("window.DECK_DATA = { readings: { n: 3 } };", encoding="utf-8")
    (talk / "index.html").write_text(
        '<script src="data/d.js"></script><section></section><section></section><section></section>', encoding="utf-8"
    )
    (talk / "script.md").write_text(SCRIPT, encoding="utf-8")
    monkeypatch.setattr(sl, "ROOT", tmp_path)
    if sl.shutil.which("node") is None:
        pytest.skip("needs node")
    found = sl.problems("a-talk")
    assert "a-talk/script.md has 2 sections for 3 talk slides" in found
    assert "a-talk/script.md: no data at readings.ok" in found


@pytest.mark.parametrize("talk", ["checking-the-checker", "claude-tooling", "federated-agents", "kourai-khryseai"])
def test_each_talk_has_a_script_that_matches_its_slides(talk: str) -> None:
    if sl.shutil.which("node") is None:
        pytest.skip("needs node")
    assert sl.problems(talk) == []
