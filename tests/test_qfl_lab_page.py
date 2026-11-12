"""The lab page (qfl-privacy/lab/): its frozen paper runs agree with the deck, and its copies agree.

The page draws and counts `lab/data/runs.js`, which figures.py writes from results/. These tests
count those rows the way the page does and compare with the values the deck shows
(data/readings.js), so the page and the slides cannot tell two stories.
"""

from __future__ import annotations

import json
import pathlib
import re

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
    small = {k: sum(x["best10"] == "recovered" for x in v) for k, v in by.items()}
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
    assert page.index('src="../lab-sim.js"') < page.index('src="data/runs.js"') < page.index('src="app.js"')


def test_each_lab_slide_frames_a_real_tab_and_keeps_the_paper_figure() -> None:
    deck = (TALK / "index.html").read_text()
    tabs = set(re.findall(r'\["(\w+)", "[^"]+"\]', (LAB / "app.js").read_text()))
    frames = re.findall(r'<iframe class="lab-frame web-only" data-src="lab/index\.html#([^"]+)"', deck)
    assert len(frames) == 3
    for frag in frames:
        q = dict(kv.split("=") for kv in frag.replace("&amp;", "&").split("&"))
        assert q["tab"] in tabs and q["embed"] == "1"
    # The frame loads only on its slide (data-src), so print and file:// show the paper's figure.
    assert not re.search(r'<iframe[^>]*\ssrc="lab/', deck)
    assert deck.count("<!-- fig:") >= len(frames)
    assert "lab.js" not in re.findall(r'<script src="([^"]+)"', deck)


def test_only_the_decks_own_frames_steer_it() -> None:
    src = (TALK / "lab-embed.js").read_text()
    assert "x.contentWindow === e.source" in src
    assert 'd.source !== "qfl-lab"' in src
    assert "Object.hasOwn(KEYS, d.key)" in src
