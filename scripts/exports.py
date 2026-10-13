#!/usr/bin/env python3
"""Export every talk for download: `<folder>.pptx` (graphe:slides `pptx`: one picture per slide,
the script in the notes), `<folder>.pdf` (graphe:slides `pdf`: vector, one page per slide) and
`thumb.webp`, its title slide, for the site's index.

    $B python scripts/exports.py _exports --slides <techne>/plugins/graphe/skills/slides/scripts/slides.py

Run it through the browser command slides.py names (WITH_BROWSER), which carries Playwright,
python-pptx and Pillow. The folder is replaced on every run, and only if this script built it.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import pathlib
import subprocess
import sys
import tempfile

# scripts/site.py, loaded by path: `import site` would find the standard library's module.
_spec = importlib.util.spec_from_file_location("talks_site", pathlib.Path(__file__).with_name("site.py"))
assert _spec and _spec.loader
talks_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(talks_site)

#: Marks a folder this script built, so it never replaces one it did not.
MARK = ".talks-exports"
#: The preview's size: half the 1920x1080 slide, sharp at the index's widest card on a 2x screen.
THUMB = (960, 540)
#: The preview's loop: the title slide's own entrance, sampled by seeking its animations, ending
#: on the still. Played on hover, so it is fetched only then.
LOOP_FPS = 10
LOOP_SECONDS = 4.4
#: Hides what is not slide, as the PowerPoint export does.
BARE = ".reveal .controls, .reveal .progress, .reveal .slide-number, .rail, .web-only, .tip, .tip-anchor { display: none !important; }"


def loop_frames(index: pathlib.Path) -> list:
    """Frames of the title slide's entrance at THUMB size, taken by pausing every animation and
    seeking it, so each frame is the same on every run."""
    from PIL import Image  # ty: ignore[unresolved-import]
    from playwright.sync_api import sync_playwright  # ty: ignore[unresolved-import]

    frames = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(index.resolve().as_uri() + "#/0")
            page.wait_for_function("window.Reveal && Reveal.isReady()", timeout=15000)
            page.add_style_tag(content=BARE)
            page.evaluate("document.getAnimations().forEach((a) => a.pause())")
            for i in range(round(LOOP_FPS * LOOP_SECONDS) + 1):
                page.evaluate(
                    "(t) => document.getAnimations().forEach((a) => { a.currentTime = t; })", i * 1000 / LOOP_FPS
                )
                page.wait_for_timeout(30)
                shot = page.screenshot(type="png")
                with Image.open(io.BytesIO(shot)) as im:
                    frames.append(im.convert("RGB").resize(THUMB, Image.Resampling.LANCZOS))
        finally:
            browser.close()
    return frames


def export(
    out: pathlib.Path, slides: pathlib.Path, root: pathlib.Path = talks_site.ROOT, loops: bool = True
) -> list[str]:
    from PIL import Image  # ty: ignore[unresolved-import]

    if not slides.is_file():
        raise SystemExit(f"no graphe:slides script at {slides}")
    found = talks_site.talks(root)
    if not found:
        raise SystemExit(f"no talks under {root}")
    talks_site.claim(out, MARK, [*found, root / "vendor"])
    for talk in found:
        target = out / talk.name
        with tempfile.TemporaryDirectory() as scratch:
            images = pathlib.Path(scratch) / "images"
            subprocess.run(
                [
                    sys.executable,
                    str(slides),
                    "pptx",
                    str(talk / "index.html"),
                    str(target / f"{talk.name}.pptx"),
                    "--images",
                    str(images),
                ],
                check=True,
            )
            subprocess.run(
                [sys.executable, str(slides), "pdf", str(talk / "index.html"), str(target / f"{talk.name}.pdf")],
                check=True,
            )
            with Image.open(images / "slide-01.png") as first:
                first.convert("RGB").resize(THUMB, Image.Resampling.LANCZOS).save(
                    target / "thumb.webp", quality=88, method=6
                )
        if loops:
            frames = loop_frames(talk / "index.html")
            frames[0].save(
                target / "thumb-loop.webp",
                save_all=True,
                append_images=frames[1:],
                duration=round(1000 / LOOP_FPS),
                loop=2,
                quality=72,
                method=4,
            )
    return [t.name for t in found]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("out", type=pathlib.Path)
    parser.add_argument("--slides", type=pathlib.Path, required=True, help="graphe:slides' slides.py")
    args = parser.parse_args()
    for name in export(args.out.resolve(), args.slides.resolve()):
        print(f"exported: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
