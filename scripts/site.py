#!/usr/bin/env python3
"""Lay out every talk as one site: each talk at /<folder>/, shared files at /vendor/, and an
index page listing the talks by their own <title> and description.

    python scripts/site.py _site      # build the site
    python scripts/site.py --list     # the talks, by folder

A talk is a top-level folder holding an index.html. Build scripts and caches stay behind.
"""

from __future__ import annotations

import html
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOT_TALKS = {"vendor", "scripts", "tests"}
#: Marks a folder this script built, so it never replaces one it did not.
MARK = ".talks-site"
SKIP = shutil.ignore_patterns("*.py", "__pycache__", "README.md")


def talks(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and d.name not in NOT_TALKS and not d.name.startswith((".", "_")) and (d / "index.html").is_file()
    )


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


INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Talks · AJ Barea</title>
  <meta name="description" content="Research talks by AJ Barea, as web decks.">
  <style>
    body {{ margin: 0; background: #f8f7f3; color: #1d1d1b; font: 18px/1.5 system-ui, sans-serif; }}
    main {{ max-width: 46rem; margin: 0 auto; padding: 3rem 1.25rem; }}
    h1 {{ font-size: 2rem; margin: 0 0 1.5rem; }}
    ul {{ list-style: none; padding: 0; margin: 0; }}
    li {{ border-top: 1px solid #c9c6bc; padding: 1rem 0; }}
    a {{ color: #1a3a8f; font-weight: 700; font-size: 1.2rem; }}
    p {{ margin: .25rem 0 0; }}
    footer {{ margin-top: 2.5rem; color: #4a4943; font-size: .9rem; }}
    footer a {{ font-size: inherit; font-weight: 400; }}
  </style>
</head>
<body>
<main>
  <h1>Talks</h1>
  <ul>
{items}
  </ul>
  <footer>Open a talk and press S for the speaker notes. Source:
    <a href="https://github.com/ajbarea/talks">github.com/ajbarea/talks</a></footer>
</main>
</body>
</html>
"""


def build(out: pathlib.Path, root: pathlib.Path = ROOT) -> list[str]:
    found = talks(root)
    if not found:
        raise SystemExit(f"no talks under {root}: a talk is a folder holding an index.html")
    if any(out.is_relative_to(source) for source in [*found, root / "vendor"]):
        raise SystemExit(f"refusing to build into {out}, inside the files it copies")
    if out.exists() and not out.is_dir():
        raise SystemExit(f"refusing to build into {out}, which is a file")
    if out.exists() and any(out.iterdir()):
        if not (out / MARK).is_file():
            raise SystemExit(f"refusing to replace {out}: not empty, and not a site this script built")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / MARK).write_text("Built by scripts/site.py, which replaces this folder on every run.\n")
    shutil.copytree(root / "vendor", out / "vendor")
    items = []
    for talk in found:
        links = [p for p in talk.rglob("*") if p.is_symlink()]
        if links:
            raise SystemExit(f"{talk.name} holds a symlink, which would publish what it points to: {links[0]}")
        title, description = entry(talk)
        shutil.copytree(talk, out / talk.name, ignore=SKIP)
        items.append(f'    <li><a href="{talk.name}/">{html.escape(title)}</a><p>{html.escape(description)}</p></li>')
    (out / "index.html").write_text(INDEX.format(items="\n".join(items)))
    return [t.name for t in found]


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: site.py <out-dir> | --list")
    if sys.argv[1] == "--list":
        print(" ".join(t.name for t in talks()))
        return 0
    out = pathlib.Path(sys.argv[1]).resolve()
    for name in build(out):
        print(f"talk: {name}/")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
