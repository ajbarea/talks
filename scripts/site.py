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
LINKS = {"code": "Code on GitHub", "docs": "Documentation", "video": "Watch the video"}


def talks(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir() and d.name not in NOT_TALKS and not d.name.startswith((".", "_")) and (d / "index.html").is_file()
    )


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


#: The downloads each talk offers, by file type, in the order the index shows them.
DOWNLOADS = {"pptx": "Download for PowerPoint", "pdf": "Download PDF"}

ICONS = {
    "code": '<path d="M9 7 4 12l5 5M15 7l5 5-5 5"/>',
    "docs": '<path d="M6 3h9l4 4v14H6zM14 3v5h5M9 12h7M9 16h7"/>',
    "video": '<path d="M5 4l14 8-14 8z"/>',
}


def icon(kind: str) -> str:
    return (
        '<svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linejoin="round">{ICONS[kind]}</svg>'
    )


def item(
    name: str,
    title: str,
    description: str,
    named: dict[str, str],
    sizes: dict[str, str] | None,
    thumb: bool,
    loop: bool = False,
) -> str:
    t, d = html.escape(title), html.escape(description)
    loop_attr = f' data-loop="{name}/thumb-loop.webp"' if loop else ""
    picture = (
        f'<a class="shot" href="{name}/" tabindex="-1" aria-hidden="true">'
        f'<img src="{name}/thumb.webp" alt="" width="960" height="540" loading="lazy"{loop_attr}></a>'
        if thumb
        else f'<a class="shot blank" href="{name}/" tabindex="-1" aria-hidden="true"><span>{t}</span></a>'
    )
    actions = [f'<a class="button primary" href="{name}/">Open the talk</a>']
    for ext, label in DOWNLOADS.items() if sizes else ():
        actions.append(
            f'<a class="button" href="{name}/{name}.{ext}" download>{label} '
            f'<span class="note">({sizes[ext]})</span></a>'
        )
    more = "".join(
        f'<li><a href="{html.escape(url)}">{icon(kind)}{LINKS[kind]}</a></li>' for kind, url in named.items()
    )
    return f"""    <article class="talk">
      {picture}
      <div class="about">
        <h2><a href="{name}/">{t}</a></h2>
        <p>{d}</p>
        <p class="actions">{"".join(actions)}</p>
        {f'<ul class="links">{more}</ul>' if more else ""}
      </div>
    </article>"""


INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Talks by AJ Barea</title>
  <meta name="description"
    content="Research talks by AJ Barea: open one in your browser, or download it as PowerPoint or PDF.">
  <meta property="og:title" content="Talks by AJ Barea">
  <meta property="og:description"
    content="Research talks: open one in your browser, or download it as PowerPoint or PDF.">
  <style>
    :root {{
      --paper: #faf8f3; --ink: #1a1a1a; --muted: #44403c; --label: #1e3a8a;
      --line: #d6d3d1; --band: #f1efe9; --mark: #0072b2; --ours: #d55e00;
      --sans: system-ui, "Segoe UI", Calibri, Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font: 1.0625rem/1.55 var(--sans); }}
    main {{ max-width: 108rem; margin: 0 auto; padding: 4rem 2rem 3rem; }}
    header {{ max-width: 44rem; margin-bottom: 3rem; }}
    .talks {{ display: block; }}
    h1 {{ font-size: clamp(2.5rem, 6vw, 4rem); line-height: 1; letter-spacing: -0.02em; margin: 0 0 1rem;
      font-weight: 750; }}
    header p {{ margin: 0; color: var(--muted); font-size: 1.2rem; }}
    header a {{ color: var(--label); }}
    .talk {{ display: grid; grid-template-columns: minmax(0, 11fr) minmax(0, 9fr); gap: 2.5rem;
      align-items: center; padding: 2.5rem 0; border-top: 1px solid var(--line); }}
    .shot {{ display: block; border-radius: 6px; overflow: hidden; outline: 1px solid var(--line);
      aspect-ratio: 16 / 9; background: var(--band); }}
    .shot img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    @media (prefers-reduced-motion: no-preference) {{
      @view-transition {{ navigation: auto; }}
      @keyframes enter {{ from {{ opacity: 0; transform: translateY(14px); }} }}
      header h1, header p, .talk {{ animation: enter 0.6s cubic-bezier(0.22, 0.8, 0.3, 1) backwards; }}
      header p {{ animation-delay: 0.1s; }}
      .talk:nth-of-type(1) {{ animation-delay: 0.25s; }}
      .talk:nth-of-type(2) {{ animation-delay: 0.4s; }}
      .talk:nth-of-type(n + 3) {{ animation-delay: 0.55s; }}
      .shot {{ transition: transform 0.35s cubic-bezier(0.22, 0.8, 0.3, 1), box-shadow 0.35s; }}
      .shot img {{ transition: transform 0.6s cubic-bezier(0.22, 0.8, 0.3, 1); }}
      .talk:hover .shot, .talk:focus-within .shot {{
        transform: translateY(-6px); box-shadow: 0 20px 36px -22px rgba(30, 58, 138, 0.55); }}
      .talk:hover .shot img, .talk:focus-within .shot img {{ transform: scale(1.025); }}
    }}
    .shot.blank {{ display: grid; place-items: center; padding: 2rem; font-size: 1.6rem; font-weight: 700; }}
    h2 {{ font-size: 1.75rem; line-height: 1.15; margin: 0 0 0.6rem; font-weight: 700; }}
    h2 a {{ color: inherit; text-decoration: none; }}
    h2 a:hover {{ text-decoration: underline; text-decoration-thickness: 2px; }}
    .about > p {{ margin: 0 0 1.4rem; color: var(--muted); max-width: 36rem; }}
    .actions {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }}
    .actions .primary {{ grid-column: 1 / -1; }}
    .button {{ display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: center; text-align: center;
      gap: 0 0.5rem; padding: 0.7rem 1.1rem;
      border-radius: 6px; border: 2px solid var(--label); color: var(--label); font-weight: 650;
      text-decoration: none; }}
    .button:hover {{ background: #e9eefb; }}
    .button.primary {{ background: var(--label); color: #fff; }}
    .button.primary:hover {{ background: #172f73; }}
    .note {{ font-weight: 400; font-size: 0.9em; white-space: nowrap; }}
    .links {{ list-style: none; display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; padding: 0; margin: 1.25rem 0 0; }}
    .links a {{ display: inline-flex; align-items: center; gap: 0.45rem; color: var(--label); font-weight: 600; }}
    a:focus-visible {{ outline: 3px solid var(--ours); outline-offset: 3px; }}
    footer {{ margin-top: 2.5rem; border-top: 1px solid var(--line); padding-top: 1.5rem; color: var(--muted);
      font-size: 0.95rem; }}
    footer a {{ color: var(--label); }}
    kbd {{ font: inherit; font-weight: 700; padding: 0 0.35em; border: 1px solid var(--line); border-radius: 4px;
      background: #fff; }}
    @media (min-width: 1400px) {{
      main {{ padding-top: 5rem; }}
      .talks {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 3rem; }}
      .talk {{ grid-template-columns: 1fr; gap: 1.75rem; align-items: start; padding: 1.5rem 1.5rem 2rem;
        border: 1px solid var(--line); border-radius: 10px; }}
      .about > p {{ max-width: none; }}
      .about > p:first-of-type {{ min-height: 3.1em; }}
    }}
    @media (max-width: 1099px) {{
      .talk {{ grid-template-columns: 1fr; gap: 1.25rem; padding: 2rem 0; }}
      .about > p {{ max-width: 44rem; }}
    }}
    @media (max-width: 760px) {{
      main {{ padding: 2.5rem 1.25rem 2rem; }}
      .actions {{ grid-template-columns: 1fr; }}
      .button {{ width: 100%; justify-content: center; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Talks</h1>
    <p>Research talks by <a href="https://ajbarea.github.io/">AJ Barea</a>, PhD student at the
      Rochester Institute of Technology. Open one in your browser, or download it as PowerPoint or PDF.</p>
  </header>
  <div class="talks">
{items}
  </div>
  <footer>In a talk, press <kbd>S</kbd> for the speaker notes and <kbd>F</kbd> for full screen.
    Source: <a href="https://github.com/ajbarea/talks">github.com/ajbarea/talks</a></footer>
</main>
<script>
  // A preview plays its talk's title slide while the card is hovered or focused, and the talk
  // opens out of the preview that was clicked.
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {{
    for (const card of document.querySelectorAll(".talk")) {{
      const img = card.querySelector("img[data-loop]");
      if (!img) continue;
      const still = img.getAttribute("src");
      const set = (src) => () => {{ img.src = src; }};
      card.addEventListener("pointerenter", set(img.dataset.loop));
      card.addEventListener("pointerleave", set(still));
      card.addEventListener("focusin", set(img.dataset.loop));
      card.addEventListener("focusout", set(still));
    }}
  }}
  addEventListener("pageswap", (e) => {{
    if (!e.viewTransition || !e.activation || !e.activation.entry) return;
    const path = new URL(e.activation.entry.url).pathname;
    for (const shot of document.querySelectorAll(".shot")) {{
      if (new URL(shot.href).pathname === path) shot.style.viewTransitionName = "talk-shot";
    }}
  }});
</script>
</body>
</html>
"""


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
    claim(out, MARK, [*found, root / "vendor", root / "shared", *([exports] if exports is not None else [])])
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
        items.append(item(talk.name, title, description, named, sizes, exports is not None, loop))
    (out / "index.html").write_text(INDEX.format(items="\n".join(items)))
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
