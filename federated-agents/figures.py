#!/usr/bin/env python3
"""Every figure the Federated Agents deck shows, derived from the sphragis artifacts.

No figure on a slide is typed by hand. This module reads the artifacts and writes
`data/readings.js`, which the slides bind to; `--check` fails when the committed copy no longer
matches what the artifacts say. The PDF deck in ajbarea/papers imports `readings()` from here,
so the two decks cannot disagree.

    python figures.py            # write data/readings.js
    python figures.py --check    # is data/readings.js current?

SPHRAGIS points at a sphragis checkout; the default is a sibling of this repository.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SPHRAGIS = pathlib.Path(os.environ.get("SPHRAGIS") or HERE.parents[1] / "sphragis")
RESULTS = SPHRAGIS / "datasets" / "results"
READINGS = HERE / "data" / "readings.js"


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.is_file():
        raise SystemExit(f"missing artifact {path}; the deck's numbers come from sphragis")
    return json.loads(path.read_text())


def interval(entry: dict) -> str:
    return f"{entry['estimate']:+.3f} [{entry['low']:+.3f}, {entry['high']:+.3f}]"


#: The rule the study registered: pooled estimand, crossed interval, three seeds. Every figure
#: the deck shows is read from this cell and no other, because a deck that quotes one rule while
#: the report quotes another is worse than a deck with no numbers.
REGISTERED = ("pooled", "crossed")


#: The suffix sphragis gives artifacts decoded at the registered repetition penalty, 1.0.
DECODER = "-rp1.0"

#: H1's registered score: the reference's mean log-probability per token (sphragis
#: `cells.REGISTERED_METRIC`, research log 2026-10-09). Exact match is its secondary.
METRIC = "logprob_per_token"

#: The share of each half's training lessons check 5 plants its marker in (sphragis
#: `neutral.PLANT_FRACTION`).
PLANT = "0.5"

#: How a development pilot's reading of the team-specific contrast reads aloud, from its verdict
#: at the stricter Holm level (sphragis `decomposition.cell_verdict`) and whether its interval
#: sits inside the SESOI band: (predicate after "OpenStack's assistant", the title's phrase for
#: one community, the title's phrase when every community reads alike). A state not listed fails
#: the build rather than reading as some other one.
TEAM_READING = {
    ("supported", False): ("is better on its own code", "a team-specific gain", "team-specific gains in both"),
    ("supported", True): (
        "is better on its own code, by less than matters",
        "a small team gain",
        "small team-specific gains",
    ),
    ("inconclusive", True): ("shows no gain that matters", "none that matters", "team-specific gains are small"),
    ("inconclusive", False): ("is not settled yet", "no answer yet", "team-specific gains are open"),
    ("bounded", True): ("shows no gain as large as the test can find", "none found", "no team-specific gain"),
    ("bounded", False): ("shows no gain as large as the test can find", "none found", "no team-specific gain"),
}

#: The communities on the slides, in the order they are named.
ORGS = {"openstack": "OpenStack", "wikimedia": "Wikimedia"}


def team_reading(pilot: dict) -> tuple[str, str, str]:
    """One community's development reading of H1 on the registered score, in words."""
    if pilot.get("metric") != METRIC:
        raise SystemExit(f"the pilot is on {pilot.get('metric')}, not {METRIC}")
    level = "0.975"
    key = (pilot["verdicts"][level], pilot["within_sesoi"][level])
    if key not in TEAM_READING:
        raise SystemExit(f"no wording for a pilot reading {key}; add one to TEAM_READING")
    return TEAM_READING[key]


def team_title(readings: dict[str, tuple[str, str, str]]) -> str:
    """The findings slide's headline: one phrase when every community reads alike, else each by name."""
    if len(set(readings.values())) == 1:
        return next(iter(readings.values()))[2]
    return ", ".join(f"{phrase} on {ORGS[org]}" for org, (_, phrase, _) in readings.items())


