#!/usr/bin/env python3
"""Export one talk as stepped files for a room that shows a PDF or .pptx, not the web deck.

    python scripts/stepped_export.py checking-the-checker out/Talk-Revised

Writes `<out>.pdf` and `<out>.pptx`. Each slide gives one page per build step: the page before
any fragment shows, then one page per fragment, the finished slide last. Clicking through reads
as the build; no transition runs between steps of one slide. The backup index's links jump to
their slides in both files.

Run it through a command that carries Playwright (`slides.py`'s WITH_BROWSER) and `uv run`'s
pymupdf and python-pptx. Pages are 1920x1080 pictures drawn in the machine's own fonts.
"""

from __future__ import annotations

import argparse
import io
import pathlib
from dataclasses import dataclass, field

W, H = 1920, 1080
#: Hides what is not slide, as the web exports do; the chapter rail is navigation, not content.
BARE = (
    "*, *::before, *::after { transition: none !important; animation: none !important; }"
    " .reveal .controls, .reveal .progress, .reveal .slide-number, .rail, .web-only, .tip, .tip-anchor"
    " { display: none !important; }"
)

_SLIDES = "() => Reveal.getSlides().map((s) => ({ id: s.id || '', ...Reveal.getIndices(s) }))"
# Slide s, shown before any fragment; the fragment steps then follow through Reveal.nextFragment.
_SHOW = "([h, v]) => { Reveal.slide(h, v, -1); }"
_STATE = """() => {
  const s = Reveal.getCurrentSlide();
  const h = [...s.querySelectorAll('h1, h2, h3')].find((el) => !el.closest('aside.notes'));
  const clone = s.cloneNode(true);
  clone.querySelectorAll('aside.notes, script, style').forEach((n) => n.remove());
  const links = [...s.querySelectorAll('a[href^="#/"]')].map((a) => {
    const r = a.getBoundingClientRect();
    return { to: a.getAttribute('href').slice(2), x: r.left, y: r.top, w: r.width, h: r.height };
  }).filter((l) => l.w > 0 && l.h > 0);
  return { title: h ? h.innerText.replace(/\\s+/g, ' ').trim() : '', links };
}"""
_TEXT = """() => {
  const s = Reveal.getCurrentSlide();
  const out = [];
  const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    const el = n.parentElement;
    if (el.closest('aside.notes, script, style')) continue;
    const st = getComputedStyle(el);
    if (st.visibility !== 'visible' || st.display === 'none' || st.opacity === '0') continue;
    const t = n.textContent.replace(/\\s+/g, ' ').trim();
    if (t) out.push(t);
  }
  return out.join(' ');
}"""


@dataclass
class Page:
    """One built step of one slide."""

    slide: int
    step: int
    slide_id: str
    title: str
    alt: str
    png: bytes
    links: list[dict] = field(default_factory=list)


def capture(index: pathlib.Path) -> list[Page]:
    """Every build step of every slide in a reveal.js deck, as pictures."""
    from playwright.sync_api import sync_playwright  # ty: ignore[unresolved-import]

    pages: list[Page] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_context(viewport={"width": W, "height": H}, bypass_csp=True).new_page()
            page.goto(index.resolve().as_uri())
            page.wait_for_function("window.Reveal && Reveal.isReady()", timeout=15000)
            page.add_style_tag(content=BARE)
            for number, slide in enumerate(page.evaluate(_SLIDES), 1):
                page.evaluate(_SHOW, [slide["h"], slide["v"]])
                step = 0
                while True:
                    page.wait_for_timeout(60)
                    state = page.evaluate(_STATE)
                    pages.append(
                        Page(
                            slide=number,
                            step=step,
                            slide_id=slide["id"],
                            title=state["title"] or f"Slide {number}",
                            alt=page.evaluate(_TEXT),
                            png=page.screenshot(),
                            links=state["links"],
                        )
                    )
                    if not page.evaluate("() => Reveal.nextFragment()"):
                        break
                    step += 1
        finally:
            browser.close()
    return pages


