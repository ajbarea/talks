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
    shutil.copy(DECK / "index.html", deck)
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
    assert "readings.js is stale" in result.stderr


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


def test_only_what_a_slide_binds_is_published() -> None:
    """readings.js is public: a reading no slide shows must not ride along in it."""
    module = _figures()
    values = {"shown": 1, "hidden": 2, "tree": {"a": {"x": 1, "y": 2}, "b": 3}}
    page = '<p data-value="readings.shown"></p><div data-source="readings.tree.a"></div>'
    assert module.published(values, module.bound_paths(page)) == {"shown": 1, "tree": {"a": {"x": 1, "y": 2}}}


#: Where sphragis states what each built stage of the pipeline slide does: (file, passage). A stage
#: drawn as built with no entry, or whose passage is gone, fails, so a new or renamed box needs a
#: source before it ships. Planned stages (dashed) are named apart.
PIPELINE_SOURCES = {
    "Collect": ("docs/dataset.md", "robots.txt or written terms"),
    "Accounts": ("sphragis/corpus/scrub.py", "_IDENTITY_KEYS"),
    "Pair": ("docs/dataset.md", "same hunk at the next patch set"),
    "Clean": ("docs/dataset.md", "a bot account wrote it"),
    "Drop copies": ("docs/dataset.md", "boilerplate"),
    "Split": ("sphragis/corpus/windows.py", "TEST_WINDOW_START"),
    "Split in two": ("sphragis/corpus/halves.py", "order_seed"),
    "Train each half": ("sphragis/experiment/model.py", "get_peft_model"),
    "Score the real fix": ("sphragis/experiment/cells.py", 'REGISTERED_METRIC = "logprob_per_token"'),
    "Compare": ("sphragis/experiment/partitions.py", "mean over partitions and seeds"),
}
PIPELINE_PLANNED = {"Read the sealed test", "Shared and private add-ons", "Try to break them"}


def test_every_built_pipeline_stage_has_a_sphragis_source() -> None:
    page = (DECK / "index.html").read_text()
    figure = page[page.index('<div class="figure pipeline">') : page.index('data-only="phone" viewBox="0 0 464 802"')]
    stages = re.findall(r'<rect class="(stage|stage run|next)"[^>]*/><text[^>]*class="b"[^>]*>([^<]+)</text>', figure)
    built = {title for kind, title in stages if kind != "next"}
    planned = {title for kind, title in stages if kind == "next"}
    assert built == set(PIPELINE_SOURCES), built ^ set(PIPELINE_SOURCES)
    assert planned == PIPELINE_PLANNED
    for title, (name, passage) in PIPELINE_SOURCES.items():
        assert passage in (SPHRAGIS / name).read_text(), f"{title}: {passage!r} is not in {name}"
