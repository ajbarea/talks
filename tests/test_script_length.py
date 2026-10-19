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
    n = sl.words((ROOT / talk / "index.html").read_text(encoding="utf-8"))
    cap = sl.CAP_MINUTES[talk]
    assert sl.minutes(n) <= cap, f"{talk}: {n} words is {sl.minutes(n):.2f} minutes, over the {cap}-minute cap"


def test_faq_notes_are_not_spoken() -> None:
    faq = '<section class="backup"><aside class="notes">one two three</aside></section>'
    assert sl.words(deck("Hello there.", faq)) == 2


def test_every_branch_counts_and_glued_branches_stay_separate_words() -> None:
    notes = '<span data-if="readings.x">It held.</span><span data-unless="readings.x">It failed.</span>'
    assert sl.words(deck(notes)) == 4


def test_a_bound_figure_counts_as_one_word() -> None:
    notes = 'OpenStack reads <span data-value="readings.team_openstack"></span>; Wikimedia too.'
    assert sl.words(deck(notes)) == 5


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
