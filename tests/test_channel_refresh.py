"""The channel refresh renders every concert and gaming description from its table, and each one passes the lint."""

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cr = _load("talks_channel_refresh", ROOT / "videos" / "channel" / "refresh.py")
yc = _load("talks_youtube_check_cr", ROOT / "videos" / "youtube_check.py")


def test_every_rendered_description_passes_the_lint() -> None:
    texts = cr.descriptions()
    assert len(texts) == len(cr.read(cr.MUSIC)) + len(cr.read(cr.GAMING)) > 0
    bad = {vid: yc.check_description(text) for vid, text in texts.items() if yc.check_description(text)}
    assert not bad


def test_a_concert_line_becomes_one_row() -> None:
    video = {
        "id": "abc",
        "title": "Dance Gavin Dance (Artificial Selection Tour) - Evaporate",
        "description": "Half Me (from Hamburg, Germany) @ Montage Music Hall in Rochester, New York [Jul 30, 2019]"
        "\n\n+ a bit",
    }
    row = cr.music_row(video, {"abc": "PL1"})
    assert row["band"] == "Half Me"
    assert row["origin"] == "Hamburg, Germany"
    assert row["song"] == "Evaporate"
    assert row["date"] == "July 30, 2019"
    assert row["tour"] == "Artificial Selection Tour"
    assert row["note"] == "+ a bit"
    assert row["playlist"] == "PL1"


def test_the_concert_template() -> None:
    row = dict.fromkeys(cr.MUSIC_FIELDS, "")
    row |= {"band": "Modest Mouse", "song": "Float On", "venue": "HISTORY", "city": "Toronto, Ontario, Canada"}
    row |= {"date": "November 17, 2024", "tour": "When We Were Young Festival 2024", "playlist": "PL1"}
    assert cr.render_music(row) == (
        "Float On by Modest Mouse, live at HISTORY in Toronto, Ontario, Canada, on November 17, 2024.\n\n"
        "Festival: When We Were Young Festival 2024\n\n"
        "Full show: https://www.youtube.com/playlist?list=PL1\n"
        "More videos: https://youtube.com/@AJBarea\n\n"
        "#ModestMouse #LiveMusic #Toronto #Concert\n"
    )


def test_a_repeated_music_credit_collapses_to_one_line() -> None:
    credit = "[Paper Moon by Plini]"
    row = cr.gaming_row({"id": "g", "description": f"year one footage\n\n{credit}\n{credit}\n{credit}"})
    assert cr.render_gaming(row) == "year one footage\n\nMusic: Paper Moon by Plini\n"


def test_a_note_ending_in_n_keeps_its_last_letter() -> None:
    row = cr.gaming_row({"id": "g", "description": "BF4 weapons test: SPAS-12 shotgun\n[Bubble Dream by Chon]"})
    assert cr.render_gaming(row) == "BF4 weapons test: SPAS-12 shotgun\n\nMusic: Bubble Dream by Chon\n"


def test_a_backslash_in_a_note_survives() -> None:
    row = cr.gaming_row({"id": "g", "description": "saved to C:\\new\nline two"})
    assert cr.render_gaming(row) == "saved to C:\\new\nline two\n"


def test_hashtags_keep_accents_and_skip_digit_led_names() -> None:
    assert cr.hashtag("Mötley Crüe") == "#MötleyCrüe"
    assert cr.hashtag("311") == ""
    row = dict.fromkeys(cr.MUSIC_FIELDS, "")
    row |= {"band": "311", "song": "Down", "venue": "Hall", "city": "Omaha, Nebraska", "date": "May 1, 2020"}
    assert cr.render_music(row).endswith("#LiveMusic #Omaha #Concert\n")


def test_extract_refuses_an_upload_with_no_tier(tmp_path, monkeypatch) -> None:
    meta = tmp_path / "meta.jsonl"
    meta.write_text('{"id": "zz", "title": "x", "description": "a talk", "categories": ["Education"]}\n')
    (tmp_path / "pl.tsv").write_text("")
    monkeypatch.setattr(cr, "MUSIC", tmp_path / "m.tsv")
    monkeypatch.setattr(cr, "GAMING", tmp_path / "g.tsv")
    with pytest.raises(SystemExit, match="no tier for zz"):
        cr.extract(meta, tmp_path / "pl.tsv")
