"""Controls for the site builder, which lays every talk out under one Pages site."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def site():
    spec = importlib.util.spec_from_file_location("talks_site", ROOT / "scripts" / "site.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _talk(root: Path, name: str, title: str = "A talk", description: str = "What it shows.") -> None:
    (root / name).mkdir(parents=True)
    (root / name / "index.html").write_text(
        f'<html><head><title>{title}</title><meta name="description" content="{description}"></head>'
        f"<body><svg><title>a figure</title></svg></body></html>"
    )
    (root / name / "figures.py").write_text("")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "vendor" / "reveal").mkdir(parents=True)
    (root / "vendor" / "reveal" / "reveal.js").write_text("")
    _talk(root, "beta-talk", "Beta &amp; more")
    _talk(root, "alpha-talk")
    (root / "scripts").mkdir()
    (root / "_site-old").mkdir()
    (root / ".deps" / "sphragis").mkdir(parents=True)
    (root / ".deps" / "sphragis" / "index.html").write_text("<title>not a talk</title>")
    return root


def test_every_talk_is_listed_and_nothing_else(site, repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert site.build(out, repo) == ["alpha-talk", "beta-talk"]
    index = (out / "index.html").read_text()
    assert index.index('href="alpha-talk/"') < index.index('href="beta-talk/"')
    # The page title, not an SVG's, and unescaped once, escaped once.
    assert "Beta &amp; more" in index and "a figure" not in index
    assert (out / "vendor" / "reveal" / "reveal.js").is_file()
    assert (out / "alpha-talk" / "index.html").is_file()
    assert not (out / "alpha-talk" / "figures.py").exists()


def test_a_talk_without_a_description_fails(site, repo: Path, tmp_path: Path) -> None:
    (repo / "alpha-talk" / "index.html").write_text("<html><head><title>T</title></head></html>")
    with pytest.raises(SystemExit, match="description"):
        site.build(tmp_path / "out", repo)


def test_it_rebuilds_its_own_site(site, repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    site.build(out, repo)
    (out / "stale.html").write_text("")
    site.build(out, repo)
    assert not (out / "stale.html").exists()


@pytest.mark.parametrize("target", ["elsewhere", ".", "alpha-talk/out", "vendor"])
def test_it_never_replaces_a_folder_it_did_not_build(site, repo: Path, tmp_path: Path, target: str) -> None:
    out = tmp_path / "elsewhere" if target == "elsewhere" else repo / target
    if target == "elsewhere":
        out.mkdir()
        (out / "keep.txt").write_text("mine")
    before = sorted(p.relative_to(out) for p in out.rglob("*")) if out.exists() else None
    with pytest.raises(SystemExit, match="refusing"):
        site.build(out, repo)
    assert (sorted(p.relative_to(out) for p in out.rglob("*")) if out.exists() else None) == before


def test_the_real_repository_has_talks(site) -> None:
    assert "federated-agents" in [t.name for t in site.talks()]
