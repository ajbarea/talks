"""Controls for the Federated Agents deck's staleness guard.

The deck's figures are generated, and the guard fails when the committed copy stops matching the
sphragis artifacts. A guard that cannot fail is worse than no guard, so these trip it on purpose.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
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


def test_the_guard_fails_when_a_figure_is_edited_by_hand(tmp_path: Path) -> None:
    """On a copy, so a run killed mid-test cannot leave the committed figures edited."""
    deck = tmp_path / "federated-agents"
    (deck / "data").mkdir(parents=True)
    shutil.copy(DECK / "figures.py", deck)
    original = (DECK / "data" / "readings.js").read_text()
    edited = original.replace('"split_in_fix"', '"split_in_fix_x"', 1)
    assert edited != original, "the edit must change the figures, or the guard is not exercised"
    (deck / "data" / "readings.js").write_text(edited)
    result = subprocess.run(
        [sys.executable, str(deck / "figures.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SPHRAGIS": str(SPHRAGIS)},
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "readings.js is stale" in result.stdout


def test_every_bound_name_has_a_figure() -> None:
    """A slide bound to a name the module does not write would show nothing."""
    page = (DECK / "index.html").read_text()
    paths = set(re.findall(r'data-(?:value|dots|of|if|unless|source)="readings\.([\w.]+)"', page))
    assert paths, "the deck binds no figures"
    values = _figures().readings()
    missing = []
    for path in paths:
        node = values
        for key in path.split("."):
            if not isinstance(node, dict) or key not in node:
                missing.append(path)
                break
            node = node[key]
    assert not missing, missing
