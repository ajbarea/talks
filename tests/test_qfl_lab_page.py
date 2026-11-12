"""The lab page (qfl-privacy/lab/): its frozen paper runs agree with the deck, and its copies agree.

The page draws and counts `lab/data/runs.js`, which figures.py writes from results/. These tests
count those rows the way the page does and compare with the values the deck shows
(data/readings.js), so the page and the slides cannot tell two stories.
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TALK = ROOT / "qfl-privacy"
LAB = TALK / "lab"


def bundle(path: pathlib.Path, name: str) -> dict:
    text = path.read_text()
    m = re.search(rf"window\.{name} = (\{{.*\}});\s*$", text, re.S)
    assert m, f"{path.name} does not set window.{name}"
    return json.loads(m.group(1))


RUNS = bundle(LAB / "data" / "runs.js", "PAPER_RUNS")
DECK = bundle(TALK / "data" / "readings.js", "DECK_DATA")
ROWS = [dict(zip(RUNS["columns"], r, strict=True)) for r in RUNS["rows"]]


def rows(**where) -> list[dict]:
    return [r for r in ROWS if all(r[k] == v for k, v in where.items())]


def test_every_attack_row_is_in_the_bundle_once() -> None:
    sizes = {e["id"]: len(rows(exp=e["id"])) for e in RUNS["experiments"]}
    assert sizes == {"rq1": 400, "budget": 80, "rq2": 600, "rq3": 240, "rq4": 320, "rq5": 720}
    who = ("exp", "qubits", "reps", "layers", "seed", "shots", "batch", "label", "task", "step")
    keys = {tuple(r[k] for k in who) for r in ROWS}
    assert len(keys) == len(ROWS)
    assert all(len(r["outcomes"]) == r["restarts"] and set(r["outcomes"]) <= set("rcas") for r in ROWS)


def test_the_bundles_thresholds_are_the_decks() -> None:
    assert RUNS["thresholds"]["recovered"] == float(DECK["paper"]["recoveredRad"])
    assert RUNS["thresholds"]["close"] == float(DECK["paper"]["closeRad"])


def test_the_repetitions_rows_match_the_deck() -> None:
    # The page's figure: 8 qubits, reps x layers = 8 blocks on every line.
    line: dict[tuple[int, int], list[dict]] = {}
    for r in rows(exp="rq1", qubits=8):
        if r["reps"] * r["layers"] == 8:
            line.setdefault((r["reps"], r["layers"]), []).append(r)
    rec = {k: sum(x["best"] == "recovered" for x in v) for k, v in line.items()}
    hits = {k: sum(x["outcomes"].count("r") for x in v) for k, v in line.items()}
    assert rec[(1, 8)] == DECK["rq1"]["rec1"] and rec[(8, 1)] == DECK["rq1"]["rec8"]
    assert hits[(1, 8)] == DECK["rq1"]["hits1"] and hits[(8, 1)] == DECK["rq1"]["hits8"]
    assert all(len(v) == DECK["paper"]["seeds"] for v in line.values())


def test_the_restarts_rows_match_the_deck() -> None:
    by = {}
    for r in rows(exp="budget"):
        by.setdefault(f"{r['reps']}×{r['layers']}", []).append(r)
    small = {k: sum(x["bestSmall"] == "recovered" for x in v) for k, v in by.items()}
    large = {k: sum(x["best"] == "recovered" for x in v) for k, v in by.items()}
    hardest = DECK["budget"]["hardest"]
    assert DECK["paper"]["seeds"] - large[hardest] == DECK["budget"]["hardestHeld"]
    others = [large[k] for k in by if k != hardest]
    assert min(others) == DECK["budget"]["othersMin"] and max(others) == DECK["budget"]["othersMax"]
    assert all(small[k] <= large[k] for k in by)


def test_the_shots_rows_match_the_deck() -> None:
    low = DECK["rq2"]["lowShots"]

    def within(q: int) -> list[int]:
        out = {}
        for r in rows(exp="rq2", qubits=q, shots=low):
            out.setdefault((r["reps"], r["layers"]), 0)
            out[(r["reps"], r["layers"])] += r["best"] in ("recovered", "close")
        return list(out.values())

    assert max(within(8)) == DECK["rq2"]["within8Max"]
    assert (min(within(4)), max(within(4))) == (DECK["rq2"]["within4Min"], DECK["rq2"]["within4Max"])


def test_the_federated_learning_picture_is_the_decks() -> None:
    def texts(html: str) -> list[str]:
        return re.findall(r"<text[^>]*>([^<]*)</text>", html)

    deck_html = (TALK / "index.html").read_text()
    deck = re.search(r'<svg data-only="desktop" viewBox="0 0 1180 452".*?</svg>', deck_html, re.S)
    page = re.search(r'<svg class="fl" viewBox="0 0 1180 452".*?</svg>', (LAB / "index.html").read_text(), re.S)
    assert deck and page
    assert texts(deck.group(0)) == texts(page.group(0))
    shapes = lambda h: re.findall(r'<(?:rect|path)[^>]*\b(?:d|x)="[^"]*"', h)  # noqa: E731
    assert shapes(deck.group(0)) == shapes(page.group(0))


def test_the_page_opens_on_input_1_and_picks_no_seed() -> None:
    src = (LAB / "app.js").read_text()
    assert re.search(r"const DEF = \{[^}]*\binput: 1\b", src)
    assert not re.search(r"\bseed:\s*\d", src)


def test_the_worker_runs_the_decks_simulator() -> None:
    assert 'importScripts("../lab-sim.js")' in (LAB / "worker.js").read_text()
    page = (LAB / "index.html").read_text()
    order = ['src="../lab-sim.js"', 'src="data/runs.js"', 'src="jobs.js"', 'src="app.js"']
    assert [page.index(s) for s in order] == sorted(page.index(s) for s in order)


def test_each_lab_slide_frames_a_real_tab_and_keeps_the_paper_figure() -> None:
    deck = (TALK / "index.html").read_text()
    tabs = set(re.findall(r'\["(\w+)", "[^"]+"\]', (LAB / "app.js").read_text()))
    frames = re.findall(r'<iframe class="lab-frame" data-lab-src="lab/index\.html#([^"]+)"', deck)
    assert len(frames) == 3
    for frag in frames:
        q = dict(kv.split("=") for kv in frag.replace("&amp;", "&").split("&"))
        assert q["tab"] in tabs and q["embed"] == "1"
    # Only lab-embed.js loads a frame (not Reveal, which lazy-loads any data-src near the slide).
    assert not re.search(r'<iframe[^>]*\ssrc="lab/', deck)
    assert deck.count("<!-- fig:") >= len(frames)
    assert "lab.js" not in re.findall(r'<script src="([^"]+)"', deck)


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_only_the_decks_own_frames_steer_it() -> None:
    out = subprocess.run(
        ["node", str(ROOT / "tests" / "qfl_embed_harness.js"), str(TALK / "lab-embed.js")],
        capture_output=True,
        text=True,
        check=True,
    )
    got = json.loads(out.stdout)
    # Wrong origin, a stranger window, another tag, a prototype key and an absurd height do nothing.
    assert {k: got[k] for k in ("calls", "tooTall", "height")} == {"calls": ["next"], "tooTall": "", "height": "513px"}
    # Forwarded keys move the deck as Reveal's own keyboard does (up, down, left, right, space):
    # a flat deck steps in order, Shift jumps to an end, a deck with stacks moves in two axes.
    assert got["flat"] == ["prev", "next", "prev", "next", "next"]
    bottom = "slide undefined 1.7976931348623157e+308"
    assert got["flatShift"] == ["slide undefined 0", bottom, "slide 0 undefined", "slide 11 undefined", "prev"]
    assert got["stacked"] == ["up", "down", "left", "right", "next"]


def test_the_embed_reuses_the_decks_phone_tests() -> None:
    deck = (ROOT / "shared" / "deck.js").read_text()
    embed = (TALK / "lab-embed.js").read_text()
    for query in re.findall(r'matchMedia\("([^"]+)"\)', embed):
        assert f'matchMedia("{query}")' in deck


def test_each_still_link_opens_its_own_slides_tab() -> None:
    deck = (TALK / "index.html").read_text()
    # The still shows in the exported PDF too, so its link is the live address, not a file path.
    live = re.escape("https://ajbarea.github.io/talks/qfl-privacy/lab/#")
    still = rf'data-lab-src="lab/index\.html#([^"]+)".*?<p class="lab-link">.*?href="{live}([^"]+)"'
    pairs = re.findall(still, deck, re.S)
    assert len(pairs) == 3
    for frame, link in pairs:
        assert frame.replace("&amp;embed=1", "") == link


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_the_many_draw_jobs_cancel_resume_and_rerun() -> None:
    out = subprocess.run(
        ["node", str(ROOT / "tests" / "qfl_jobs_harness.js"), str(LAB)],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    got = json.loads(out.stdout)
    full = {"seeds": [1, 2, 3, 4, 5, 6], "done": 1, "right": True, "current": False}
    # A newer job cancels the last: the Worker hears the cancel first, the old job never ends.
    assert got["supersede"]["log"][:3] == ["job 1", "cancel 1", "job 2"]
    assert got["supersede"]["a"]["done"] == 0 and got["supersede"]["b"] == full
    mid = got["midway"]
    assert mid["a"]["seeds"] == [1, 2] and mid["a"]["done"] == 0 and mid["b"] == full
    # The Worker itself stops the cancelled job: at most the input already under way.
    assert mid["stale"] <= 1
    alone = got["alone"]
    assert alone["a"]["seeds"] == [1, 2] and alone["a"]["done"] == 0 and alone["stale"] <= 1
    assert got["aloneThread"] == {"seeds": [1, 2], "done": 0, "right": True, "current": False}
    # A cancelled job stays cancelled when its Worker then fails (twice): nothing resumes it.
    fac = got["failAfterCancel"]
    assert fac["a"]["seeds"] == [1, 2] and fac["a"]["done"] == 0 and fac["terminated"]
    # A Worker that fails mid-job is let go; the job ends here, every input once, scored alike.
    assert got["failure"] == {**full, "terminated": True, "inWorker": False}
    assert got["thread"] == {**full, "inWorker": False}
    assert got["shouldRun"] == [False, True, True]


def _bodies(src: str, start: str) -> list[str]:
    """The brace-balanced body after each match of `start` (a handler's opening)."""
    out = []
    for m in re.finditer(start, src):
        i = src.index("{", m.end() - 1)
        depth = 0
        for j in range(i, len(src)):
            depth += {"{": 1, "}": -1}.get(src[j], 0)
            if depth == 0:
                out.append(src[i : j + 1])
                break
    return out


def test_every_key_handler_leaves_browser_shortcuts_alone() -> None:
    # A handler that takes a key (preventDefault) must leave Ctrl, Meta and Alt keys to the
    # browser (Alt+Left and Cmd+Left are Back, Ctrl+P prints), or say how it treats them.
    src = (LAB / "app.js").read_text()
    starts = [r'addEventListener\("keydown", \(\w+\) => \{', r"function onKey\(\w+\) \{"]
    bodies = [b for st in starts for b in _bodies(src, st)]
    taking = [b for b in bodies if "preventDefault" in b]
    assert len(taking) == 4  # the player, the runs grid, the tabs bar, the embed's forwarder
    # A handler written in another shape would escape the search: every preventDefault is in one.
    assert sum(b.count("preventDefault") for b in taking) == src.count("preventDefault")
    for b in taking:
        assert all(k in b for k in ("ctrlKey", "metaKey", "altKey")), b[:120]
        assert b.index("altKey") < b.index("preventDefault"), b[:120]
