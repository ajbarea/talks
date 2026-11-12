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


def figures_module(monkeypatch):
    import importlib.util

    monkeypatch.setenv("SPHRAGIS", str(SPHRAGIS))
    spec = importlib.util.spec_from_file_location("fa_step_one_figures", DECK / "figures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audit_is_the_reports_organization(monkeypatch):
    # The report quotes the human check on OpenStack's items alone; the slide must too.
    fig = figures_module(monkeypatch)
    values: dict = {}
    fig.label_audit(values)
    human = fig.load(fig.AUDIT_BY_ORG)["valid_shares"]["human"]
    assert (values["audit_checked"], values["audit_valid_human"]) == (human["n"], human["valid"])
    assert values["audit_org"] == "OpenStack"


@pytest.mark.parametrize("rater", ["human", "A", "B"])
def test_audit_mismatch_with_report_fails(monkeypatch, rater):
    fig = figures_module(monkeypatch)
    real = fig.load

    def load(name):
        data = real(name)
        if name == fig.AUDIT_BY_ORG:
            if rater == "human":
                data["valid_shares"]["human"]["valid"] += 1
            else:
                data["pairs"][f"human~{rater} valid_vs_rest"]["confusion"]["False"]["True"] += 1
        return data

    monkeypatch.setattr(fig, "load", load)
    with pytest.raises(SystemExit, match=f"{rater}'s .* differs from"):
        fig.label_audit({})


def test_audit_missing_rater_label_is_named(monkeypatch):
    fig = figures_module(monkeypatch)
    real = fig.load

    def load(name):
        data = real(name)
        if name == fig.AUDIT:
            key = next(k for k, v in data["labels"].items() if k.startswith("openstack:") and "human" in v)
            del data["labels"][key]["B"]
        return data

    monkeypatch.setattr(fig, "load", load)
    with pytest.raises(SystemExit, match="lacks a label from B"):
        fig.label_audit({})


def test_marks_add_no_spacing():
    # Spacing on the boxed characters reaches the PDF's text layer: copied code would gain spaces.
    # Every rule that styles the marks (phone overrides included) may set box spacing only to 0.
    css = re.sub(r"/\*.*?\*/", "", (DECK / "deck.css").read_text(), flags=re.S)
    rules = [body for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css) if ".ex-steps mark" in sel]
    assert rules, "no .ex-steps mark rule"
    spacing = re.compile(r"^(padding|margin|border(?!-radius)|letter-spacing|word-spacing)")
    for body in rules:
        for decl in filter(None, (d.strip() for d in body.split(";"))):
            prop, value = (x.strip() for x in decl.split(":", 1))
            if spacing.match(prop):
                assert value in ("0", "none"), decl
