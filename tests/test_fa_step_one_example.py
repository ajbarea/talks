"""The Federated Agents Step One example slide: each guard on the published example fires.

Runs `figures.py --check` without the corpus, as CI does, against a tampered copy of the
committed readings, and expects each tampering to fail the check.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "federated-agents-step-one"
SPHRAGIS = Path(os.environ.get("SPHRAGIS") or ROOT.parent / "sphragis")

pytestmark = pytest.mark.skipif(
    not (SPHRAGIS / "datasets" / "results").is_dir() and not os.environ.get("CI"),
    reason="the deck's figures come from a sphragis checkout; set SPHRAGIS",
)


def check(tmp_path: Path, readings: str) -> subprocess.CompletedProcess:
    """`figures.py --check` on a copy of the deck whose readings.js is `readings`."""
    deck = tmp_path / "federated-agents-step-one"
    (deck / "data").mkdir(parents=True)
    (deck / "figures.py").write_text((DECK / "figures.py").read_text())
    (deck / "data" / "readings.js").write_text(readings)
    # figures.py loads the sibling Federated Agents deck's helpers.
    (tmp_path / "federated-agents").symlink_to(ROOT / "federated-agents")
    env = {**os.environ, "SPHRAGIS": str(SPHRAGIS), "SPHRAGIS_CORPUS": str(tmp_path / "no-corpus")}
    return subprocess.run(
        [sys.executable, str(deck / "figures.py"), "--check"], env=env, capture_output=True, text=True
    )


COMMITTED = (DECK / "data" / "readings.js").read_text()


def test_committed_example_passes_without_corpus(tmp_path):
    assert check(tmp_path, COMMITTED).returncode == 0


@pytest.mark.parametrize(
    ("old", "new", "why"),
    [
        ('"$0"', '"$1"', "code changed"),
        ('"day": "2025-03-14"', '"day": "2025-03-15"', "date changed"),
        ('"project": "starlingx/config"', '"project": "starlingx/other"', "project changed"),
        ('"window": "train"', '"window": "test"', "window changed"),
        ('"month": "Mar 2025"', '"month": "Apr 2025"', "month changed"),
    ],
)
def test_tampered_example_fails(tmp_path, old, new, why):
    assert COMMITTED.count(old) >= 1, why
    result = check(tmp_path, COMMITTED.replace(old, new, 1))
    assert result.returncode != 0, why


def test_flipped_mark_fails(tmp_path):
    # The boxed characters are part of what the slide shows; flipping one flag must be caught.
    tampered, n = re.subn(r'(\[\s*"\\"",\s*)true', r"\1false", COMMITTED, count=1)
    assert n == 1
    assert check(tmp_path, tampered).returncode != 0


def test_missing_day_is_named(tmp_path):
    tampered = re.sub(r'\s*"day": "[^"]*",', "", COMMITTED, count=1)
    result = check(tmp_path, tampered)
    assert result.returncode != 0
    assert "lacks day" in result.stderr
