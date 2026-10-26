#!/usr/bin/env python3
"""Every figure the Federated Agents deck shows, derived from the sphragis artifacts.

No figure on a slide is typed by hand. This module reads the artifacts and writes
`data/readings.js`, which the slides bind to; `--check` fails when the committed copy no longer
matches what the artifacts say. The PDF version of this talk imports `readings()` from here,
so the two cannot disagree.

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
    # Bounded: the interval's upper end lies below the SESOI (sphragis research log 2026-10-14).
    ("bounded", True): ("shows no gain that matters", "none that matters", "no team-specific gain that matters"),
    ("bounded", False): ("shows no gain that matters", "none that matters", "no team-specific gain that matters"),
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
    """The H1 simulation at the K a Gerrit test read takes, both drawn in relation chains, H1's
    registered cluster unit (sphragis `k-coverage-<org>-likelihood-chains.json`).

    The panel says a real effect of the smallest size that matters is found at the registered
    power, which holds only if every effect the simulation detects at that power, at the spread
    K was sized on, is below the SESOI.
    """
    k = load(f"k-coverage-{org}-likelihood-chains.json")
    if k.get("metric") != METRIC:
        raise SystemExit(f"{org}'s K source is on {k.get('metric')}, not {METRIC}")
    if (k.get("cluster_unit") or {}).get("unit") != "chain":
        raise SystemExit(f"{org}'s K source is not drawn in relation chains")
    matches = [
        sim
        for path in sorted(RESULTS.glob(f"partition-sensitivity-{org}{DECODER}-{METRIC}*.json"))
        # A simulation written before the null-only mode existed carries no flag and is full.
        if not (sim := json.loads(path.read_text())).get("null_only", False)
        and sim.get("metric") == METRIC
        # The simulation drew the same cluster unit as the K source (a by-change one carries none).
        and (sim.get("cluster_unit") or {}).get("unit") == (k.get("cluster_unit") or {}).get("unit")
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


#: The funnel's stages on the slide, each a group of sphragis `dataset_funnel.py` steps summed in
#: their own unit, with the reasons drawn inside it: (label, unit, steps, reasons shown).
FUNNEL_STAGES = (
    ("comments set aside", "comments", ("Comments dropped", "Comments removed at refinement"), 3),
    (
        "pairs that are not a fix",
        "pairs",
        ("Hunks dropped as ill-posed", "Examples dropped at refinement", "Examples left with no comment"),
        3,
    ),
    ("copies removed", "lessons", ("Examples removed as duplicates",), 2),
)

#: Steps the slide leaves to the rule page, each allowed only while it stays below this share of
#: the merged changes; every other step must be in a stage, or the build fails.
FUNNEL_LEFT_OUT = {
    "Changes lost before any comment was read": 0.001,
    # Zero for a full build; a community built skipping uncommented changes needs its own stage.
    "Changes the build did not read": 0.001,
}

#: Plain words for a funnel row, so the slide speaks to a newcomer; a row not listed fails the build.
FUNNEL_WORDS = {
    "on the commit message or the patch set as a whole": "not on a code file",
    "written by the change's author": "the author's own",
    "from an account the host tags as a bot": "from a bot account",
    "an acknowledgement (Done, LGTM, thanks, ok and the like)": "\u201cDone\u201d, \u201cLGTM\u201d",
    "an acknowledgement": "\u201cDone\u201d, \u201cLGTM\u201d",
    "a bot's template, matched to the bot's own source": "a bot's template",
    "only acknowledgements were left": "only \u201cDone\u201d left",
    "only a bot's templates were left": "only bot text left",
    "anchored to no line": "on no line",
    "on the last patch set, with no revision after it": "never revised",
    "its diff could not be fetched": "unreadable",
    "outside any hunk the next patch set changed": "on code left unchanged",
    "nothing before or after the edit": "empty on one side",
    "grown or shrunk past the size rules": "too large a rewrite",
    "next patch set only a rebase, not a rework": "only a rebase",
    "target written by the reviewer (suggested edit, applied fix)": "the reviewer wrote the fix",
    "exact copies": "exact copies",
    "near duplicates (MinHash)": "near copies",
    "shared boilerplate": "boilerplate",
    "one change in two places": "one change twice",
}


def funnel(values: dict) -> dict:
    """Each community's way from merged changes to lessons (sphragis `dataset-funnel.json`).

    The stages are in different units (comments, pairs, lessons), so no width is shared between
    them; inside a stage the reasons are in one unit and drawn to scale. The lessons kept must be
    the corpus the deck counts elsewhere, or the build fails.
    """
    art = load("dataset-funnel.json")["organizations"]
    out = {}
    for org, name in (("openstack", "OpenStack"), ("wikimedia", "Wikimedia")):
        f = art[org]
        steps = {st["step"]: st["rows"] for st in f["steps"]}
        staged = {n for _, _, names, _ in FUNNEL_STAGES for n in names}
        if unplaced := set(steps) - staged - set(FUNNEL_LEFT_OUT):
            raise SystemExit(f"{org}: funnel steps in no stage {sorted(unplaced)}")
        for step, most in FUNNEL_LEFT_OUT.items():
            if sum(r["count"] or 0 for r in steps.get(step, [])) > most * f["merged_changes"]:
                raise SystemExit(f"{org}: {step} is too large to leave off the slide")
        stages = []
        for label, unit, names, shown in FUNNEL_STAGES:
            rows = [r for n in names for r in steps[n]]
            # OpenStack's bot rule could not run (its months predate the bot tag; sphragis
            # docs/dataset.md), so it removed nothing there and the stage total is exact.
            if any(r["count"] is None for r in rows if r["reason"] != "from an account the host tags as a bot"):
                raise SystemExit(f"{org}: a {label} row was not counted")
            unknown = [r["reason"] for r in rows if r["count"] and r["reason"] not in FUNNEL_WORDS]
            if unknown:
                raise SystemExit(f"no plain words for funnel rows {unknown}")
            # Rows with the same plain words (an acknowledgement dropped on reading and at
            # refinement) are one reason on the slide.
            by_words: dict[str, int] = {}
            for r in rows:
                if r["count"]:
                    words = FUNNEL_WORDS[r["reason"]]
                    by_words[words] = by_words.get(words, 0) + r["count"]
            counted = sorted(by_words.items(), key=lambda kv: -kv[1])
            total = sum(by_words.values())
            # One leftover reason is named rather than called "other reasons".
            top = counted if len(counted) <= shown + 1 else counted[:shown]
            reasons = [{"label": words, "count": count} for words, count in top]
            rest = total - sum(count for _, count in top)
            if rest:
                reasons.append({"label": "other reasons", "count": rest})
            stages.append({"label": label, "unit": unit, "count": total, "reasons": reasons})
        kept = f["examples"]
        if f"{kept:,}" != values[f"corpus_examples_{org}"]:
            raise SystemExit(f"{org}: the funnel keeps {kept:,}, the corpus counts {values[f'corpus_examples_{org}']}")
        out[org] = {"name": name, "changes": f["merged_changes"], "stages": stages, "kept": kept}
    return out


#: The split of the team-specific contrast (sphragis research log 2026-10-15): the parts that add
#: up to s, by the pilots' component files, read at the stricter Holm level.
SPLITS = {
    "names": (("identifier", "names"), ("other", "the rest")),
    "edit": (("changed", "what the fix changed"), ("copied", "code carried over")),
}


def split() -> dict:
    """Each community's development contrast, whole and split two ways, with 97.5% intervals."""
    level = "0.975"
    out = {}
    for org, name in ORGS.items():
        whole = load(f"partition-pilot-{org}-likelihood.json")
        if whole.get("metric") != METRIC:
            raise SystemExit(f"{org}'s pilot is on {whole.get('metric')}, not {METRIC}")

        def cell(d: dict) -> dict:
            interval = d["intervals"][level]
            return {"estimate": d["estimate"], "low": interval["low"], "high": interval["high"]}

        entry = {"name": name, "whole": cell(whole)}
        for key, parts in SPLITS.items():
            entry[key] = []
            for component, label in parts:
                part = load(f"partition-pilot-{org}-likelihood-split-{component}.json")
                if part.get("metric") != f"{METRIC}:{component}" or part["run_files"] != whole["run_files"]:
                    raise SystemExit(f"{org}'s {component} split is not read on the pilot's runs")
                entry[key].append({"label": label, **cell(part)})
            end = load(f"partition-pilot-{org}-likelihood-split-end.json")["estimate"]
            total = sum(p["estimate"] for p in entry[key]) + end
            if not math.isclose(total, whole["estimate"], abs_tol=1e-6):
                raise SystemExit(f"{org}'s {key} parts add to {total}, not {whole['estimate']}")
        out[org] = entry
    return out


