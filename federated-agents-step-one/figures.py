#!/usr/bin/env python3
"""Every figure this deck shows that comes from the sphragis artifacts.

Writes `data/readings.js`, which the slides and `script.md` bind to; `--check` fails when the
committed copy no longer matches the artifacts. Venue facts live in `data/venue.js` with their
sources. Federated Agents' figures.py already reads the planted-convention runs and the study's
windows; this module loads those two helpers from it rather than repeating them.

    python figures.py            # write data/readings.js
    python figures.py --check    # is data/readings.js current?

SPHRAGIS points at a sphragis checkout; the default is a sibling of this repository.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SPHRAGIS = pathlib.Path(os.environ.get("SPHRAGIS") or HERE.parents[1] / "sphragis")
RESULTS = SPHRAGIS / "datasets" / "results"
READINGS = HERE / "data" / "readings.js"
#: The corpus itself is not in git; CI reuses the committed example (see `example`).
CORPUS = pathlib.Path(os.environ.get("SPHRAGIS_CORPUS") or SPHRAGIS / "datasets" / "gerrit")

#: The Gerrit organizations of the confirmatory design, in the order the slides name them.
ORGS = {"openstack": "OpenStack", "wikimedia": "Wikimedia", "qt": "Qt"}
#: H1 is read on the whole fix and on its non-name part (paper, Section III).
H1_SCORES = 2
#: The level both hypotheses are first read at (paper, Execution Plan, step 7).
LEVEL = "0.975"


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.is_file():
        raise SystemExit(f"missing artifact {path}; the deck's numbers come from sphragis")
    return json.loads(path.read_text())


def federated_agents():
    """Federated Agents' figures.py, for its planted-run and window helpers."""
    path = HERE.parent / "federated-agents" / "figures.py"
    spec = importlib.util.spec_from_file_location("fa_figures", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def comma(n: int) -> str:
    return f"{n:,}"


def points(value: float) -> str:
    """An exact-match difference in points: 0.0284 reads "+2.84"."""
    return f"{value * 100:+.2f}"


def corpus(values: dict) -> None:
    """Examples per window and organization, from each frozen v3 corpus's window report."""
    total = 0
    for org in ORGS:
        windows = load(f"window-report-{org}-v3.json")[org]["windows"]
        count = sum(w["examples"] for w in windows.values())
        total += count
        values[f"examples_{org}"] = comma(count)
    values["examples_total"] = comma(total)


def smallest_effect(values: dict) -> None:
    """delta and its reading as "each token about x percent more likely" (e^delta - 1)."""
    sesoi = load("likelihood-sesoi.json")
    if sesoi["rate_source"] != "planted":
        raise SystemExit("delta's rate is not the planted one the paper registers")
    values["delta"] = f"{sesoi['sesoi']:.4f}"
    values["delta_pct"] = f"{(math.exp(sesoi['sesoi']) - 1) * 100:.1f}"


def registered_design(values: dict, fa) -> None:
    """Training size and the number of confirmatory cells."""
    floors = {load(f"admissible-partitions-{org}.json")["size_floor"] for org in ORGS}
    if len(floors) != 1:
        raise SystemExit(f"the organizations' training sizes differ: {floors}")
    values["n"] = comma(floors.pop())
    values["h1_cells"] = len(ORGS) * H1_SCORES
    values["orgs_count"] = len(ORGS)
    for name, (start, end) in fa.windows().items():
        span = fa.month_span(start, end)
        first, _, last = span.partition(" to ")
        values[f"window_{name}"] = first if first == last else span
    model, rank, _ = fa.trained_setup()
    values["model"] = model.rsplit("/", 1)[-1]
    values["rank"] = rank


#: The sizing simulations the paper's Table I reads: each H1 cell on the whole fix and on its
#: non-name part, and H2's one cell, every one at its registered number of runs.
SIZING = {
    "openstack": ("cells6-logprob_per_token-chains-k10", "logprob_per_token-other-chains-k10"),
    "wikimedia": ("cells6-logprob_per_token-chains-k20", "logprob_per_token-other-chains-k20-calibrated"),
    "qt": ("cells6-logprob_per_token-chains-k10", "logprob_per_token-other-chains-k10"),
}
SIZING_H2 = "partition-sensitivity-qt-rp1.0-foreignchromium-logprob_per_token-chains-k40-calibrated.json"


def sizing(values: dict) -> None:
    """The smallest effect each confirmatory cell detects at the first Holm level, at the sizing
    bound of its run-to-run spread, and its number of runs; every one must lie below delta."""
    sesoi = load("likelihood-sesoi.json")["sesoi"]

    def detect(name: str, cells: str) -> tuple[float, int]:
        sim = load(name)
        bound = sim["by_target"]["sizing_bound_90"]
        return bound["by_level"][LEVEL]["by_cells"][cells]["minimum_detectable_effect"], sim["runs"]

    cells = str(len(ORGS) * H1_SCORES)
    found = []
    for org, (whole, other) in SIZING.items():
        mde, runs = detect(f"partition-sensitivity-{org}-rp1.0-{whole}.json", cells)
        mde_other, runs_other = detect(f"partition-sensitivity-{org}-rp1.0-{other}.json", cells)
        if runs != runs_other:
            raise SystemExit(f"{org}: the two scores' runs differ ({runs}, {runs_other})")
        values[f"k_{org}"] = runs
        values[f"mde_{org}"] = f"{mde:+.4f}"
        values[f"mde_{org}_other"] = f"{mde_other:+.4f}"
        found += [mde, mde_other]
    mde, runs = detect(SIZING_H2, "1")
    values["k_h2"] = runs
    values["mde_h2"] = f"{mde:+.4f}"
    found.append(mde)
    if max(found) >= sesoi:
        raise SystemExit("a cell cannot detect delta; the backup slide says every one can")


def split_example(values: dict, figure: dict) -> None:
    """The example on the "why plan first" slide: one split's first reading against five splits."""
    first = load("decomposition-pilot-openstack-v3.json")["per_org"]["H1"]["openstack"]
    if first["role"] != "confirmatory" or first["verdicts"]["0.95"] != "supported":
        raise SystemExit("the single split's first reading no longer passes")
    interval = first["intervals"]["0.95"]
    values["split_first"] = points(first["estimate"])
    figure["split_first_low"] = points(interval["low"])
    figure["split_first_high"] = points(interval["high"])
    runs = load("partition-variance-openstack-v3.json")["runs"]
    means = {name: sum(r["h1"] for r in rows) / len(rows) for name, rows in runs.items()}
    if len(means) != 5:
        raise SystemExit(f"expected five partitions, found {len(means)}")
    figure["split_means"] = {name: round(value * 100, 2) for name, value in means.items()}
    values["split_low"] = points(min(means.values()))
    values["split_high"] = points(max(means.values()))
    values["split_mean"] = points(sum(means.values()) / len(means))
    figure["split_count"] = len(means)


def planted(values: dict, fa) -> None:
    """Check 5: each organization's runs with a marker planted in half the training examples."""
    every: list[str] = []
    for org in ORGS:
        runs = fa.planted_runs(org)
        every.extend(runs)
        values[f"planted_runs_{org}"] = len(runs)
        values[f"planted_found_{org}"] = runs.count("pass")
    values["planted_total"] = len(every)
    values["planted_found"] = every.count("pass")


#: The one corpus example the "what Sphragis builds" slide shows: an OpenStack train-window hunk
#: that the human checker and both model raters labeled valid. Only its code is read; the
#: protocol publishes no review text, so its comments never leave the corpus.
EXAMPLE = (
    "openstack:I7584e060b9fe3a1d81f98be624eab6176b92354b:"
    "controllerconfig/controllerconfig/upgrade-scripts/200-cis-benchmark-support.sh:1:8"
)
#: SHA-256 of the example's [before, after, created day, project], so a run without the corpus
#: (CI) still checks the committed code against the corpus row it was drawn from.
EXAMPLE_DIGEST = "4c05d828aaa808d310fde1dd7f0ed7f2ef124a5484a2ada56ccacb8bf5ca9a3a"
#: Windows an example on a slide may come from: frozen and public, never the sealed test window.
SHOWABLE = ("train", "dev")
AUDIT = "label-audit-v2.json"
AUDIT_RATERS = ("human", "A", "B")


def marked(old: str, new: str) -> tuple[list, list]:
    """Each side as [text, changed] runs, so the slide can mark what the fix changed."""
    a: list = []
    b: list = []

    def add(runs: list, text: str, changed: bool) -> None:
        if runs and runs[-1][1] == changed:
            runs[-1][0] += text
        elif text:
            runs.append([text, changed])

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        add(a, old[i1:i2], tag != "equal")
        add(b, new[j1:j2], tag != "equal")
    return a, b


def committed_figure() -> dict:
    """DECK_FIGURE as committed, for the example when the corpus is not on this machine."""
    if not READINGS.is_file():
        return {}
    _, _, tail = READINGS.read_text().partition("window.DECK_FIGURE = ")
    return json.loads(tail.rstrip().removesuffix(";")) if tail else {}


def addresses() -> object:
    """sphragis's own test for a third-party email address, which its release redaction uses."""
    path = SPHRAGIS / "sphragis" / "corpus" / "redact.py"
    spec = importlib.util.spec_from_file_location("sphragis_redact", path)
    if spec is None or spec.loader is None or not path.is_file():
        raise SystemExit(f"missing {path}; the example's address check comes from sphragis")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.third_party_addresses


def example_digest(before: str, after: str, day: str, project: str) -> str:
    return hashlib.sha256(json.dumps([before, after, day, project]).encode()).hexdigest()


def example(values: dict, figure: dict, fa) -> None:
    """The slide's example: its code before and after review, where and when it was written, and
    its audit labels, which must all be valid since the slide says so. Only its code fields are
    read; its review comments never leave the corpus."""
    labels = load(AUDIT)["labels"].get(EXAMPLE)
    if not labels or any(labels.get(r, {}).get("label") != "valid" for r in AUDIT_RATERS):
        raise SystemExit(f"{EXAMPLE} is not labeled valid by {', '.join(AUDIT_RATERS)}")
    org = EXAMPLE.split(":", 1)[0]
    found = None
    for path in sorted((CORPUS / org / "examples").glob("*.jsonl")):
        with path.open() as rows:
            for line in rows:
                if EXAMPLE in line:
                    row = json.loads(line)
                    if row["id"] == EXAMPLE:
                        found = row
                        break
        if found:
            break
    if found is None:
        committed = committed_figure().get("example")
        if not committed or committed.get("id") != EXAMPLE:
            raise SystemExit(f"no corpus at {CORPUS} and no committed copy of {EXAMPLE}")
        missing = [k for k in ("before", "after", "day", "project") if k not in committed]
        if missing:
            raise SystemExit(f"the committed copy of {EXAMPLE} lacks {', '.join(missing)}; run with the corpus")
        print(f"no corpus at {CORPUS}; the example's code is the committed copy", file=sys.stderr)
        # Rebuilt from the committed text, so the digest covers everything the slide shows.
        row = {
            "before": "".join(text for text, _ in committed["before"]),
            "after": "".join(text for text, _ in committed["after"]),
            "created": committed["day"],
            "project": committed["project"],
        }
    else:
        row = found
    day = row["created"][:10]
    window = next((w for w, (start, end) in fa.windows().items() if start <= day < end), None)
    before, after = marked(row["before"], row["after"])
    drawn = {
        "id": EXAMPLE,
        "window": window,
        "day": day,
        "month": f"{dt.date.fromisoformat(day):%b %Y}",
        "project": row["project"],
        "before": before,
        "after": after,
    }
    if window not in SHOWABLE:
        raise SystemExit(f"{EXAMPLE} falls in the {window} window, not in {SHOWABLE}")
    if example_digest(row["before"], row["after"], day, row["project"]) != EXAMPLE_DIGEST:
        raise SystemExit(f"{EXAMPLE}: the example's code or date no longer matches EXAMPLE_DIGEST")
    found_addresses = addresses()("\n".join((row["before"], row["after"])))
    if found_addresses:
        raise SystemExit(f"{EXAMPLE}: its code holds {len(found_addresses)} email address(es)")
    figure["example"] = drawn
    values["example_org"] = ORGS[org]
    values["example_project"] = drawn["project"]
    values["example_month"] = drawn["month"]
    values["example_window"] = {"train": "training", "dev": "development"}[drawn["window"]]


def label_audit(values: dict) -> None:
    """How many of the examples a person checked each reader called valid."""
    audit = load(AUDIT)
    if "valid" not in audit["rubric"]:
        raise SystemExit(f"{AUDIT}: no 'valid' label in the rubric {audit['rubric']}")
    checked = [v for v in audit["labels"].values() if "human" in v]
    values["audit_checked"] = len(checked)
    for rater in AUDIT_RATERS:
        values[f"audit_valid_{rater.lower()}"] = sum(v[rater]["label"] == "valid" for v in checked)


def readings() -> tuple[dict, dict]:
    fa = federated_agents()
    values: dict = {}
    figure: dict = {}
    corpus(values)
    smallest_effect(values)
    registered_design(values, fa)
    sizing(values)
    split_example(values, figure)
    planted(values, fa)
    example(values, figure, fa)
    label_audit(values)
    return values, figure


def render(values: dict, figure: dict) -> str:
    body = json.dumps(values, indent=2, ensure_ascii=False)
    drawn = json.dumps(figure, indent=2)
    return (
        "// GENERATED by figures.py from the sphragis artifacts. Do not edit.\n"
        f"window.DECK_DATA = Object.assign(window.DECK_DATA || {{}}, {{ readings: {body} }});\n"
        f"window.DECK_FIGURE = {drawn};\n"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if data/readings.js is stale")
    args = ap.parse_args(argv)
    text = render(*readings())
    if args.check:
        if not READINGS.is_file() or READINGS.read_text() != text:
            print(f"{READINGS} is stale; run figures.py", file=sys.stderr)
            return 1
        print(f"{READINGS.name} is current")
        return 0
    READINGS.parent.mkdir(exist_ok=True)
    READINGS.write_text(text)
    print(f"wrote {READINGS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
