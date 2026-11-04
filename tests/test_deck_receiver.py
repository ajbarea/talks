"""shared/deck.js in a speaker-view preview: no reload listener, no chapter rail (tests/deck_receiver.js)."""

import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_speaker_view_previews_neither_reload_nor_show_the_rail() -> None:
    run = subprocess.run(["node", str(ROOT / "tests" / "deck_receiver.js")], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr or run.stdout
