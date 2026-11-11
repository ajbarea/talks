"""Controls for the site builder, which lays every talk out under one Pages site."""

from __future__ import annotations

import importlib.util
import json
import re
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


def test_a_talk_folders_markdown_is_not_published(site, repo: Path, tmp_path: Path) -> None:
    (repo / "alpha-talk" / "README.md").write_text("notes")
    (repo / "alpha-talk" / "video-script.md").write_text("a script")
    out = tmp_path / "out"
    site.build(out, repo)
    assert (out / "alpha-talk" / "index.html").is_file()
    assert not list((out / "alpha-talk").rglob("*.md"))


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
    assert 'href="alpha-talk/alpha-talk.pptx" download' in alpha and "2.5 MB" in alpha
    assert 'href="alpha-talk/alpha-talk.pdf" download' in alpha and "350 KB" in alpha
    assert '<span class="sr-only">Download </span>PDF' in alpha
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
    assert exports.export(out, stub, repo, loops=False) == ["alpha-talk", "beta-talk"]
    from PIL import Image

    for name in ("alpha-talk", "beta-talk"):
        assert (out / name / f"{name}.pptx").read_bytes() == b"pptx"
        assert (out / name / f"{name}.pdf").read_bytes() == b"pdf"
        with Image.open(out / name / "thumb.webp") as thumb:
            assert thumb.size == exports.THUMB
    with pytest.raises(SystemExit, match="refusing"):
        exports.export(repo, stub, repo, loops=False)


def test_every_talk_loads_the_shared_deck_and_keeps_only_its_own_styles(site) -> None:
    """The shared files are the one copy: a talk holds no deck.js and no copy of the base styles."""
    for talk in site.talks():
        page = (talk / "index.html").read_text()
        assert page.index("../shared/deck.css") < page.index('href="deck.css"')
        assert '<script src="../shared/deck.js"></script>' in page
        assert not (talk / "deck.js").exists()
        assert ".reveal .slides section {" not in (talk / "deck.css").read_text()


def test_the_chapter_rail_never_wraps_its_pills() -> None:
    """A wrapping pill becomes a tall circle that covers the slide on a landscape phone."""
    css = (ROOT / "shared" / "deck.css").read_text()
    pill = css[css.index(".rail button {") :].split("}")[0]
    assert "white-space: nowrap" in pill and "flex: none" in pill
    row = css[css.index(".rail {") :].split("}")[0]
    assert "max-width" in row and "overflow-x: auto" in row


def test_a_preview_loop_is_offered_only_when_exported(site, repo: Path, tmp_path: Path) -> None:
    exports = _exports(tmp_path, "alpha-talk", "beta-talk")
    (exports / "alpha-talk" / "thumb-loop.webp").write_bytes(b"loop")
    out = tmp_path / "out"
    site.build(out, repo, exports)
    index = (out / "index.html").read_text()
    assert 'data-loop="alpha-talk/thumb-loop.webp"' in index and "beta-talk/thumb-loop.webp" not in index
    assert (out / "alpha-talk" / "thumb-loop.webp").is_file()
    assert not (out / "beta-talk" / "thumb-loop.webp").exists()


def test_every_talk_loads_the_motion_files_after_the_deck(site) -> None:
    for talk in site.talks():
        page = (talk / "index.html").read_text()
        assert page.index("../shared/deck.css") < page.index("../shared/motion.css") < page.index('href="deck.css"')
        assert page.index("../shared/deck.js") < page.index("../shared/motion.js")


def test_the_motion_resting_style_is_the_finished_one() -> None:
    """Exports, phones and print never turn motion on, so no rule outside html.m-live may hide or move a figure."""
    css = (ROOT / "shared" / "motion.css").read_text()
    for rule in css.split("}"):
        selector = rule.split("{")[0].strip()
        if selector.startswith(("html.m-live", "@", "from", "to", "0%", "12%", "100%", "[data-motion=")):
            continue
        body = rule.split("{")[-1]
        assert "transform" not in body or "keyframes" in rule, selector


def test_every_talk_loads_the_tip_files_after_the_deck(site) -> None:
    for talk in site.talks():
        page = (talk / "index.html").read_text()
        assert page.index("../shared/deck.css") < page.index("../shared/tip.css") < page.index('href="deck.css"')
        assert page.index("../shared/deck.js") < page.index("../shared/tip.js")


def test_a_dot_is_described_by_a_tip_never_by_a_native_title() -> None:
    """A svg title or title attribute on a dot would show beside the tip."""
    deck = (ROOT / "shared" / "deck.js").read_text()
    assert 'svg("title"' not in deck and "title:" not in deck.replace("data-tip-title", "")
    assert deck.count("...tip(w)") == 3


def test_the_tip_never_reaches_an_export() -> None:
    assert ".tip, .tip-anchor" in (ROOT / "scripts" / "exports.py").read_text()
    assert "@media print" in (ROOT / "shared" / "tip.css").read_text()
    assert "print-pdf" in (ROOT / "shared" / "tip.js").read_text()


def test_a_moved_talk_is_published_as_a_redirect_and_not_listed(site, tmp_path):
    out = tmp_path / "site"
    site.build(out)
    moved = [d.name for d in site.moved()]
    assert "claude-duet" in moved and "claude-duet" not in [t.name for t in site.talks()]
    page = (out / "claude-duet" / "index.html").read_text()
    assert 'http-equiv="refresh"' in page and "../claude-tooling/" in page
    assert "claude-duet/" not in (out / "index.html").read_text()