def planted_runs(org: str) -> list[str]:
    """Check 5's planted runs on the registered score, one per partition, each read as a verdict.

    Mirrors sphragis's `neutral.planted_convention`, which the deck cannot import without
    sphragis's dependencies: the organization's two halves, each planted at `PLANT` under its own
    partition root, trained at the admissible size, read on the development window, scored on
    `METRIC`, and adapter arms that are not degenerate on exact match (test 6). A run failing any
    of these is not a check-5 run and fails the build.
    """
    size = load(f"admissible-partitions-{org}.json")["size_floor"]
    verdicts: dict[int, str] = {}
    for path in sorted(RESULTS.glob(f"likelihood-partition-{org}-*-plant{PLANT}{DECODER}.json")):
        run = json.loads(path.read_text())
        sources = [c["source"] for c in run["corpora"].values()]
        if (
            set(run["corpora"]) != {f"{org}-a", f"{org}-b"}
            or run.get("metric") != METRIC
            or run.get("train_size") != size
            # sphragis `neutral.source_windows`: the windows a corpus source names.
            or not all(f"-plant{PLANT}/" in s and s.split(" windows")[0] == "train -> dev" for s in sources)
        ):
            raise SystemExit(f"{path.name} is not a check-5 run on {METRIC}")
        adapters = {arm: rows for arm, rows in run["results"].items() if arm.startswith("adapter:")}
        rates = [sum(float(r["exact_match"]) for r in rows) / len(rows) if rows else 0.0 for rows in adapters.values()]
        if not rates or not all(0.0 < rate < 1.0 for rate in rates):
            raise SystemExit(f"{path.name} has degenerate adapter arms (test 6)")
        # The partition is the corpus root's `-p<seed>`, one for both halves.
        roots = [re.search(rf"/corpus-partition-{org}-p(\d+)", s) for s in sources]
        if not all(roots):
            raise SystemExit(f"{path.name} has a half outside {org}'s partition corpora")
        partition = {m.group(1) for m in roots}
        if len(partition) != 1 or (seed := int(partition.pop())) in verdicts:
            raise SystemExit(f"{path.name} is not one new partition")
        verdicts[seed] = run["verdict"]["verdict"]
    if not verdicts:
        raise SystemExit(f"no planted runs for {org} in {RESULTS}")
    return list(verdicts.values())


#: Dots on the sizing panel, one per simulated study with a real effect.
SIZED_STUDIES = 20


def same_calibration(a: dict, b: dict) -> bool:
    """Spread targets at the same points and values, within sphragis `cells.same_calibration`'s
    relative 1e-9 (the chi-squared bounds' last bits differ across machines)."""
    return set(a) == set(b) and all(math.isclose(a[k], b[k], rel_tol=1e-9) for k in a)


def sized_simulation(org: str) -> dict:
    """The H1 simulation at the K a test read takes (sphragis `k-coverage-<org>-likelihood.json`).

    The panel says a real effect of the smallest size that matters is found at the registered
    power, which holds only if every effect the simulation detects at that power, at the spread
    K was sized on, is below the SESOI.
    """
    k = load(f"k-coverage-{org}-likelihood.json")
    if k.get("metric") != METRIC:
        raise SystemExit(f"{org}'s K source is on {k.get('metric')}, not {METRIC}")
    matches = [
        sim
        for path in sorted(RESULTS.glob(f"partition-sensitivity-{org}{DECODER}-{METRIC}*.json"))
        # A simulation written before the null-only mode existed carries no flag and is full.
        if not (sim := json.loads(path.read_text())).get("null_only", False)
        and sim.get("metric") == METRIC
        and sim["runs"] == k["runs"]
        and sim["null_trials"] == k["null_trials"]
        and same_calibration(sim["spread_targets"], k["spread_targets"])
    ]
    if len(matches) != 1:
        raise SystemExit(f"{len(matches)} full simulations for {org} at K = {k['runs']}; need one")
    sim = matches[0]
    # The registered SESOI, not the one the simulation carries about itself.
    sesoi = load("likelihood-sesoi.json")["sesoi"]
    if not math.isclose(sim["sesoi"], sesoi, rel_tol=1e-9):
        raise SystemExit(f"{org}'s simulation was sized at SESOI {sim['sesoi']}, not {sesoi}")
    bound = sim["by_target"][k["spread_target"]]["by_level"]
    effects = [c["minimum_detectable_effect"] for lv in bound.values() for c in lv["by_cells"].values()]
    if max(effects) >= sesoi:
        raise SystemExit(f"{org} detects {max(effects):.4f} at K = {k['runs']}, not below the SESOI")
    return sim


def registered(name: str) -> dict:
    return load(name)["readings"][REGISTERED[0]][REGISTERED[1]]["per_org"]


