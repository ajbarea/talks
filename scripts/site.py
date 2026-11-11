#!/usr/bin/env python3
"""Lay out every talk as one site: each talk at /<folder>/, shared files at /vendor/ and /shared/, and an
index page listing the talks by their own <title> and description, with each talk's links.

    python scripts/site.py _site                       # build the site
    python scripts/site.py _site --exports _exports    # with each talk's .pptx, .pdf and preview
    python scripts/site.py --list                      # the talks, by folder

A talk is a top-level folder holding an index.html, and optionally a talk.json naming its links
({"links": {"code": URL, "docs": URL, "video": URL}}, each optional). With --exports, every talk
must have its `<folder>.pptx`, `<folder>.pdf` and `thumb.webp` there (scripts/exports.py writes
them), and the index offers the downloads; a `thumb-loop.webp` there plays when a preview is
hovered. Build scripts and caches stay behind.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOT_TALKS = {"vendor", "shared", "scripts", "tests"}
#: Marks a folder this script built, so it never replaces one it did not.
MARK = ".talks-site"
#: A talk folder's notes (README.md) and scripts stay in the repository.
SKIP = shutil.ignore_patterns("*.py", "__pycache__", "*.md", "talk.json")
#: The links a talk may name, in the order the index shows them, with their short labels and what
#: assistive technology reads after the label.
LINKS = {"code": ("Code", " on GitHub"), "docs": ("Docs", ""), "video": ("Video", "")}


def is_moved(d: pathlib.Path) -> bool:
    """A folder left behind when a talk was renamed: its index.html only redirects."""
    return 'http-equiv="refresh"' in (d / "index.html").read_text(errors="ignore")[:2000]


def candidates(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and d.name not in NOT_TALKS and not d.name.startswith((".", "_")) and (d / "index.html").is_file()
    )


def talks(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    return [d for d in candidates(root) if not is_moved(d)]


def moved(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    """Old talk addresses that redirect to the new one; published as-is, never listed."""
    return [d for d in candidates(root) if is_moved(d)]


def claim(out: pathlib.Path, mark: str, sources: list[pathlib.Path]) -> None:
    """Make `out` an empty folder this script owns, or refuse: it never replaces a folder it
    did not build, a file, or anything inside the files it copies."""
    if any(out.is_relative_to(source) for source in sources):
        raise SystemExit(f"refusing to build into {out}, inside the files it copies")
    if out.exists() and not out.is_dir():
        raise SystemExit(f"refusing to build into {out}, which is a file")
    if out.exists() and any(out.iterdir()):
        if not (out / mark).is_file():
            raise SystemExit(f"refusing to replace {out}: not empty, and not a folder this script built")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / mark).write_text("Built by the talks scripts, which replace this folder on every run.\n")


def meta(page: str, pattern: str, name: str, folder: str) -> str:
    match = re.search(pattern, page, re.S | re.I)
    if not match or not match.group(1).strip():
        raise SystemExit(f"{folder}/index.html has no {name}; the index lists talks by it")
    return html.unescape(" ".join(match.group(1).split()))


def entry(talk: pathlib.Path) -> tuple[str, str]:
    page = (talk / "index.html").read_text()
    title = meta(page, r"<head>.*?<title>(.*?)</title>", "<title>", talk.name)
    description = meta(page, r'<meta\s+name="description"\s+content="(.*?)"', "description", talk.name)
    return title, description


def links(talk: pathlib.Path) -> dict[str, str]:
    """The talk's links from its talk.json, checked: known kinds only, each an https URL."""
    path = talk / "talk.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{talk.name}/talk.json is not JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) - {"links"}:
        raise SystemExit(f'{talk.name}/talk.json holds only {{"links": {{...}}}}')
    named = data.get("links", {})
    if not isinstance(named, dict) or set(named) - set(LINKS):
        raise SystemExit(f"{talk.name}/talk.json links are limited to {', '.join(LINKS)}")
    for kind, url in named.items():
        if not isinstance(url, str) or not url.startswith("https://"):
            raise SystemExit(f"{talk.name}/talk.json {kind} must be an https:// URL, not {url!r}")
    return {kind: named[kind] for kind in LINKS if kind in named}


def size(path: pathlib.Path) -> str:
    mb = path.stat().st_size / 1_000_000
    return f"{mb:.1f} MB" if mb >= 1 else f"{max(1, round(mb * 1000))} KB"


#: The downloads each talk offers, by file type, in the order the index shows them, with their labels.
DOWNLOADS = {"pptx": "PowerPoint", "pdf": "PDF"}
#: The index page's template, styles and script, joined into one file at build time.
PAGE = pathlib.Path(__file__).with_name("index")

ICONS = {
    "download": '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    "code": '<path d="M9 7 4 12l5 5M15 7l5 5-5 5"/>',
    "docs": '<path d="M6 3h9l4 4v14H6zM14 3v5h5M9 12h7M9 16h7"/>',
    "video": '<path d="M7 5l12 7-12 7z"/>',
    "open": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}


def icon(kind: str, px: int = 16) -> str:
    return (
        f'<svg aria-hidden="true" viewBox="0 0 24 24" width="{px}" height="{px}" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[kind]}</svg>'
    )


