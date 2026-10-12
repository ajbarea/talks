#!/usr/bin/env python3
"""Export every talk for download: `<folder>.pptx` (graphe:slides `pptx`: one picture per slide,
the script in the notes) and `thumb.webp`, its title slide, for the site's index.

    $B python scripts/exports.py _exports --slides <techne>/plugins/graphe/skills/slides/scripts/slides.py

Run it through the browser command slides.py names (WITH_BROWSER), which carries Playwright,
python-pptx and Pillow. The folder is replaced on every run, and only if this script built it.
"""

from __future__ import annotations

import argparse
import importlib.util
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


def export(out: pathlib.Path, slides: pathlib.Path, root: pathlib.Path = talks_site.ROOT) -> list[str]:
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
            with Image.open(images / "slide-01.png") as first:
                first.convert("RGB").resize(THUMB, Image.Resampling.LANCZOS).save(
                    target / "thumb.webp", quality=88, method=6
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
