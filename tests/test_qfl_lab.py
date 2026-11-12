"""The QFL privacy talk: its in-browser simulator (qfl-privacy/lab-sim.js) and its figures.py.

The simulator is checked against an independent statevector written here with complex 2x2
matrices, its parameter-shift gradient against a finite difference, and its shot sampler's mean
and spread against the binomial law. Each lab step's preset is held to the story the script
tells. figures.py is checked to refuse a value the paper does not print.
"""

from __future__ import annotations

import cmath
import importlib.util
import json
import math
import os
import pathlib
import random
import re
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TALK = ROOT / "qfl-privacy"
SIM = TALK / "lab-sim.js"
QFL = pathlib.Path(os.environ.get("QFL") or ROOT.parent / "csci739-qfl-privacy")

needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="needs node")


def js(body: str) -> object:
    """Run `body` in node with the simulator loaded as Q; it prints one JSON value."""
    prog = f"const Q = require({json.dumps(str(SIM))});\n{body}"
    out = subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# An independent reference: the same circuit with complex matrices.
def ry(a: float) -> list[list[complex]]:
    c, s = math.cos(a / 2), math.sin(a / 2)
    return [[c, -s], [s, c]]


def rz(a: float) -> list[list[complex]]:
    return [[cmath.exp(-0.5j * a), 0], [0, cmath.exp(0.5j * a)]]


def apply(m: list[list[complex]], v: list[complex]) -> list[complex]:
    return [m[0][0] * v[0] + m[0][1] * v[1], m[1][0] * v[0] + m[1][1] * v[1]]


def ref_expz(x: float, theta: list[float], reps: int, layers: int) -> float:
    v: list[complex] = [1, 0]
    k = 0
    for _ in range(reps):
        v = apply(ry(x), v)
        for _ in range(layers):
            v = apply(ry(theta[k]), v)
            v = apply(rz(theta[k + 1]), v)
            k += 2
    return abs(v[0]) ** 2 - abs(v[1]) ** 2


SHAPES = [(1, 1), (1, 8), (2, 4), (4, 2), (8, 1), (3, 2)]


@needs_node
@pytest.mark.parametrize(("reps", "layers"), SHAPES)
def test_expectation_matches_an_independent_statevector(reps: int, layers: int) -> None:
    rng = random.Random(reps * 100 + layers)
    cases = [(rng.uniform(-7, 7), [rng.uniform(0, 2 * math.pi) for _ in range(2 * reps * layers)]) for _ in range(5)]
    got = js(f"console.log(JSON.stringify({json.dumps(cases)}.map(([x, t]) => Q.expZ(x, t, {reps}, {layers}))))")
    for (x, theta), z in zip(cases, got, strict=True):
        assert z == pytest.approx(ref_expz(x, theta, reps, layers), abs=1e-12)


@needs_node
@pytest.mark.parametrize(("reps", "layers"), SHAPES)
def test_parameter_shift_gradient_matches_a_finite_difference(reps: int, layers: int) -> None:
    rng = random.Random(7 + reps + 10 * layers)
    x = rng.uniform(0, math.pi)
    theta = [rng.uniform(0, 2 * math.pi) for _ in range(2 * reps * layers)]
    got = js(f"console.log(JSON.stringify(Array.from(Q.gradient({x}, {json.dumps(theta)}, {reps}, {layers}, 1, 0))))")
    f = ref_expz(x, theta, reps, layers)
    h = 1e-6
    for j, g in enumerate(got):
        up, down = theta.copy(), theta.copy()
        up[j] += h
        down[j] -= h
        df = (ref_expz(x, up, reps, layers) - ref_expz(x, down, reps, layers)) / (2 * h)
        assert g == pytest.approx(2 * (f - 1) * df, abs=1e-7)


@needs_node
@pytest.mark.parametrize(("reps", "layers", "shots"), [(1, 8, 0), (2, 4, 100), (4, 2, 0), (8, 1, 10)])
def test_fourier_form_matches_the_direct_loss_and_its_slope(reps: int, layers: int, shots: int) -> None:
    """The attack runs on the loss's Fourier form; it must equal the circuit simulated directly."""
    got = js(
        f"const c = Q.client(5, {reps}, {layers}, {shots});"
        "const L = (x) => Q.matchLoss(x, c.target, c.theta, c.reps, c.layers, c.y);"
        "const xs = [-7.1, -0.4, 0.3, 1.9, 3.3, 5.8, 12.4];"
        "const fd = (x) => (L(x + 1e-6) - L(x - 1e-6)) / 2e-6;"
        "console.log(JSON.stringify(xs.map((x) => [...Q.lossAndSlope(c, x), L(x), fd(x)])))"
    )
    for fast_loss, fast_slope, loss, slope in got:
        assert fast_loss == pytest.approx(loss, abs=1e-11)
        assert fast_slope == pytest.approx(slope, abs=1e-5)


