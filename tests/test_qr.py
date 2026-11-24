"""Each talk's committed QR codes decode to that talk's exact address."""

import importlib.util
import json
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
        want = qr.close_target(talk)[0] if kind == "close" else qr.talk_url(talk)
        assert [r.text for r in results] == [want], kind
        assert results[0].ec_level == "M", kind


@pytest.mark.parametrize("talk", TALKS, ids=lambda t: t.name)
def test_codes_are_current(talk):
    page = (talk / "index.html").read_text()
    assert qr.render(page, talk) == page


@pytest.mark.parametrize("talk", TALKS, ids=lambda t: t.name)
def test_address_appears_once_on_the_closing_slide(talk):
    page = (talk / "index.html").read_text()
    start = page.rindex("<section", 0, page.index("Thank you"))
    slide = page[start : page.index("</section>", start)]
    assert "closing" in slide[: slide.index(">")]
    address = qr.short(qr.close_target(talk)[0]).rstrip("/")
    assert slide.count(address.replace("/talks/", "/talks/<br>")) == 1
    assert "These slides:" not in slide


def test_quiet_zone_is_four_modules_of_white():
    img = rasterize(qr.svg("https://example.com/x"))
    margin = qr.QUIET * SCALE
    assert img.crop((0, 0, img.width, margin)).getextrema()[0] == 255
    assert img.crop((0, 0, margin, img.height)).getextrema()[0] == 255


def test_a_talk_can_end_on_its_playground():
    url, label = qr.close_target(ROOT / "qfl-privacy")
    assert (url, label) == ("https://ajbarea.github.io/talks/qfl-privacy/lab/", "Try the lab")
    assert qr.close_target(ROOT / "checking-the-checker") == (qr.talk_url("checking-the-checker"), "These slides")


BAD_CLOSE = [
    {"path": "../etc/", "label": "x"},
    {"path": "nowhere/", "label": "x"},
    {"path": "lab/"},
    {"path": "lab/", "label": "x", "url": "https://example.com"},
    {"path": "data/", "label": "x"},
    "lab/",
    ["lab/"],
    5,
    {"path": 5, "label": "x"},
    {"path": "lab/", "label": 5},
]


@pytest.mark.parametrize("close", BAD_CLOSE)
def test_a_close_entry_must_name_a_page_inside_the_talk(tmp_path, monkeypatch, close):
    (tmp_path / "t" / "lab").mkdir(parents=True)
    (tmp_path / "t" / "lab" / "index.html").write_text("<!doctype html>")
    (tmp_path / "t" / "data").mkdir()  # a folder with no page in it
    (tmp_path / "etc").mkdir()  # "../etc/" exists, so only the path rule can refuse it
    (tmp_path / "etc" / "index.html").write_text("<!doctype html>")
    (tmp_path / "t" / "talk.json").write_text(json.dumps({"close": close}))
    monkeypatch.setattr(qr, "ROOT", tmp_path)
    with pytest.raises(SystemExit):
        qr.close_target(tmp_path / "t")


def test_a_talk_json_that_is_not_json_names_the_file(tmp_path, monkeypatch):
    (tmp_path / "t").mkdir()
    (tmp_path / "t" / "talk.json").write_text("{")
    monkeypatch.setattr(qr, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="t/talk.json is not JSON"):
        qr.close_target(tmp_path / "t")
