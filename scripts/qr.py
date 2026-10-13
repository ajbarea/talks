#!/usr/bin/env python3
"""Put a QR code to the talk's own address on every talk's title and closing slides.

    uv run python scripts/qr.py            # write the codes into each talk's index.html
    uv run python scripts/qr.py --check    # fail if any talk's codes are missing or stale

The address is SITE plus the talk's folder name, the one place it is defined. Each code is an
inline SVG (error correction M, 4-module quiet zone, black on white), so it is crisp at any
size, travels into the PDF and PowerPoint exports, and needs no network. A block sits between
`<!-- qr:KIND -->` and `<!-- /qr -->`; a talk without one gets it added: KIND `follow` into the
first slide, KIND `close` into the slide titled "Thank you".
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import pathlib
import re
import sys

import segno

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://ajbarea.github.io/talks/"
QUIET = 4
KINDS = ("follow", "close")
BLOCK = re.compile(r"[ \t]*<!-- qr:(follow|close) -->.*?<!-- /qr -->\n?", re.S)

# scripts/site.py, loaded by path: `import site` would find the standard library's module.
_spec = importlib.util.spec_from_file_location("talks_site", pathlib.Path(__file__).with_name("site.py"))
assert _spec and _spec.loader
talks_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(talks_site)


def talk_url(talk: pathlib.Path | str) -> str:
    return f"{SITE}{pathlib.Path(talk).name}"


def short(url: str) -> str:
    return url.removeprefix("https://")


def svg(url: str) -> str:
    """The code as one path of horizontal runs on a white square that includes the quiet zone."""
    rows = segno.make(url, error="m", boost_error=False, micro=False).matrix
    size = len(rows) + 2 * QUIET
    runs = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if not row[x]:
                x += 1
                continue
            start = x
            while x < len(row) and row[x]:
                x += 1
            runs.append(f"M{start + QUIET} {y + QUIET}h{x - start}v1h-{x - start}z")
    label = f"QR code for {short(url)}"
    return (
        f'<svg class="qr-code" viewBox="0 0 {size} {size}" role="img" aria-label="{label}" '
        f'shape-rendering="crispEdges"><rect width="{size}" height="{size}" fill="#fff"/>'
        f'<path fill="#000" d="{"".join(runs)}"/></svg>'
    )


def block(kind: str, url: str) -> str:
    text = html.escape(short(url)).replace("/talks/", "/talks/<wbr>")
    if kind == "follow":
        body = f'<p class="qr-label"><b>Follow along</b><span>{text}</span></p>\n    {svg(url)}'
        attrs = 'class="qr qr-follow"'
    else:
        body = svg(url)
        attrs = 'class="qr qr-close" data-motion="pop" data-delay="300" data-dur="600"'
    return f"  <!-- qr:{kind} -->\n  <div {attrs}>\n    {body}\n  </div>\n  <!-- /qr -->\n"


def slide_end(page: str, kind: str, talk: str) -> int:
    """Where a new block goes: before the slide's notes, else before its closing tag."""
    if kind == "follow":
        start = page.index("<section")
    else:
        m = re.search(r"<h2>\s*Thank you\s*</h2>", page)
        if not m:
            raise SystemExit(f'{talk}/index.html has no "Thank you" slide to hold its closing QR code')
        start = m.start()
    end = page.index("</section>", start)
    notes = page.rfind('<aside class="notes">', start, end)
    if notes != -1:
        return page.rfind("\n", start, notes) + 1
    return page.rfind("\n", start, end) + 1


def render(page: str, talk: pathlib.Path) -> str:
    url = talk_url(talk)
    found = {m.group(1) for m in BLOCK.finditer(page)}
    page = BLOCK.sub(lambda m: block(m.group(1), url), page)
    for kind in KINDS:
        if kind not in found:
            at = slide_end(page, kind, talk.name)
            page = page[:at] + block(kind, url) + page[at:]
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if any talk's codes are missing or stale")
    args = parser.parse_args()
    stale = []
    for talk in talks_site.talks(ROOT):
        index = talk / "index.html"
        page = index.read_text()
        want = render(page, talk)
        if want != page:
            stale.append(talk.name)
            if not args.check:
                index.write_text(want)
                print(f"wrote {talk.name}: {talk_url(talk)}")
    if args.check and stale:
        print(f"QR codes missing or stale in: {', '.join(stale)}; run `make qr`", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