def readings() -> dict[str, str | int | bool]:
    """Every figure and flag the deck shows, by the name a slide binds it to."""
    values: dict[str, str | int | bool] = {}
    dev = load("rq1-qtfull-fp32-seeds.json")["readings"]["pooled"]["crossed"]
    windows = {org: load(f"window-report-{org}.json")[org] for org in ("openstack", "qt")}
    values["verdict"] = dev["verdict"]
    for org in ("qt", "openstack"):
        values[f"dev_{org}"] = interval(dev["per_org"][org])
    # The placebo and the capacity check, on the same registered cell as the gate above.
    for org in ("qt", "openstack"):
        placebo = registered(f"rq1-placebo-{org}-seeds.json")
        values[f"placebo_{org}"] = interval(placebo[f"{org}-a"])
    for org in ("qt", "openstack"):
        values[f"r256_{org}"] = interval(registered("rq1-r256-seeds.json")[org])
    for org in ("qt", "openstack"):
        w = windows[org]["windows"]
        values[f"train_{org}"] = w["train"]["examples"]
        values[f"dev_examples_{org}"] = w["dev"]["examples"]
        top = max(w["train"]["content"].items(), key=lambda kv: kv[1])
        share = round(100 * top[1] / w["train"]["examples"])
        values[f"language_{org}"] = f"{top[0]} {share}%"
    # The corpora as the study loads them (deduplicated, split into windows), every window but
    # the sealed test one, and the label audit's scored sample.
    built = load("ai-trailers.json")["orgs"]
    for org in ("openstack", "wikimedia"):
        corpus = built[org]["windows"].values()
        values[f"corpus_examples_{org}"] = f"{sum(w['examples'] for w in corpus):,}"
        values[f"corpus_changes_{org}"] = f"{sum(w['changes'] for w in corpus):,}"
    values["audit_items"] = f"{load('label-audit-v2.json')['items']:,}"
    # How far OpenStack's development pilot moves when read without its AI-assisted examples.
    # The pilot and both comparators are read at the registered decoder, repetition penalty 1.0
    # (sphragis research log, 2026-10-08); the earlier artifacts decoded at the checkpoint's 1.1.
    pilot = load(f"partition-pilot-openstack-sensitivities{DECODER}.json")
    values["ai_shift_openstack"] = f"{pilot['without']['ai_assisted']['estimate'] - pilot['estimate']:+.4f}"
    # The retrieval comparator on the development window: own half's pool minus sibling's, at
    # k = 1 and 3, the adapters over the same partitions, and the sibling-minus-foreign contrast.
    for org in ("openstack", "wikimedia"):
        read = load(f"retrieval-reading-{org}{DECODER}.json")
        for k in ("1", "3"):
            cell = read["ks"][k]
            values[f"retrieval_k{k}_{org}"] = interval(cell["own_minus_sibling"])
            values[f"retrieval_org_k{k}_{org}"] = interval(cell["sibling_minus_foreign"])
        values[f"retrieval_adapters_{org}"] = interval(read["adapters"]["own_minus_sibling"])
        values[f"retrieval_partitions_{org}"] = len(read["partitions"])
    # The rules-file comparator on the same partitions: the distilled file's own half minus
    # sibling, and the adapters' over the same partitions and examples.
    for org in ("openstack", "wikimedia"):
        read = load(f"rules-reading-{org}{DECODER}.json")
        values[f"rules_distilled_{org}"] = interval(read["families"]["distilled"]["own_minus_sibling"])
        values[f"rules_adapters_{org}"] = interval(read["adapters"]["own_minus_sibling"])
        values[f"rules_partitions_{org}"] = len(read["partitions"])
    # The team-specific contrast on the registered score, each community's development pilot.
    team = {}
    for org in ORGS:
        pilot = load(f"partition-pilot-{org}-likelihood.json")
        team[org] = team_reading(pilot)
        values[f"team_{org}"] = team[org][0]
        values[f"team_gain_{org}"] = pilot["verdicts"]["0.975"] == "supported"
    values["team_title"] = team_title(team)
    # Check 5: each half's own marker planted in half its training lessons; how many runs found it.
    planted = {org: planted_runs(org) for org in ("openstack", "wikimedia")}
    if len({len(v) for v in planted.values()}) != 1:
        raise SystemExit(f"planted runs differ in number: { {o: len(v) for o, v in planted.items()} }")
    every = [v for runs in planted.values() for v in runs]
    values["planted_runs"] = len(every)
    values["planted_found"] = every.count("pass")
    values["planted_all"] = values["planted_found"] == values["planted_runs"]
    # Each community's K from the coverage rule a test read takes it from, beside the
    # reproducibility K it would have had: the coverage rule raised it where they differ.
    for org in ORGS:
        k = load(f"k-coverage-{org}-likelihood.json")
        values[f"k_{org}"] = k["runs"]
        values[f"k_reproducibility_{org}"] = k["reproducibility_runs"]
        values[f"k_raised_{org}"] = k["runs"] > k["reproducibility_runs"]
    # The sizing panel: studies out of SIZED_STUDIES that find an effect at the registered power.
    power = {sized_simulation(org)["hypothesis_power"] for org in ("openstack", "wikimedia")}
    if len(power) != 1:
        raise SystemExit(f"the simulations are sized at different powers: {power}")
    values["sized_studies"] = SIZED_STUDIES
    values["sized_found"] = round(SIZED_STUDIES * power.pop())
    return values


def readings_js(values: dict) -> str:
    """The figures as a script the deck loads: a `.js` file, so it opens from file:// with no server."""
    body = json.dumps(values, indent=2)
    return (
        "// GENERATED by figures.py from the sphragis artifacts. Do not edit.\n"
        f"window.DECK_DATA = Object.assign(window.DECK_DATA || {{}}, {{ readings: {body} }});\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if data/readings.js is stale")
    args = parser.parse_args()
    expected = readings_js(readings())
    if args.check:
        committed = READINGS.read_text() if READINGS.is_file() else ""
        if committed != expected:
            print(f"{READINGS.name} is stale against the sphragis artifacts; run figures.py")
            return 1
        print(f"{READINGS.name} matches the sphragis artifacts")
        return 0
    READINGS.write_text(expected)
    print(f"wrote {READINGS.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
