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