@needs_node
def test_last_z_rotation_never_moves_the_output() -> None:
    """The effective-parameter count the slides use: the last R_Z has zero gradient."""
    got = js("console.log(JSON.stringify(Array.from(Q.gradient(0.7, [0.3,1.1,2.0,0.4,0.9,2.2], 1, 3, 1, 0))))")
    assert got[-1] == pytest.approx(0, abs=1e-12)
    assert all(abs(g) > 1e-9 for g in got[:-1])


@needs_node
def test_an_encoded_input_sits_on_the_xz_circle_at_its_angle() -> None:
    got = js("console.log(JSON.stringify([0.3, 1.9, 4.0].map((x) => Q.bloch(Q.ry([1,0,0,0], x)))))")
    for x, v in zip([0.3, 1.9, 4.0], got, strict=True):
        assert v == pytest.approx([math.sin(x), 0, math.cos(x)], abs=1e-12)


@needs_node
@pytest.mark.parametrize(
    ("z", "shots"),
    [(0.3, 100), (-0.6, 1000), (0.2, 100000), (0.99999, 100000), (-0.999995, 1000000)],
    ids=["binomial-100", "binomial-1000", "normal", "poisson-near-1", "poisson-near-minus-1"],
)
def test_sampled_expectation_has_the_binomial_mean_and_spread(z: float, shots: int) -> None:
    draws = 4000
    got = js(
        f"const r = Q.rng(11); const v = []; for (let i = 0; i < {draws}; i++) v.push(Q.sampleZ({z}, {shots}, r));"
        "console.log(JSON.stringify(v))"
    )
    p = (1 + z) / 2
    sd = 2 * math.sqrt(p * (1 - p) / shots)
    mean = sum(got) / draws
    var = sum((g - mean) ** 2 for g in got) / (draws - 1)
    assert abs(mean - z) < 5 * sd / math.sqrt(draws) + 1e-12
    assert math.sqrt(var) == pytest.approx(sd, rel=0.15)
    assert all(-1 <= g <= 1 for g in got)


@needs_node
def test_exact_means_no_sampling() -> None:
    assert js("console.log(JSON.stringify(Q.sampleZ(0.123, 0, Math.random)))") == 0.123


@needs_node
def test_angle_error_is_taken_modulo_a_full_turn() -> None:
    got = js(
        "const e = Q.angleError;"
        "console.log(JSON.stringify([e(0.1, 2*Math.PI - 0.1), e(7, 7 - 4*Math.PI), e(0, Math.PI)]))"
    )
    assert got == pytest.approx([0.2, 0, math.pi], abs=1e-12)


@needs_node
@pytest.mark.parametrize(
    ("guess_shift", "want"),
    [(0.0499999, "recovered"), (0.0500001, "close"), (0.1999999, "close"), (0.2000001, None)],
)
def test_outcome_thresholds_are_inclusive_like_the_papers(guess_shift: float, want: str | None) -> None:
    got = js(
        f"const c = Q.client(3, 1, 8, 0); const g = c.x + {guess_shift};"
        "console.log(JSON.stringify(Q.outcome(c, g, Q.matchLoss(g, c.target, c.theta, c.reps, c.layers, c.y))))"
    )
    if want is None:
        assert got in ("ambiguous", "stuck")
    else:
        assert got == want


@needs_node
def test_a_guess_that_fits_as_well_as_the_truth_is_ambiguous_not_stuck() -> None:
    got = js(
        "const c = Q.client(3, 1, 8, 0); const far = c.x + 2;"
        "console.log(JSON.stringify([Q.outcome(c, far, 0), Q.outcome(c, far, 1e9)]))"
    )
    assert got == ["ambiguous", "stuck"]


@needs_node
def test_the_same_seed_replays_the_same_attack() -> None:
    body = "const a = Q.attack(Q.client(42, 2, 4, 100), 3); console.log(JSON.stringify(a.runs.map((r) => r.end)))"
    assert js(body) == js(body)


def presets() -> dict[str, dict[str, int]]:
    src = (TALK / "lab.js").read_text()
    found = {
        name: {k: int(v) for k, v in re.findall(r"(\w+): (\d+)", body)}
        for name, body in re.findall(r"^\s+(\w+): \{ free: \"\w+\", ([^}]*)\}", src, re.M)
    }
    assert set(found) == {"reps", "restarts", "shots"}
    return found


@needs_node
def test_repetitions_preset_shows_fewer_restarts_finding_the_input() -> None:
    seed = presets()["reps"]["seed"]
    hits = js(
        f"console.log(JSON.stringify([[1,8],[2,4],[4,2],[8,1]].map(([r, l]) =>"
        f" Q.attack(Q.client({seed}, r, l, 0), 10).runs.filter((u) => u.outcome === 'recovered').length)))"
    )
    # explainer.md quotes these four counts
    assert hits == [10, 8, 6, 1]