def item(
    name: str,
    title: str,
    description: str,
    named: dict[str, str],
    sizes: dict[str, str] | None,
    thumb: bool,
    loop: bool = False,
    centered: bool = False,
) -> str:
    """One talk: its preview and, beside or under it, its title, description, one primary action
    and a row of small labelled downloads and links. The page script turns the list into a cover flow."""
    t, d = html.escape(title), html.escape(description)
    loop_attr = f' data-loop="{name}/thumb-loop.webp"' if loop else ""
    # Every preview loads at once anyway: its reflection draws from the same file.
    priority = ' fetchpriority="high"' if centered else ""
    picture = (
        f'<a class="cover" href="{name}/" tabindex="-1" aria-hidden="true" draggable="false" '
        f"style=\"--thumb: url('{name}/thumb.webp')\">"
        f'<img src="{name}/thumb.webp" alt="" width="960" height="540" decoding="async" draggable="false"'
        f"{priority}{loop_attr}></a>"
        if thumb
        else f'<a class="cover blank" href="{name}/" tabindex="-1" aria-hidden="true" draggable="false">'
        f"<span>{t}</span></a>"
    )
    chips = [
        f'<li><a class="chip" href="{name}/{name}.{ext}" download>{icon("download")}'
        f'<span class="sr-only">Download </span>{label} <span class="size">{sizes[ext]}</span></a></li>'
        for ext, label in (DOWNLOADS.items() if sizes else ())
    ]
    chips += [
        f'<li><a class="chip" href="{html.escape(url)}">{icon(kind)}{LINKS[kind][0]}'
        + (f'<span class="sr-only">{LINKS[kind][1]}</span>' if LINKS[kind][1] else "")
        + "</a></li>"
        for kind, url in named.items()
    ]
    more = f'\n          <ul class="chips">{"".join(chips)}</ul>' if chips else ""
    return f"""      <div class="talk" id="talk-{name}" data-name="{name}">
        {picture}
        <div class="about">
          <h2 id="title-{name}"><a href="{name}/">{t}</a></h2>
          <p class="description">{d}</p>
          <a class="open" href="{name}/">Open the deck{icon("open", 18)}</a>{more}
        </div>
      </div>"""


def page(items: list[str]) -> str:
    """The index page: the template with its styles and script inlined, so it paints in one request."""
    template = (PAGE / "index.html").read_text()
    css, js = (PAGE / "index.css").read_text(), (PAGE / "index.js").read_text()
    for name, part, text in (("index.css", "style", css), ("index.js", "script", js)):
        if f"</{part}" in text.lower():
            raise SystemExit(f"scripts/index/{name} must not close its own <{part}>")
    return (
        template.replace("/* index.css */", css.strip())
        .replace("/* index.js */", js.strip())
        .replace("<!-- talks -->", "\n".join(items))
    )


def build(out: pathlib.Path, root: pathlib.Path = ROOT, exports: pathlib.Path | None = None) -> list[str]:
    found = talks(root)
    if not found:
        raise SystemExit(f"no talks under {root}: a talk is a folder holding an index.html")
    for talk in found:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", talk.name):
            raise SystemExit(f"{talk.name}: name a talk's folder in lowercase words joined by hyphens")
        symlinks = [p for p in talk.rglob("*") if p.is_symlink()]
        if symlinks:
            raise SystemExit(f"{talk.name} holds a symlink, which would publish what it points to: {symlinks[0]}")
    if exports is not None:
        for talk in found:
            for name in (*(f"{talk.name}.{ext}" for ext in DOWNLOADS), "thumb.webp"):
                if not (exports / talk.name / name).is_file():
                    raise SystemExit(f"no {exports / talk.name / name}; run scripts/exports.py first")
    rows = [(talk, *entry(talk), links(talk)) for talk in found]
    sources = [*found, *moved(root), root / "vendor", root / "shared"]
    claim(out, MARK, [*sources, *([exports] if exports is not None else [])])
    for old in moved(root):  # keep old links working: copy the redirect page only
        (out / old.name).mkdir(parents=True)
        shutil.copy2(old / "index.html", out / old.name / "index.html")
    for shared in ("vendor", "shared"):
        shutil.copytree(root / shared, out / shared)
    items = []
    for talk, title, description, named in rows:
        shutil.copytree(talk, out / talk.name, ignore=SKIP)
        sizes = None
        loop = exports is not None and (exports / talk.name / "thumb-loop.webp").is_file()
        if exports is not None:
            files = [f"{talk.name}.{ext}" for ext in DOWNLOADS]
            for name in (*files, "thumb.webp"):
                shutil.copy2(exports / talk.name / name, out / talk.name / name)
            sizes = {ext: size(out / talk.name / f) for ext, f in zip(DOWNLOADS, files, strict=True)}
            if loop:
                shutil.copy2(exports / talk.name / "thumb-loop.webp", out / talk.name / "thumb-loop.webp")
        centered = len(items) == (len(rows) - 1) // 2  # the talk the cover flow opens on
        items.append(item(talk.name, title, description, named, sizes, exports is not None, loop, centered))
    (out / "index.html").write_text(page(items))
    return [t.name for t in found]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out", nargs="?", type=pathlib.Path, help="the folder to build the site in")
    parser.add_argument("--exports", type=pathlib.Path, help="each talk's .pptx, .pdf and preview, from exports.py")
    parser.add_argument("--list", action="store_true", help="print the talks, by folder")
    args = parser.parse_args()
    if args.list:
        print(" ".join(t.name for t in talks()))
        return 0
    if args.out is None:
        parser.error("give the folder to build the site in, or --list")
    out = args.out.resolve()
    exports = args.exports.resolve() if args.exports else None
    for name in build(out, exports=exports):
        print(f"talk: {name}/")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