def first_page_of(pages: list[Page]) -> dict[str, int]:
    """Slide id -> index of that slide's first page, for the links."""
    out: dict[str, int] = {}
    for i, pg in enumerate(pages):
        if pg.slide_id:
            out.setdefault(pg.slide_id, i)
    return out


def build_pdf(pages: list[Page], target: pathlib.Path) -> None:
    import pymupdf  # ty: ignore[unresolved-import]

    scale = 0.75  # 1920 px at 96 dpi is 1440 pt
    doc = pymupdf.open()
    where = first_page_of(pages)
    for pg in pages:
        sheet = doc.new_page(width=W * scale, height=H * scale)
        sheet.insert_image(sheet.rect, stream=pg.png)
    for i, pg in enumerate(pages):
        for link in pg.links:
            if link["to"] in where:
                x, y, w, h = (link[k] * scale for k in ("x", "y", "w", "h"))
                rect = pymupdf.Rect(x, y, x + w, y + h)
                doc[i].insert_link({"kind": pymupdf.LINK_GOTO, "from": rect, "page": where[link["to"]]})
    toc, seen = [], set()
    for i, pg in enumerate(pages):
        if pg.slide not in seen:
            seen.add(pg.slide)
            toc.append([1, pg.title, i + 1])
    doc.set_toc(toc)
    doc.set_metadata({"title": pages[0].title if pages else ""})
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".partial")
    doc.save(str(partial), garbage=4, deflate=True)
    doc.close()
    partial.replace(target)


def build_pptx(pages: list[Page], target: pathlib.Path) -> None:
    from pptx import Presentation  # ty: ignore[unresolved-import]
    from pptx.util import Emu  # ty: ignore[unresolved-import]

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    layout = prs.slide_layouts[5]  # title only
    slides = []
    for pg in pages:
        slide = prs.slides.add_slide(layout)
        slides.append(slide)
        heading = slide.shapes.title
        heading.text = pg.title
        # Above the slide: not shown, but the outline, slide list and screen readers read it.
        heading.left, heading.top = Emu(0), Emu(-prs.slide_height // 6)
        heading.width, heading.height = prs.slide_width, Emu(prs.slide_height // 6)
        picture = slide.shapes.add_picture(io.BytesIO(pg.png), 0, 0, prs.slide_width, prs.slide_height)
        picture.name = f"Slide {pg.slide}, step {pg.step + 1}"
        picture._element.nvPicPr.cNvPr.set("descr", pg.alt)
    where = first_page_of(pages)
    ex, ey = prs.slide_width / W, prs.slide_height / H
    for slide, pg in zip(slides, pages, strict=True):
        for link in pg.links:
            if link["to"] not in where:
                continue
            x, w = (Emu(int(link[k] * ex)) for k in ("x", "w"))
            y, h = (Emu(int(link[k] * ey)) for k in ("y", "h"))
            hot = slide.shapes.add_shape(1, x, y, w, h)
            hot.fill.background()
            hot.line.fill.background()
            hot.name = f"Link to {link['to']}"
            hot.click_action.target_slide = slides[where[link["to"]]]
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".partial")
    prs.save(str(partial))
    partial.replace(target)


def export(index: pathlib.Path, out: pathlib.Path) -> list[Page]:
    pages = capture(index)
    build_pdf(pages, out.with_suffix(".pdf"))
    build_pptx(pages, out.with_suffix(".pptx"))
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("talk", type=pathlib.Path, help="the talk's folder")
    parser.add_argument("out", type=pathlib.Path, help="output path without extension")
    args = parser.parse_args()
    pages = export(args.talk / "index.html", args.out)
    slides = len({p.slide for p in pages})
    print(f"stepped: {len(pages)} pages from {slides} slides -> {args.out}.pdf, {args.out}.pptx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
