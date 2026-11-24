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
#: The links a talk may name, in the order the index shows them, with their labels.
# WCAG G201: the name says the link leaves in a new tab, after the visible label.
NEW_TAB = ", opens in a new tab"
LINKS = {"code": "Code on GitHub", "docs": "Docs site", "video": "Video"}


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
    if not isinstance(data, dict) or set(data) - {"links", "close"}:
        raise SystemExit(f'{talk.name}/talk.json holds only {{"links": {{...}}, "close": {{...}}}}')
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
    "pptx": (
        '<path d="M4 3h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM2 17h20M10 21h4M12 17v4"/>'
        '<path d="M9 13V7h3.5a1.5 1.5 0 0 1 0 3H9"/>'
    ),
    "pdf": ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 13h6M9 17h4"/>'),
    "code": (
        '<path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 '
        "0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-"
        ".908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647"
        ".35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-"
        ".446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 "
        "1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 "
        "3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58"
        '.688.482A10.019 10.019 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/>'
    ),
    "docs": (
        '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10M6 10h10M6 14h6"/>'
    ),
    "video": '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m10 9 5 3-5 3V9z"/>',
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
    has_cover: bool = False,
) -> str:
    """One talk: its preview and, beside or under it, its title, description,
    and a row of clean icon action buttons for downloads and links. The cover itself is the primary way in."""
    t, d = html.escape(title), html.escape(description)
    loop_attr = f' data-loop="{name}/thumb-loop.webp"' if loop else ""
    priority = ' fetchpriority="high"' if centered else ""

    if thumb:
        img_src = f"{name}/thumb.webp"
    elif has_cover:
        img_src = f"{name}/cover.svg"
    else:
        img_src = ""

    picture = (
        f'<a class="cover" href="{name}/" tabindex="-1" aria-hidden="true" draggable="false" '
        f'style="--thumb: url(\'{img_src}\')" aria-label="Open {t}">'
        f'<img src="{img_src}" alt="" width="960" height="540" decoding="async" draggable="false"'
        f"{priority}{loop_attr}></a>"
        if img_src
        else (
            f'<a class="cover blank" href="{name}/" tabindex="-1" aria-hidden="true" draggable="false" '
            f'aria-label="Open {t}"><span>{t}</span></a>'
        )
    )
    chips = [
        f'<li><a class="chip action-btn" href="{name}/{name}.{ext}" download '
        f'aria-label="Download {label}, {sizes[ext]}" data-tooltip="{label}, {sizes[ext]}">{icon(ext, 20)}'
        f'<span class="sr-only">Download </span><span class="sr-only">{label} </span>'
        f'<span class="sr-only size">{sizes[ext]}</span></a></li>'
        for ext, label in (DOWNLOADS.items() if sizes else ())
    ]
    chips += [
        f'<li><a class="chip action-btn" href="{html.escape(url)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{LINKS[kind]}{NEW_TAB}" data-tooltip="{LINKS[kind]}{NEW_TAB}">{icon(kind, 20)}'
        f'<span class="sr-only">{LINKS[kind]}{NEW_TAB}</span></a></li>'
        for kind, url in named.items()
    ]
    more = f'<ul class="chips">{"".join(chips)}</ul>' if chips else ""
    return f"""      <div class="talk" id="talk-{name}" data-name="{name}">
        {picture}
        <div class="about">
          <h2><a href="{name}/">{t}</a></h2>
          <p class="description">{d}</p>
          <div class="actions">{more}</div>
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
        has_cover = (talk / "cover.svg").is_file()
        items.append(item(talk.name, title, description, named, sizes, exports is not None, loop, centered, has_cover))
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
