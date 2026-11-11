"""Controls for the stepped export: one page per build step, links that jump, no transitions."""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pymupdf
import pytest
from PIL import Image
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def stepped():
    spec = importlib.util.spec_from_file_location("stepped_export", ROOT / "scripts" / "stepped_export.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _png(shade: int) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (192, 108), (shade, shade, shade)).save(out, "PNG")
    return out.getvalue()


@pytest.fixture
def pages(stepped):
    """Slide 1 has three steps, slide 2 (id "faq") one and links to slide 1, slide 3 (id "end") one."""
    link = [{"to": "intro", "x": 100, "y": 200, "w": 300, "h": 40}]
    return [
        stepped.Page(1, 0, "intro", "Intro", "first", _png(10)),
        stepped.Page(1, 1, "intro", "Intro", "first, second", _png(20)),
        stepped.Page(1, 2, "intro", "Intro", "first, second, third", _png(30)),
        stepped.Page(2, 0, "faq", "Questions", "list", _png(40), link),
        stepped.Page(3, 0, "end", "Back", "bye", _png(50), [{"to": "missing", "x": 0, "y": 0, "w": 9, "h": 9}]),
    ]


def test_pdf_has_one_page_per_step_and_a_link_to_the_slides_first_step(stepped, pages, tmp_path):
    out = tmp_path / "t.pdf"
    stepped.build_pdf(pages, out)
    with pymupdf.open(out) as doc:
        assert len(doc) == 5
        assert [p.get_pixmap(dpi=4).samples[0] for p in doc] == [10, 20, 30, 40, 50]
        jumps = doc[3].get_links()
        assert [(j["kind"], j["page"]) for j in jumps] == [(pymupdf.LINK_GOTO, 0)]
        assert doc[4].get_links() == []  # a target that is not a slide draws no link
        assert [t[1] for t in doc.get_toc()] == ["Intro", "Questions", "Back"]


def test_pptx_has_one_slide_per_step_with_the_steps_text_and_no_transition(stepped, pages, tmp_path):
    out = tmp_path / "t.pptx"
    stepped.build_pptx(pages, out)
    prs = Presentation(out)
    slides = list(prs.slides)
    assert len(slides) == 5
    alts = [[s._element.xpath("//p:pic/p:nvPicPr/p:cNvPr/@descr")][0][0] for s in slides]
    assert alts[:3] == ["first", "first, second", "first, second, third"]
    assert all(not s._element.xpath("//p:transition") for s in slides)
    hot = [sh for sh in slides[3].shapes if sh.name == "Link to intro"]
    assert len(hot) == 1
    assert hot[0].click_action.target_slide == slides[0]
    assert not [sh for sh in slides[4].shapes if sh.name.startswith("Link to")]


def test_first_page_of_names_each_slides_first_step(stepped, pages):
    assert stepped.first_page_of(pages) == {"intro": 0, "faq": 3, "end": 4}
