"""Each talk's committed QR codes decode to that talk's exact address."""

import importlib.util
import pathlib
import re

import pytest
import zxingcpp
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("talks_qr", ROOT / "scripts" / "qr.py")
assert _spec and _spec.loader
qr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qr)

TALKS = qr.talks_site.talks(ROOT)
SCALE = 8


def rasterize(svg: str) -> Image.Image:
    """The SVG's path of `M x y h w v1 h-w z` runs, drawn in black on its white square."""
    size = int(re.search(r'viewBox="0 0 (\d+) \1"', svg).group(1))
    img = Image.new("L", (size * SCALE, size * SCALE), 255)
    draw = ImageDraw.Draw(img)
    for x, y, w in re.findall(r"M(\d+) (\d+)h(\d+)v1h-\3z", re.search(r' d="([^"]*)"', svg).group(1)):
        x, y, w = int(x), int(y), int(w)
        draw.rectangle([x * SCALE, y * SCALE, (x + w) * SCALE - 1, (y + 1) * SCALE - 1], fill=0)
    return img


def codes(talk: pathlib.Path) -> dict[str, str]:
    page = (talk / "index.html").read_text()
    return {m.group(1): m.group(0) for m in qr.BLOCK.finditer(page)}


def test_there_are_talks():
    assert TALKS


@pytest.mark.parametrize("talk", TALKS, ids=lambda t: t.name)
def test_every_talk_has_both_codes_decoding_to_its_address(talk):
    found = codes(talk)
    assert set(found) == set(qr.KINDS)
    for kind, markup in found.items():
        results = zxingcpp.read_barcodes(rasterize(markup))
        assert [r.text for r in results] == [qr.talk_url(talk)], kind
        assert results[0].ec_level == "M", kind


@pytest.mark.parametrize("talk", TALKS, ids=lambda t: t.name)
def test_codes_are_current(talk):
    page = (talk / "index.html").read_text()
    assert qr.render(page, talk) == page


@pytest.mark.parametrize("talk", TALKS, ids=lambda t: t.name)
def test_closing_slide_text_matches_the_address(talk):
    page = (talk / "index.html").read_text()
    assert f"These slides: {qr.short(qr.talk_url(talk))}<" in page


def test_quiet_zone_is_four_modules_of_white():
    img = rasterize(qr.svg("https://example.com/x"))
    margin = qr.QUIET * SCALE
    assert min(img.crop((0, 0, img.width, margin)) == 255
    assert min(img.crop((0, 0, margin, img.height)).getdata()) == 255
