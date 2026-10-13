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
    (root / "shared").mkdir()
    (root / "shared" / "deck.js").write_text("")
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
    assert (out / "shared" / "deck.js").is_file()
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


def test_a_talk_holding_a_symlink_fails(site, repo: Path, tmp_path: Path) -> None:
    (repo / "alpha-talk" / "deps").symlink_to(repo / ".deps")
    with pytest.raises(SystemExit, match="symlink"):
        site.build(tmp_path / "out", repo)


def test_a_file_is_not_an_output_folder(site, repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "file.txt"
    out.write_text("mine")
    with pytest.raises(SystemExit, match="refusing"):
        site.build(out, repo)
    assert out.read_text() == "mine"


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


def _exports(root: Path, *names: str) -> Path:
    out = root / "exports"
    for name in names:
        (out / name).mkdir(parents=True)
        (out / name / f"{name}.pptx").write_bytes(b"x" * 2_500_000)
        (out / name / f"{name}.pdf").write_bytes(b"x" * 350_000)
        (out / name / "thumb.webp").write_bytes(b"webp")
    return out


def test_links_and_downloads_appear_for_each_talk(site, repo: Path, tmp_path: Path) -> None:
    (repo / "alpha-talk" / "talk.json").write_text(
        '{"links": {"video": "https://youtu.be/x", "code": "https://github.com/a/b"}}'
    )
    out = tmp_path / "out"
    site.build(out, repo, _exports(tmp_path, "alpha-talk", "beta-talk"))
    index = (out / "index.html").read_text()
    alpha = index[index.index('href="alpha-talk/"') : index.index('href="beta-talk/"')]
    assert 'href="alpha-talk/alpha-talk.pptx" download' in alpha and "(2.5 MB)" in alpha
    assert 'href="alpha-talk/alpha-talk.pdf" download' in alpha and "Download PDF" in alpha and "(350 KB)" in alpha
    assert alpha.index(".pptx") < alpha.index(".pdf")
    # In the order the index defines, whatever order talk.json lists them.
    assert alpha.index("https://github.com/a/b") < alpha.index("https://youtu.be/x")
    for name in ("alpha-talk.pptx", "alpha-talk.pdf", "thumb.webp"):
        assert (out / "alpha-talk" / name).is_file()
    assert not (out / "alpha-talk" / "talk.json").exists()


def test_without_exports_the_index_offers_no_download(site, repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    site.build(out, repo)
    index = (out / "index.html").read_text()
    assert ".pptx" not in index and ".pdf" not in index


def test_a_missing_export_fails_before_anything_is_written(site, repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match="exports.py"):
        site.build(out, repo, _exports(tmp_path, "alpha-talk"))
    assert not out.exists()


def test_a_missing_pdf_fails_too(site, repo: Path, tmp_path: Path) -> None:
    exports = _exports(tmp_path, "alpha-talk", "beta-talk")
    (exports / "beta-talk" / "beta-talk.pdf").unlink()
    with pytest.raises(SystemExit, match=r"beta-talk\.pdf"):
        site.build(tmp_path / "out", repo, exports)


@pytest.mark.parametrize(
    "text",
    [
        "not json",
        '{"links": {"slides": "https://x"}}',
        '{"links": {"code": "http://insecure"}}',
        '{"links": {"code": "javascript:alert(1)"}}',
        '{"title": "x"}',
        '["https://x"]',
    ],
)
def test_a_talk_json_outside_the_shape_fails(site, repo: Path, tmp_path: Path, text: str) -> None:
    (repo / "alpha-talk" / "talk.json").write_text(text)
    with pytest.raises(SystemExit, match="talk.json"):
        site.build(tmp_path / "out", repo)


def test_a_talk_folder_is_named_in_lowercase_hyphenated_words(site, repo: Path, tmp_path: Path) -> None:
    _talk(repo, 'Bad"Name')
    with pytest.raises(SystemExit, match="lowercase"):
        site.build(tmp_path / "out", repo)


def test_the_site_never_replaces_the_exports_it_reads(site, repo: Path, tmp_path: Path) -> None:
    exports = _exports(tmp_path, "alpha-talk", "beta-talk")
    with pytest.raises(SystemExit, match="refusing"):
        site.build(exports, repo, exports)
    assert (exports / "alpha-talk" / "alpha-talk.pptx").is_file()


STUB = """import pathlib, sys
from PIL import Image
args = sys.argv[1:]
assert args[0] in ("pptx", "pdf")
pathlib.Path(args[2]).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(args[2]).write_bytes(args[0].encode())
if args[0] == "pptx":
    images = pathlib.Path(args[args.index("--images") + 1])
    images.mkdir(parents=True)
    Image.new("RGB", (1920, 1080), "navy").save(images / "slide-01.png")
"""


def test_exports_write_each_talks_pptx_and_preview(repo: Path, tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("talks_exports", ROOT / "scripts" / "exports.py")
    assert spec and spec.loader
    exports = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exports)
    stub = tmp_path / "slides.py"
    stub.write_text(STUB)
    out = tmp_path / "exports"
    assert exports.export(out, stub, repo) == ["alpha-talk", "beta-talk"]
    from PIL import Image

    for name in ("alpha-talk", "beta-talk"):
        assert (out / name / f"{name}.pptx").read_bytes() == b"pptx"
        assert (out / name / f"{name}.pdf").read_bytes() == b"pdf"
        with Image.open(out / name / "thumb.webp") as thumb:
            assert thumb.size == exports.THUMB
    with pytest.raises(SystemExit, match="refusing"):
        exports.export(repo, stub, repo)


def test_every_talk_loads_the_shared_deck_and_keeps_only_its_own_styles(site) -> None:
    """The shared files are the one copy: a talk holds no deck.js and no copy of the base styles."""
    for talk in site.talks():
        page = (talk / "index.html").read_text()
        assert page.index("../shared/deck.css") < page.index('href="deck.css"')
        assert '<script src="../shared/deck.js"></script>' in page
        assert not (talk / "deck.js").exists()
        assert ".reveal .slides section {" not in (talk / "deck.css").read_text()