def registered(name: str) -> dict:
    return load(name)["readings"][REGISTERED[0]][REGISTERED[1]]["per_org"]


def readings() -> dict[str, str | int | bool]:
    """Every figure and flag the deck shows, by the name a slide binds it to."""
    values: dict[str, str | int | bool] = {}
    # The corpora as the study loads them (deduplicated, split into windows), every window but
    # the sealed test one, and the label audit's scored sample.
    built = load("ai-trailers.json")["orgs"]
    for org in ("openstack", "wikimedia"):
        corpus = built[org]["windows"].values()
        values[f"corpus_examples_{org}"] = f"{sum(w['examples'] for w in corpus):,}"
        values[f"corpus_changes_{org}"] = f"{sum(w['changes'] for w in corpus):,}"
    # Every figure here comes from data the study may publish: Qt's records fetched before its
    # 2026-10-15 grant are in none of them (sphragis research log), and data/readings.js is public.
    values["funnel"] = funnel(values)
    values["split"] = split()
    # The split slide claims only what the intervals show. Its claims are about the communities
    # whose whole gain is clear (interval above zero): there the fix carries it and the part
    # outside names is above zero. Carried-over code is "next to none" only if every
    # community's interval holds zero; a community without a clear gain is named as unsettled.
    sp = values["split"]
    gain = [o for o in sp.values() if o["whole"]["low"] > 0]
    unsettled = [o["name"] for o in sp.values() if o["whole"]["low"] <= 0]
    values["split_gain_orgs"] = " and ".join(o["name"] for o in gain)
    values["split_in_fix"] = bool(gain) and all(o["edit"][0]["low"] > 0 for o in gain)
    values["split_beyond_names"] = bool(gain) and all(o["names"][1]["low"] > 0 for o in gain)
    values["split_copied_none"] = all(o["edit"][1]["low"] <= 0 <= o["edit"][1]["high"] for o in sp.values())
    values["split_unsettled_orgs"] = " and ".join(unsettled)
    values["split_any_unsettled"] = bool(unsettled)
    # The label audit on OpenStack's items alone (sphragis label-audit-v2-openstack.json): the
    # share of lessons whose rewrite answers its comment, by the rater the human checked.
    audit = load("label-audit-v2-openstack.json")
    valid = audit["valid_shares"]["A"]
    values["audit_valid_openstack"] = f"{100 * valid['share']:.0f}%"
    values["audit_items_openstack"] = audit["items"]
    # How far OpenStack's development pilot moves when read without its AI-assisted examples, on
    # the registered score (sphragis research log, 2026-10-21).
    pilot = load("partition-pilot-openstack-likelihood-sensitivities.json")
    if pilot.get("metric") != METRIC:
        raise SystemExit(f"the sensitivities are on {pilot.get('metric')}, not {METRIC}")
    values["ai_shift_openstack"] = f"{pilot['without']['ai_assisted']['estimate'] - pilot['estimate']:+.4f}"
    # The backport lookup (sphragis research log, 2026-10-20): the share of development targets
    # whose added lines already stood in their project at the weight upload, as a range over the
    # communities, and whether leaving them out keeps each development pilot's reading, on the
    # registered score at the deck's level.
    shares = []
    for org in ("openstack", "wikimedia", "qt"):
        dev = load(f"backport-lookup-{org}.json")["windows"]["dev"]
        shares.append(dev["found"] / dev["examples"])
    low, high = round(100 * min(shares)), round(100 * max(shares))
    values["found_share_dev"] = f"{low}%" if low == high else f"{low}% to {high}%"
    holds = []
    for org in ORGS:
        read = load(f"partition-pilot-{org}-likelihood-sensitivities.json")
        if read.get("metric") != METRIC:
            raise SystemExit(f"the sensitivities are on {read.get('metric')}, not {METRIC}")
        primary = read["intervals"]["0.975"]["low"] > 0
        without = read["without"]["found_before_checkpoint"]["intervals"]["0.975"]["low"] > 0
        holds.append(primary == without)
    values["found_holds"] = all(holds)
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
    # The development pilots read again with relation chains as the resampled unit, H1's
    # registered cluster unit (sphragis research log, 2026-10-21): whether every community's
    # verdict at the deck's level is the one it has by change.
    same = []
    for org in (*ORGS, "qt"):
        by_change = load(f"partition-pilot-{org}-likelihood.json")
        by_chain = load(f"partition-pilot-{org}-likelihood-chains.json")
        if by_chain.get("metric") != METRIC or by_chain["cluster_unit"]["unit"] != "chain":
            raise SystemExit(f"{org}'s chain pilot is not on {METRIC} by chain")
        same.append(by_change["verdicts"]["0.975"] == by_chain["verdicts"]["0.975"])
    values["chains_hold"] = all(same)
    # Qt's development pilot, read before Qt is admitted: the status slide names its reading alone
    # (sphragis research log, 2026-10-18).
    values["team_qt"] = team_reading(load("partition-pilot-qt-likelihood.json"))[0]
    # Check 5: each half's own marker planted in half its training lessons; how many runs found it.
    planted = {org: planted_runs(org) for org in ("openstack", "wikimedia")}
    if len({len(v) for v in planted.values()}) != 1:
        raise SystemExit(f"planted runs differ in number: { {o: len(v) for o, v in planted.items()} }")
    every = [v for runs in planted.values() for v in runs]
    values["planted_runs"] = len(every)
    values["planted_found"] = every.count("pass")
    values["planted_all"] = values["planted_found"] == values["planted_runs"]
    # Each community's K from the coverage rule a Gerrit test read takes it from, in relation
    # chains, beside the reproducibility K it would have had: the coverage rule raised it where
    # they differ (sphragis research log, 2026-10-22).
    for org in ORGS:
        k = load(f"k-coverage-{org}-likelihood-chains.json")
        values[f"k_{org}"] = k["runs"]
        values[f"k_reproducibility_{org}"] = k["reproducibility_runs"]
        values[f"k_raised_{org}"] = k["runs"] > k["reproducibility_runs"]
    # The sizing panel: studies out of SIZED_STUDIES that find an effect at the registered power.
    power = {sized_simulation(org)["hypothesis_power"] for org in (*ORGS, "qt")}
    if len(power) != 1:
        raise SystemExit(f"the simulations are sized at different powers: {power}")
    values["sized_studies"] = SIZED_STUDIES
    values["sized_found"] = round(SIZED_STUDIES * power.pop())
    return values


def bound_paths(page: str | None = None) -> set[str]:
    """Every `readings.` path a slide binds, through any data-* attribute."""
    page = (HERE / "index.html").read_text() if page is None else page
    return set(re.findall(r'data-[\w-]+="readings\.([\w.]+)"', page))


def published(values: dict, bound: set[str]) -> dict:
    """Only what a slide binds: readings.js is public, so a figure no slide shows stays out of it.
    A bound path keeps everything under it."""

    def keep(node: object, path: str) -> object:
        if path in bound:
            return node
        if isinstance(node, dict) and any(b.startswith(path + ".") for b in bound):
            kept = {k: keep(v, f"{path}.{k}") for k, v in node.items()}
            return {k: v for k, v in kept.items() if v is not _CUT}
        return _CUT

    kept = {k: keep(v, k) for k, v in values.items()}
    return {k: v for k, v in kept.items() if v is not _CUT}


_CUT = object()


def readings_js(values: dict) -> str:
    """The figures as a script the deck loads: a `.js` file, so it opens from file:// with no server."""
    body = json.dumps(published(values, bound_paths()), indent=2)
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
