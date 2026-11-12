#!/usr/bin/env python3
"""Every number this deck shows, read from the csci739-qfl-privacy results.

Writes `data/readings.js` (the values the slides and `script.md` bind to) and draws the paper's
20-seed results as SVG into `index.html`, between `<!-- fig:NAME -->` and `<!-- /fig -->`, so they
show in the exports and with scripts off, and their text alternative comes from the same data.
Each value is computed from `results/*.jsonl` with the paper's own outcome rule, then checked
against the paper's generated macros (`report/tables/numbers.tex`) and table rows: a value that
disagrees with the paper stops the build. `--check` fails when the committed files are stale.

    python figures.py            # write data/readings.js and the figures in index.html
    python figures.py --check    # are they current?

QFL points at a csci739-qfl-privacy checkout; the default is a sibling of this repository.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import statistics
import sys
from collections import defaultdict
from html import escape

HERE = pathlib.Path(__file__).resolve().parent
QFL = pathlib.Path(os.environ.get("QFL") or HERE.parents[1] / "csci739-qfl-privacy")
RESULTS = QFL / "results"
TABLES = QFL / "report" / "tables"
READINGS = HERE / "data" / "readings.js"
INDEX = HERE / "index.html"
BLOCK = re.compile(r"<!-- fig:(\w+) -->.*?<!-- /fig -->", re.S)

# Colours of the deck's roles (deck.css): the leak, the held-back input, ink and rules.
LEAK = "#b3361b"
LEAK_TINT = "#f6ddd5"
HELD = "#1d4e89"
INK = "#1a1f24"
MUTED = "#47505a"
RULE = "#bcc2c8"
OPEN = "#ffffff"


class Mismatch(SystemExit):
    pass


def agree(name: str, ours: str, paper: str) -> None:
    """Stop when a value computed here differs from the paper's."""
    if ours != paper:
        raise Mismatch(f"{name}: results/ gives {ours!r}, the paper says {paper!r}")


def macros() -> dict[str, str]:
    path = TABLES / "numbers.tex"
    if not path.is_file():
        raise SystemExit(f"missing {path}; the deck's numbers come from csci739-qfl-privacy")
    found = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", path.read_text(), re.M))
    if not found:
        raise SystemExit(f"no macros in {path}")
    return found


def table_rows(name: str) -> list[str]:
    return [line.strip() for line in (TABLES / f"{name}.tex").read_text().splitlines() if line.strip()]


def load(name: str) -> list[dict]:
    path = RESULTS / f"{name}.jsonl"
    if not path.is_file():
        raise SystemExit(f"missing artifact {path}")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class Rule:
    """The paper's outcome rule (qflp.attack.classify), with its thresholds read from the paper."""

    def __init__(self, m: dict[str, str]) -> None:
        self.recovered = float(m["RecoveredRad"])
        self.close = float(m["CloseRad"])
        slack = re.fullmatch(r"\\ensuremath\{10\^\{(-?\d+)\}\}", m["ExplainsSlack"])
        if not slack:
            raise SystemExit(f"cannot read ExplainsSlack {m['ExplainsSlack']!r}")
        self.slack = 10.0 ** int(slack.group(1))

    def classify(self, error: float, match: float, row: dict) -> str:
        if error <= self.recovered:
            return "recovered"
        if error <= self.close:
            return "close"
        if match <= row["true_match"] + self.slack * row["grad_norm2"]:
            return "ambiguous"
        return "stuck"

    def outcomes(self, row: dict) -> list[str]:
        return [self.classify(d["error"], d["match"], row) for d in row["restarts_detail"]]

    def best(self, row: dict, budget: int | None = None) -> str:
        detail = row["restarts_detail"][:budget]
        fin = [d["match"] if math.isfinite(d["match"]) else math.inf for d in detail]
        return self.outcomes(row)[fin.index(min(fin))]


def group(rows: list[dict], *keys: str) -> dict[tuple, list[dict]]:
    out: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys)].append(r)
    return dict(sorted(out.items()))


def joined(items: list) -> str:
    """The paper's list style: "20, 18, 8 and 2"."""
    s = [str(i) for i in items]
    return s[0] if len(s) == 1 else ", ".join(s[:-1]) + " and " + s[-1]


def circuit(reps: int, layers: int) -> str:
    return f"{reps}\u00d7{layers}"


