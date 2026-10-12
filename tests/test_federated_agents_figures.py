"""Controls for the Federated Agents deck's staleness guard.

The deck's figures are generated, and the guard fails when the committed copy stops matching the
sphragis artifacts. A guard that cannot fail is worse than no guard, so these trip it on purpose.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

DECK = Path(__file__).resolve().parents[1] / "federated-agents"
SPHRAGIS = Path(os.environ.get("SPHRAGIS") or DECK.parents[1] / "sphragis")

pytestmark = pytest.mark.skipif(
    not (SPHRAGIS / "datasets" / "results").is_dir() and not os.environ.get("CI"),
    reason="the deck's figures come from a sphragis checkout; set SPHRAGIS",
)


def _figures():
    spec = importlib.util.spec_from_file_location("deck_figures", DECK / "figures.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_figure_is_derived_from_an_artifact() -> None:
    """If this returns little, the slides are quoting numbers from somewhere else."""
    values = _figures().readings()
    assert len(values) >= 8, values


def test_the_committed_readings_match_the_artifacts() -> None:
    module = _figures()
    assert (DECK / "data" / "readings.js").read_text() == module.readings_js(module.readings())


def test_the_guard_fails_when_a_figure_is_edited_by_hand() -> None:
    path = DECK / "data" / "readings.js"
    original = path.read_text()
    try:
        path.write_text(original.replace('"verdict"', '"verdict_x"', 1))
        result = subprocess.run([sys.executable, str(DECK / "figures.py"), "--check"], capture_output=True, text=True)
        assert result.returncode == 1, result.stdout + result.stderr
        assert "readings.js is stale" in result.stdout
    finally:
        path.write_text(original)


def test_every_bound_name_has_a_figure() -> None:
    """A slide bound to a name the module does not write would show nothing."""
    page = (DECK / "index.html").read_text()
    bound = set(re.findall(r'data-(?:value|dots|of|if|unless)="readings\.(\w+)"', page))
    assert bound, "the deck binds no figures"
    assert bound <= set(_figures().readings()), bound - set(_figures().readings())