def _built(site, repo: Path, tmp_path: Path, **links: str) -> str:
    if links:
        (repo / "alpha-talk" / "talk.json").write_text(json.dumps({"links": links}))
    exports = _exports(tmp_path, "alpha-talk", "beta-talk")
    (exports / "alpha-talk" / "thumb-loop.webp").write_bytes(b"loop")
    out = tmp_path / "out"
    site.build(out, repo, exports)
    return (out / "index.html").read_text()


def _talks(index: str) -> dict[str, str]:
    """Each talk's markup, by folder name."""
    found = re.findall(r'<div class="talk" id="talk-([a-z0-9-]+)".*?\n      </div>', index, re.S)
    return {
        name: re.search(rf'<div class="talk" id="talk-{name}".*?\n      </div>', index, re.S).group(0) for name in found
    }


def test_every_talk_offers_its_deck_downloads_and_links_once(site, repo: Path, tmp_path: Path) -> None:
    index = _built(site, repo, tmp_path, code="https://github.com/a/b", video="https://youtu.be/x")
    talks = _talks(index)
    assert list(talks) == ["alpha-talk", "beta-talk"]
    for name, talk in talks.items():
        assert talk.count(f'<a class="open" href="{name}/">Open the deck') == 1
        assert f'<h2 id="title-{name}"><a href="{name}/">' in talk
        for ext, label in (("pptx", "PowerPoint"), ("pdf", "PDF")):
            assert f'href="{name}/{name}.{ext}" download>' in talk and f"Download </span>{label} " in talk
    alpha = talks["alpha-talk"]
    assert alpha.index("github.com/a/b") < alpha.index("youtu.be/x")
    assert 'Code<span class="sr-only"> on GitHub</span>' in alpha and ">Video</a>" in alpha
    assert "github.com" not in talks["beta-talk"]


def test_the_page_names_the_carousel_and_its_controls(site, repo: Path, tmp_path: Path) -> None:
    index = _built(site, repo, tmp_path)
    assert '<section class="talks" id="talks" aria-label="Talks">' in index
    assert '<button class="step prev" type="button" aria-label="Previous talk" hidden>' in index
    assert '<button class="step next" type="button" aria-label="Next talk" hidden>' in index
    assert '<p class="sr-only" aria-live="polite" aria-atomic="true"></p>' in index
    # The label never repeats "carousel", which the role description already says.
    assert 'aria-label="Talks carousel"' not in index


def test_without_script_every_talk_is_a_plain_card(site, repo: Path, tmp_path: Path) -> None:
    """The carousel roles, hidden talks and the stage controls exist only once the script runs."""
    index = _built(site, repo, tmp_path)
    body = index[index.index("<body>") : index.index("<script>\n")]
    assert "aria-roledescription" not in body and "inert" not in body
    assert '<html lang="en">' in index and 'classList.add("flow")' in index
    for talk in _talks(index).values():
        about = talk[talk.index('<div class="about">') :].replace('<svg aria-hidden="true"', "<svg")
        assert "hidden" not in about and "tabindex" not in about
        # The preview repeats the deck link, so it stays out of the tab order and the accessibility tree.
        cover = talk[: talk.index('<div class="about">')]
        assert 'tabindex="-1" aria-hidden="true"' in cover


def test_the_script_wires_the_carousel_pattern() -> None:
    js = (ROOT / "scripts" / "index" / "index.js").read_text()
    for wiring in (
        '"aria-roledescription", "carousel"',
        '"role", "group"',
        '"aria-roledescription", "slide"',
        "aria-labelledby",
        ".inert = !here",
        '"aria-hidden", "true"',
        "aria-disabled",
        "scrollend",
    ):
        assert wiring in js, wiring


def test_the_centered_talk_alone_loads_eagerly_and_loops(site, repo: Path, tmp_path: Path) -> None:
    for name in ("gamma-talk", "delta-talk"):
        _talk(repo, name)
    exports = _exports(tmp_path, "alpha-talk", "beta-talk", "delta-talk", "gamma-talk")
    out = tmp_path / "out"
    site.build(out, repo, exports)
    talks = _talks((out / "index.html").read_text())
    middle = list(talks)[(len(talks) - 1) // 2]
    assert [n for n, t in talks.items() if 'fetchpriority="high"' in t] == [middle]
    assert all('loading="lazy"' in t for n, t in talks.items() if n != middle)
    assert all(f"--thumb: url('{n}/thumb.webp')" in t for n, t in talks.items())


def test_the_page_inlines_its_styles_and_script(site, repo: Path, tmp_path: Path) -> None:
    index = _built(site, repo, tmp_path)
    assert "/* index.css */" not in index and "/* index.js */" not in index and "<!-- talks -->" not in index
    assert "@keyframes flow-tilt" in index and "animation-timeline: --talk" in index
    assert "prefers-reduced-motion: reduce" in index and "prefers-color-scheme: dark" in index


def test_the_cover_flow_animates_only_transform_and_opacity() -> None:
    """Each per-frame change runs on the compositor; z-index orders the covers and changes only by step."""
    css = (ROOT / "scripts" / "index" / "index.css").read_text()
    names = re.findall(r"@keyframes (flow-[a-z]+) \{", css)
    assert {"flow-z", "flow-tilt", "flow-shade", "flow-about", "flow-flat"} <= set(names)
    for name in names:
        start = css.index("{", css.index(f"@keyframes {name} {{")) + 1
        depth, end = 1, start
        while depth:
            depth += {"{": 1, "}": -1}.get(css[end], 0)
            end += 1
        props = set(re.findall(r"([a-z-]+):", css[start:end]))
        assert props <= ({"z-index"} if name == "flow-z" else {"transform", "opacity"}), name