def tex_circuit(reps: int, layers: int) -> str:
    return f"${reps}\\times{layers}$"


# --- the numbers -------------------------------------------------------------------------------


def rq1(m: dict, rule: Rule, values: dict) -> dict:
    rows = [r for r in load("rq1") if r["shots"] == 0 and r["batch"] == 1]
    seeds = int(m["Seeds"])
    by = group(rows, "n_qubits", "reps", "layers")
    for k, rs in by.items():
        if len(rs) != seeds:
            raise SystemExit(f"rq1 {k}: {len(rs)} seeds, not {seeds}")
    top = max(r * layer for _, r, layer in by)
    line = sorted((reps, rs) for (n, reps, layers), rs in by.items() if n == 8 and reps * layers == top)
    if [reps for reps, _ in line] != [1, 2, 4, 8]:
        raise SystemExit("rq1: the 8-qubit top line is not r = 1, 2, 4, 8")
    recovered = [sum(rule.best(r) == "recovered" for r in rs) for _, rs in line]
    hits = [sum(o == "recovered" for r in rs for o in rule.outcomes(r)) for _, rs in line]
    tries = {len(rs) * len(rs[0]["restarts_detail"]) for _, rs in line}
    effective = {rs[0]["n_effective"] for _, rs in line}
    agree("RecByRepsLarge", joined(recovered), m["RecByRepsLarge"])
    agree("RestartHitsLarge", joined(hits), m["RestartHitsLarge"])
    agree("RestartTries", str(tries.pop()), m["RestartTries"])
    agree("ParamsTopLarge", str(effective.pop()), m["ParamsTopLarge"])
    shallow = [rs for (_, reps, layers), rs in by.items() if reps == 1 and layers >= 2]
    if not all(sum(rule.best(r) == "recovered" for r in rs) == seeds for rs in shallow):
        raise SystemExit("rq1: a 1 x l >= 2 circuit missed a seed; the contribution slide says none did")
    agree("RqOneAttacks", str(len(rows)), m["RqOneAttacks"])
    agree("RqOneShapes", str(len(by)), m["RqOneShapes"])
    # Only the values a slide or the script shows; the deck publishes this file.
    values["rq1"] = {
        "attacks": len(rows),
        "params": int(m["ParamsTopLarge"]),
        "tries": int(m["RestartTries"]),
        "rec1": recovered[0],
        "rec8": recovered[-1],
        "hits1": hits[0],
        "hits8": hits[-1],
        "squareWrongSmall": int(m["SquareWrongSmall"]),
        "squareWrongLarge": int(m["SquareWrongLarge"]),
    }
    return {"line": [(circuit(reps, top // reps), k, h) for (reps, _), k, h in zip(line, recovered, hits, strict=True)]}


def budget(m: dict, rule: Rule, values: dict) -> dict:
    small = int(m["Restarts"])
    large = int(m["BudgetRestarts"])
    rows = [r for r in load("budget") if r["shots"] == 0 and r["batch"] == 1]
    out = []
    lines = []
    for (n, reps, layers), rs in group(rows, "n_qubits", "reps", "layers").items():
        before = sum(rule.best(r, small) == "recovered" for r in rs)
        after = sum(rule.best(r) == "recovered" for r in rs)
        per = [o == "recovered" for r in rs for o in rule.outcomes(r)]
        rate = sum(per) / len(per)
        lines.append(
            f"{n} & {tex_circuit(reps, layers)} & {rs[0]['n_effective']} & {before}/{len(rs)} & "
            f"{after}/{len(rs)} & {100 * rate:.1f}\\% \\\\"
        )
        out.append({"name": circuit(reps, layers), "before": before, "after": after, "rate": round(100 * rate, 1)})
    agree("budget.tex", "\n".join(lines), "\n".join(table_rows("budget")))
    hardest = min(out, key=lambda c: c["rate"])
    agree("BudgetHardestCircuit", tex_circuit(*map(int, hardest["name"].split("\u00d7"))), m["BudgetHardestCircuit"])
    values["budget"] = {
        "small": small,
        "large": large,
        "circuits": len(out),
        "hardest": hardest["name"],
        "hardestRate": float(m["BudgetHardestRate"]),
        "hardestHeld": int(m["BudgetHardestHeld"]),
        "othersMin": int(m["BudgetOthersMin"]),
        "othersMax": int(m["BudgetOthersMax"]),
        "othersCount": int(m["BudgetOthersCount"]),
        "secondsPerClient": int(m["BudgetClientSeconds"]),
    }
    return {"circuits": out}


def rq2(m: dict, rule: Rule, values: dict) -> dict:
    rows = [r for r in load("rq2") if r["batch"] == 1]
    seeds = int(m["Seeds"])
    lines = []
    cells: dict[tuple, dict] = {}
    for (n, reps, layers), rs in group(rows, "n_qubits", "reps", "layers").items():
        shots = group(rs, "shots")
        parts = []
        for (s,), ss in shots.items():
            if len(ss) != seeds:
                raise SystemExit(f"rq2 {n}q {reps}x{layers} {s} shots: {len(ss)} seeds")
            med = statistics.median(r["best_error"] for r in ss)
            within = sum(r["best_error"] <= rule.close for r in ss)
            parts.append(f"{med:.3f} ({within})")
            cells[(n, reps, layers, s)] = {"median": med, "within": within}
        lines.append(f"{n} & {tex_circuit(reps, layers)} & " + " & ".join(parts) + " \\\\")
    agree("rq2.tex", "\n".join(lines), "\n".join(table_rows("rq2")))
    low = min(s for *_, s in cells)
    rows_at = [(n, reps, layers, c["within"]) for (n, reps, layers, s), c in cells.items() if s == low]
    agree("ShotLowWithinLargeMax", str(max(w for n, *_, w in rows_at if n == 8)), m["ShotLowWithinLargeMax"])
    agree("ShotLowWithinSmallMin", str(min(w for n, *_, w in rows_at if n == 4)), m["ShotLowWithinSmallMin"])
    agree("ShotLowWithinSmallMax", str(max(w for n, *_, w in rows_at if n == 4)), m["ShotLowWithinSmallMax"])
    values["rq2"] = {
        "lowShots": low,
        "within8Max": int(m["ShotLowWithinLargeMax"]),
        "within4Min": int(m["ShotLowWithinSmallMin"]),
        "within4Max": int(m["ShotLowWithinSmallMax"]),
        "noise8": m["ShotNoiseLarge"],
        "signal8": m["ShotSignalLarge"],
        "noise4": m["ShotNoiseSmall"],
        "signal4": m["ShotSignalSmall"],
        "slopeMin": tex_number(m["ShotSlopeMin"]),
        "slopeMax": tex_number(m["ShotSlopeMax"]),
        "ambig8Min": int(m["ShotLowAmbigLargeMin"]),
        "ambig8Max": int(m["ShotLowAmbigLargeMax"]),
    }
    return {"low": low, "rows": [(n, circuit(reps, layers), w) for n, reps, layers, w in sorted(rows_at)]}


def rq3(m: dict, rule: Rule, values: dict) -> dict:
    seeds = int(m["Seeds"])
    batch = [r for r in load("rq3") if r["shots"] == 0 and r.get("label", "fixed") == "fixed" and r["restarts"] == 10]
    shapes = {(r["n_qubits"], r["reps"], r["layers"]) for r in batch}
    single = [r for r in load("rq1") if r["shots"] == 0 and (r["n_qubits"], r["reps"], r["layers"]) in shapes]
    lines = []
    series: dict[tuple, list] = defaultdict(list)
    for (n, reps, layers, b), rs in group(batch + single, "n_qubits", "reps", "layers", "batch").items():
        if len(rs) != seeds:
            raise SystemExit(f"rq3 {n}q {reps}x{layers} B={b}: {len(rs)} seeds")
        counts = {o: sum(rule.best(r) == o for r in rs) for o in ("recovered", "close", "ambiguous", "stuck")}
        p = rs[0]["n_effective"]
        err = statistics.median(r["best_error"] for r in rs)
        lines.append(
            f"{n} & {tex_circuit(reps, layers)} & {p} & {b} & {n * b} & {counts['recovered']} & "
            f"{counts['close']} & {counts['ambiguous']} & {counts['stuck']} & {err:.2f} \\\\"
        )
        series[(n, reps, layers)].append((n * b / p, counts["recovered"]))
    agree("rq3.tex", "\n".join(lines), "\n".join(table_rows("rq3")))
    values["rq3"] = {
        "leakMax": m["BatchLeakMaxRatio"],
        "heldMin": m["BatchHeldMinRatio"],
        "fewestBelow": int(m["BatchFewestRecoveredBelow"]),
    }
    return {"series": {f"{n} qubits, {circuit(r, layer)}": pts for (n, r, layer), pts in series.items()}}


def p_value(macro: str) -> str:
    """ "= 0.013" reads "0.013"; "< 0.001" keeps its sign."""
    return macro.replace("=", "").strip()


def tex_number(macro: str) -> str:
    """\\ensuremath{-0.49} reads "-0.49", with a true minus sign."""
    inner = re.fullmatch(r"\\ensuremath\{(.*)\}", macro)
    return (inner.group(1) if inner else macro).replace("-", "\u2212")


def rq4_rq5(m: dict, values: dict) -> dict:
    values["rq4"] = {
        "knownOnly": int(m["LabelKnownOnlyAll"]),
        "unknownOnly": int(m["LabelUnknownOnlyAll"]),
        "p": p_value(m["LabelPooledPAll"]),
        "knownOnlyTwo": int(m["LabelKnownOnlyTwo"]),
        "stuckKnown": int(m["LabelTopStuckKnown"]),
        "stuckUnknown": int(m["LabelTopStuckUnknown"]),
    }
    values["rq5"] = {
        "before": int(m["TrainedOnlyBeforeAll"]),
        "after": int(m["TrainedOnlyAfterAll"]),
        "p": p_value(m["TrainedPooledPAll"]),
        "tasks": int(m["TrainedTasks"]),
        "steps": int(m["TrainedFinalStep"]),
        "attacks": int(m["TrainedAttacks"]),
        "leadBefore": int(m["TrainedOnlyBeforeCurvesTwo"]),
        "leadAfter": int(m["TrainedOnlyAfterCurvesTwo"]),
        "leadAcc": m["TrainedLeadAccLow"],
    }
    return {
        "labels": (values["rq4"]["knownOnly"], values["rq4"]["unknownOnly"]),
        "training": (values["rq5"]["before"], values["rq5"]["after"]),
    }


def settings(m: dict, values: dict) -> None:
    values["paper"] = {
        "seeds": int(m["Seeds"]),
        "restarts": int(m["Restarts"]),
        "recoveredRad": m["RecoveredRad"],
        "closeRad": m["CloseRad"],
        "maxIter": int(m["MaxIter"]),
    }


# --- the still figures -------------------------------------------------------------------------


def svg_open(width: int, height: int, label: str) -> list[str]:
    return [f'<svg class="paper-fig" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">']


def text(x: float, y: float, s: str, size: int = 22, fill: str = INK, anchor: str = "start", weight: int = 400) -> str:
    return (
        f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}">{escape(s)}</text>'
    )


# The figures are drawn 480 units wide, about the width they show at, so a 20-unit label reads as
# 20px on the slide. Each figure's key is HTML beside it, where the contrast gate can measure it.
W = 480


def dot_row(
    x0: float, y: float, filled: int, total: int, extra: int = 0, r: float = 6.5, step: float = 15.5
) -> list[str]:
    """`filled` solid dots, then `extra` ringed ones, then open ones: one per seed."""
    out = []
    for i in range(total):
        cx = x0 + i * step
        if i < filled:
            out.append(f'<circle cx="{cx:g}" cy="{y:g}" r="{r}" fill="{LEAK}"/>')
        elif i < filled + extra:
            ring = f'fill="{LEAK_TINT}" stroke="{LEAK}" stroke-width="2.5"'
            out.append(f'<circle cx="{cx:g}" cy="{y:g}" r="{r - 0.5}" {ring}/>')
        else:
            hollow = f'fill="{OPEN}" stroke="{MUTED}" stroke-width="1.5"'
            out.append(f'<circle cx="{cx:g}" cy="{y:g}" r="{r - 0.5}" {hollow}/>')
    return out


def dot_table(rows: list[tuple[str, int, int, str]], seeds: int, head: tuple[str, str, str], label: str) -> str:
    """Rows of (name, filled, ringed, value at the right), one dot per seed between."""
    h = 44 + 52 * len(rows)
    out = svg_open(W, h, label)
    out.append(text(0, 20, head[0], 19, MUTED))
    out.append(text(96, 20, head[1], 19, MUTED))
    out.append(text(W, 20, head[2], 19, MUTED, "end"))
    for i, (name, filled, extra, value) in enumerate(rows):
        y = 64 + 52 * i
        out.append(text(0, y + 8, name, 24, INK, weight=700))
        out += dot_row(102, y, filled, seeds, extra)
        out.append(text(W, y + 8, value, 24, INK, "end", 700))
    return "\n".join([*out, "</svg>"])


def fig_reps(d: dict, seeds: int, tries: int) -> str:
    rows = [(name, k, 0, str(hit)) for name, k, hit in d["line"]]
    label = f"Seeds whose input was recovered, of {seeds}, by repetitions times layers: " + "; ".join(
        f"{name}: {k} seeds, {hit} of {tries} restarts" for name, k, hit in d["line"]
    )
    return dot_table(rows, seeds, ("r \u00d7 \u2113", f"seeds, of {seeds}", "hits"), label)


def fig_budget(d: dict, seeds: int, small: int, large: int) -> str:
    rows = [
        (c["name"], c["before"], c["after"] - c["before"], f"{c['before']}\u2192{c['after']}") for c in d["circuits"]
    ]
    label = f"Seeds recovered with {small} and with {large} restarts, of {seeds}: " + "; ".join(
        f"{c['name']}: {c['before']} then {c['after']}" for c in d["circuits"]
    )
    return dot_table(rows, seeds, ("r \u00d7 \u2113", f"seeds, of {seeds}", f"{small}\u2192{large}"), label)


def fig_shots(d: dict, seeds: int, close: str) -> str:
    rows = [(f"{n}q {name}", k, 0, str(k)) for n, name, k in d["rows"]]
    label = f"Seeds guessed within {close} radians at {d['low']} shots, of {seeds}: " + "; ".join(
        f"{n} qubits {name}: {k}" for n, name, k in d["rows"]
    )
    return dot_table(rows, seeds, ("circuit", f"seeds within {close} rad", f"of {seeds}"), label)


def mark(shape: str, cx: float, cy: float) -> str:
    """One of four point marks that differ in shape and fill, so the lines part without colour."""
    if shape == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{LEAK}"/>'
    if shape == "square":
        box = f'width="14" height="14" fill="{OPEN}" stroke="{LEAK}" stroke-width="3"'
        return f'<rect x="{cx - 7:.1f}" y="{cy - 7:.1f}" {box}/>'
    if shape == "diamond":
        return f'<path d="M{cx:.1f} {cy - 10:.1f}l10 10l-10 10l-10 -10z" fill="{INK}"/>'
    return f'<path d="M{cx:.1f} {cy - 10:.1f}l10 17h-20z" fill="{OPEN}" stroke="{INK}" stroke-width="3"/>'


def fig_batch(d: dict, seeds: int) -> str:
    h = 470
    left, right, top, bottom = 44, W - 10, 118, 414
    lo, hi = math.log2(1 / 8), math.log2(4)

    def x(v: float) -> float:
        return left + (math.log2(v) - lo) / (hi - lo) * (right - left)

    def y(k: float) -> float:
        return bottom - k / seeds * (bottom - top)

    series = d["series"]
    label = f"Seeds recovered, of {seeds}, against unknown inputs per gradient entry: " + "; ".join(
        f"{name}: " + ", ".join(f"{v:.2f} gives {k}" for v, k in pts) for name, pts in series.items()
    )
    out = svg_open(W, h, label)
    marks = ["circle", "square", "diamond", "triangle"]
    for i, name in enumerate(series):
        lx, ly = 10 + 240 * (i % 2), 18 + 34 * (i // 2)
        out.append(mark(marks[i], lx, ly))
        out.append(text(lx + 18, ly + 7, name, 19, INK))
    out.append(f'<rect x="{x(1):g}" y="{top}" width="{right - x(1):g}" height="{bottom - top}" fill="#e6ecf4"/>')
    out.append(text(right - 6, top + 26, "more unknowns", 19, HELD, "end", 700))
    out.append(text(right - 6, top + 50, "than entries", 19, HELD, "end", 700))
    for k in (0, 10, 20):
        out.append(f'<line x1="{left}" x2="{right}" y1="{y(k):g}" y2="{y(k):g}" stroke="{RULE}" stroke-width="1"/>')
        out.append(text(left - 10, y(k) + 7, str(k), 19, MUTED, "end"))
    for v, s in ((1 / 8, "1/8"), (1 / 4, "1/4"), (1 / 2, "1/2"), (1, "1"), (2, "2"), (4, "4")):
        out.append(text(x(v), bottom + 28, s, 19, MUTED, "middle"))
    dash = f'stroke="{HELD}" stroke-width="2" stroke-dasharray="6 5"'
    out.append(f'<line x1="{x(1):g}" x2="{x(1):g}" y1="{top}" y2="{bottom}" {dash}/>')
    out.append(text(0, top - 14, "seeds recovered", 19, MUTED))
    for i, (_name, pts) in enumerate(series.items()):
        pts = sorted(pts)
        path = " ".join(f"{'M' if j == 0 else 'L'}{x(v):.1f} {y(k):.1f}" for j, (v, k) in enumerate(pts))
        out.append(f'<path d="{path}" fill="none" stroke="{LEAK}" stroke-width="2.5" stroke-opacity="0.5"/>')
        for v, k in pts:
            out.append(mark(marks[i % len(marks)], x(v), y(k)))
    return "\n".join([*out, "</svg>"])


def fig_pairs(d: dict) -> str:
    h = 270
    (k_only, u_only), (before, after) = d["labels"], d["training"]
    biggest = max(k_only, u_only, before, after)
    label = (
        f"Seeds recovered under one condition only. Labels: {k_only} only when known, {u_only} only when hidden. "
        f"Training: {before} only before, {after} only after."
    )
    out = svg_open(W, h, label)
    scale = 200 / biggest

    def bar(y: float, name: str, k: int, fill: str) -> None:
        out.append(text(0, y + 8, name, 21, INK))
        out.append(f'<rect x="210" y="{y - 13:g}" width="{k * scale:.1f}" height="26" fill="{fill}"/>')
        out.append(text(220 + k * scale, y + 8, str(k), 23, INK, weight=700))

    out.append(text(0, 22, "Label", 21, HELD, weight=700))
    bar(60, "only if known", k_only, LEAK)
    bar(98, "only if hidden", u_only, MUTED)
    out.append(text(0, 160, "Training", 21, HELD, weight=700))
    bar(198, "only before", before, LEAK)
    bar(236, "only after", after, MUTED)
    return "\n".join([*out, "</svg>"])


def build() -> dict[pathlib.Path, str]:
    m = macros()
    rule = Rule(m)
    values: dict = {}
    settings(m, values)
    seeds = values["paper"]["seeds"]
    reps = rq1(m, rule, values)
    bud = budget(m, rule, values)
    shots = rq2(m, rule, values)
    batch = rq3(m, rule, values)
    pairs = rq4_rq5(m, values)
    body = json.dumps(values, indent=2, ensure_ascii=False)
    figs = {
        "reps": fig_reps(reps, seeds, values["rq1"]["tries"]),
        "restarts": fig_budget(bud, seeds, values["budget"]["small"], values["budget"]["large"]),
        "shots": fig_shots(shots, seeds, values["paper"]["closeRad"]),
        "batch": fig_batch(batch, seeds),
        "pairs": fig_pairs(pairs),
    }
    page = INDEX.read_text()
    named = BLOCK.findall(page)
    if sorted(named) != sorted(figs):
        raise SystemExit(f"index.html has figure blocks {sorted(named)}; figures.py draws {sorted(figs)}")
    page = BLOCK.sub(lambda b: f"<!-- fig:{b.group(1)} -->\n{figs[b.group(1)]}\n<!-- /fig -->", page)
    return {
        READINGS: "// Generated by figures.py from csci739-qfl-privacy results/; do not edit.\n"
        f"window.DECK_DATA = {body};\n",
        INDEX: page,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when the committed files are stale")
    args = parser.parse_args(argv)
    files = build()
    stale = [p for p, s in files.items() if not p.is_file() or p.read_text() != s]
    if args.check:
        for p in stale:
            print(f"stale: {p.relative_to(HERE)}; run python {pathlib.Path(__file__).name}", file=sys.stderr)
        return 1 if stale else 0
    for p in stale:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(files[p])
        print(f"wrote {p.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
