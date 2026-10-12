"""Controls for the Federated Agents deck's derivations: every guard that keeps a slide from
reading wrongly when a sphragis artifact changes is tripped here on a synthetic artifact, because
a guard that cannot fail is worse than no guard."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

DECK = Path(__file__).resolve().parents[1] / "federated-agents"


@pytest.fixture
def figures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("deck_figures_derivations", DECK / "figures.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "RESULTS", tmp_path)
    return module


def _write(root: Path, name: str, data: dict) -> None:
    (root / name).write_text(json.dumps(data))


def _pilot(verdict: str, within: bool, metric: str = "logprob_per_token") -> dict:
    return {"metric": metric, "verdicts": {"0.975": verdict}, "within_sesoi": {"0.975": within}}


@pytest.mark.parametrize(
    "key",
    ["supported/False", "supported/True", "inconclusive/True", "inconclusive/False", "bounded/True", "bounded/False"],
)
def test_every_mapped_pilot_state_has_wording(figures, key: str) -> None:
    verdict, within = key.split("/")
    assert all(figures.team_reading(_pilot(verdict, within == "True")))


@pytest.mark.parametrize("pilot", [_pilot("contradicted", True), _pilot("supported", False, metric="exact_match")])
def test_an_unworded_state_or_another_metric_fails_the_build(figures, pilot: dict) -> None:
    with pytest.raises(SystemExit):
        figures.team_reading(pilot)


def test_the_title_names_each_community_only_when_they_differ(figures) -> None:
    gain = figures.TEAM_READING[("supported", False)]
    none = figures.TEAM_READING[("inconclusive", True)]
    assert figures.team_title({"openstack": gain, "wikimedia": gain}) == gain[2]
    differ = figures.team_title({"openstack": gain, "wikimedia": none})
    assert differ == f"{gain[1]} on OpenStack, {none[1]} on Wikimedia"


def _planted_run(seed: int, *, org: str = "openstack", rate: float = 0.4) -> dict:
    source = f"train -> dev windows under /d/corpus-partition-{org}-p{seed}-plant0.5/{{half}}/refined"
    rows = [{"exact_match": 1.0}] * int(10 * rate) + [{"exact_match": 0.0}] * (10 - int(10 * rate))
    return {
        "metric": "logprob_per_token",
        "train_size": 1850,
        "corpora": {f"{org}-{h}": {"source": source.format(half=h)} for h in "ab"},
        "results": {f"adapter:{org}-a|{org}-a|s1": rows, "base|x": [{"exact_match": 0.0}]},
        "verdict": {"verdict": "pass"},
    }


def _retarget(run: dict, old: str, new: str) -> dict:
    """The run with every half's corpus source rewritten."""
    corpora = {h: {"source": c["source"].replace(old, new)} for h, c in run["corpora"].items()}
    return {**run, "corpora": corpora}


def _planted(root: Path, runs: list[dict], org: str = "openstack") -> None:
    _write(root, f"admissible-partitions-{org}.json", {"size_floor": 1850})
    for n, run in enumerate(runs):
        _write(root, f"likelihood-partition-{org}-p{n}-plant0.5-rp1.0.json", run)


def test_planted_runs_count_one_verdict_per_partition(figures, tmp_path: Path) -> None:
    _planted(tmp_path, [_planted_run(1), _planted_run(2)])
    assert figures.planted_runs("openstack") == ["pass", "pass"]


@pytest.mark.parametrize(
    "bad",
    [
        _planted_run(1, rate=0.0),  # a degenerate adapter arm (test 6)
        _planted_run(1, rate=1.0),
        {**_planted_run(1), "corpora": {"openstack-a": _planted_run(1)["corpora"]["openstack-a"]}},
        {**_planted_run(1), "train_size": 900},
        {**_planted_run(1), "metric": "exact_match"},
        _retarget(_planted_run(1), "train -> dev windows", "train -> test windows"),  # another window
        _retarget(_planted_run(1), "-plant0.5/", "-plant0.25/"),  # another strength
        _planted_run(1, org="wikimedia")
        | {
            "corpora": {
                f"openstack-{h}": c
                for h, c in zip("ab", _planted_run(1, org="wikimedia")["corpora"].values(), strict=True)
            }
        },
    ],
)
def test_a_run_that_is_not_check_5_fails_the_build(figures, tmp_path: Path, bad: dict) -> None:
    _planted(tmp_path, [bad])
    with pytest.raises(SystemExit):
        figures.planted_runs("openstack")


def test_the_same_partition_twice_fails_the_build(figures, tmp_path: Path) -> None:
    _planted(tmp_path, [_planted_run(3), _planted_run(3)])
    with pytest.raises(SystemExit, match="not one new partition"):
        figures.planted_runs("openstack")


TARGETS = {"sizing_bound_90": 0.008}


def _sizing(
    root: Path,
    *,
    mde: float,
    sesoi: float = 0.0183,
    registered: float = 0.0183,
    k_metric: str = "logprob_per_token",
    sim_metric: str = "logprob_per_token",
    null_trials: int = 4000,
) -> None:
    _write(root, "likelihood-sesoi.json", {"sesoi": registered})
    _write(
        root,
        "k-coverage-wikimedia-likelihood.json",
        {
            "metric": k_metric,
            "runs": 20,
            "null_trials": 4000,
            "spread_target": "sizing_bound_90",
            "spread_targets": TARGETS,
        },
    )
    cells = {"1": {"minimum_detectable_effect": mde / 2}, "2": {"minimum_detectable_effect": mde}}
    _write(
        root,
        "partition-sensitivity-wikimedia-rp1.0-logprob_per_token-k20.json",
        {
            "metric": sim_metric,
            "null_only": False,
            "runs": 20,
            "null_trials": null_trials,
            "spread_targets": TARGETS,
            "sesoi": sesoi,
            "hypothesis_power": 0.95,
            "by_target": {"sizing_bound_90": {"by_level": {"0.975": {"by_cells": cells}}}},
        },
    )


def test_a_simulation_below_the_sesoi_sizes_the_panel(figures, tmp_path: Path) -> None:
    _sizing(tmp_path, mde=0.007)
    assert figures.sized_simulation("wikimedia")["hypothesis_power"] == 0.95


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mde": 0.0183},  # at the SESOI
        {"mde": 0.010, "sesoi": 0.05},  # sized at a SESOI not registered, every MDE below both
        {"mde": 0.007, "k_metric": "exact_match"},
        {"mde": 0.007, "sim_metric": "exact_match"},
        {"mde": 0.007, "null_trials": 1000},
    ],
)
def test_a_simulation_that_cannot_back_the_panel_fails_the_build(figures, tmp_path: Path, kwargs: dict) -> None:
    _sizing(tmp_path, **kwargs)
    with pytest.raises(SystemExit):
        figures.sized_simulation("wikimedia")