@needs_node
def test_restarts_preset_is_stuck_alone_and_found_with_more() -> None:
    p = presets()["restarts"]
    seq = js(
        f"const a = Q.attack(Q.client({p['seed']}, {p['reps']}, {8 // p['reps']}, 0), 20);"
        "const out = []; for (let n = 1; n <= 20; n++) {"
        " const b = a.runs.slice(0, n).reduce((x, u) => (u.loss < x.loss ? u : x)); out.push(b.outcome); }"
        "console.log(JSON.stringify(out))"
    )
    # explainer.md: stuck with 1 to 5 restarts, the 6th finds the input
    assert p["restarts"] == 1
    assert seq[:5] == ["stuck"] * 5
    assert seq[5:] == ["recovered"] * 15


@needs_node
def test_shots_preset_matches_the_explainer() -> None:
    p = presets()["shots"]
    layers = 8 // p["reps"]
    got = js(
        f"const c = (s) => Q.client({p['seed']}, {p['reps']}, {layers}, s);"
        "const run = (s) => { const a = Q.attack(c(s), 10); return [a.outcome, a.error]; };"
        "console.log(JSON.stringify([0, 1000, 100, 10].map(run)))"
    )
    # explainer.md: recovered when exact and at 1,000 shots (0.028 rad), close at 100 (0.148),
    # ambiguous at 10 (1.087)
    assert [o for o, _ in got] == ["recovered", "recovered", "close", "ambiguous"]
    assert [round(e, 3) for _, e in got[1:]] == [0.028, 0.148, 1.087]


def figures_module():
    spec = importlib.util.spec_from_file_location("qfl_figures", TALK / "figures.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_outcome_rule_matches_the_simulator_and_the_paper() -> None:
    f = figures_module()
    rule = f.Rule({"RecoveredRad": "0.05", "CloseRad": "0.2", "ExplainsSlack": r"\ensuremath{10^{-6}}"})
    row = {"true_match": 0.0, "grad_norm2": 1.0}
    assert rule.classify(0.05, 1.0, row) == "recovered"
    assert rule.classify(0.2, 1.0, row) == "close"
    assert rule.classify(1.0, 1e-6, row) == "ambiguous"
    assert rule.classify(1.0, 2e-6, row) == "stuck"


def test_a_value_the_paper_does_not_print_stops_the_build() -> None:
    f = figures_module()
    f.agree("same", "20, 18, 8 and 2", "20, 18, 8 and 2")
    with pytest.raises(f.Mismatch):
        f.agree("RecByRepsLarge", "20, 18, 8 and 2", "20, 18, 9 and 2")


@pytest.mark.skipif(not (QFL / "results").is_dir(), reason="needs a csci739-qfl-privacy checkout (set QFL)")
def test_figures_agree_with_the_papers_tables_and_are_current() -> None:
    run = subprocess.run(
        ["python3", str(TALK / "figures.py"), "--check"],
        capture_output=True,
        text=True,
        env={**os.environ, "QFL": str(QFL)},
    )
    assert run.returncode == 0, run.stderr


MUTANTS = [
    "RecByRepsLarge",
    "SquareWrongSmall",
    "BudgetOthersMin",
    "BudgetHardestHeld",
    "ShotNoiseLarge",
    "ShotLowAmbigLargeMin",
    "BatchHeldMinRatio",
    "BatchFewestRecoveredBelow",
    "LabelKnownOnlyAll",
    "LabelTopStuckUnknown",
    "TrainedOnlyBeforeAll",
    "TrainedOnlyAfterCurvesTwo",
]


@pytest.mark.skipif(not (QFL / "results").is_dir(), reason="needs a csci739-qfl-privacy checkout (set QFL)")
@pytest.mark.parametrize("macro", MUTANTS)
def test_a_changed_macro_is_caught(tmp_path: pathlib.Path, macro: str) -> None:
    """Mutation check: change one digit of one macro the deck shows; the build must stop on it."""
    fake = tmp_path / "qfl"
    (fake / "report" / "tables").mkdir(parents=True)
    (fake / "results").symlink_to(QFL / "results")
    for t in (QFL / "report" / "tables").iterdir():
        (fake / "report" / "tables" / t.name).write_text(t.read_text())
    numbers = fake / "report" / "tables" / "numbers.tex"
    before = numbers.read_text()
    line = re.compile(r"(\\newcommand\{\\" + macro + r"\}\{[^0-9]*)(\d)")
    after = line.sub(lambda m: m[1] + str((int(m[2]) + 1) % 10), before, count=1)
    assert after != before, f"the mutant must change {macro}"
    numbers.write_text(after)
    run = subprocess.run(
        ["python3", str(TALK / "figures.py"), "--check"],
        capture_output=True,
        text=True,
        env={**os.environ, "QFL": str(fake)},
    )
    assert run.returncode != 0
    assert macro in (run.stderr + run.stdout), run.stderr + run.stdout
