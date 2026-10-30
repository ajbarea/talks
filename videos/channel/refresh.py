"""Render the channel refresh descriptions: live music from one template (Tier 2), gaming clips reformatted (Tier 3).

Usage:
  python3 videos/channel/refresh.py extract META.jsonl PLAYLISTS.tsv   rebuild music.tsv and gaming.tsv from a pull
  python3 videos/channel/refresh.py render OUT_DIR                      write OUT_DIR/<id>-description.txt for every row

META.jsonl is one yt-dlp JSON object per line; PLAYLISTS.tsv is `playlist id, playlist title, video id` per line.
Every other upload is Tier 1 (tech and research), written by hand in tier1/.
"""

import csv
import datetime
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
MUSIC = HERE / "music.tsv"
GAMING = HERE / "gaming.tsv"
MUSIC_FIELDS = ["id", "band", "origin", "song", "venue", "city", "date", "tour", "note", "playlist"]
GAMING_FIELDS = ["id", "note", "music"]
CHANNEL = "More videos: https://youtube.com/@AJBarea"
PLAYLIST = "https://www.youtube.com/playlist?list="
#: "Band (from X) @ Venue in City [Date] (Tour)", the first line of every concert upload.
CONCERT = re.compile(
    r"^(?P<band>.+?)(?: \((?P<origin>from [^)]*)\))? @ (?P<venue>.+?) in (?P<city>.+?)"
    r" \[(?P<date>[^\]]+)\]\s*(?:\((?P<tour>[^)]*)\))?\s*$"
)
CREDIT = re.compile(r"^\[(.+ by .+)\]$")


def full_date(text: str) -> str:
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            d = datetime.datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
        return f"{d:%B} {d.day}, {d.year}"
    raise ValueError(f"unknown date {text!r}")


def hashtag(text: str) -> str:
    """CamelCase hashtag, or "" when no letter leads it (YouTube ignores #311)."""
    tag = "".join(w[:1].upper() + w[1:] for w in re.findall(r"[^\W_]+", text))
    return f"#{tag}" if tag[:1].isalpha() else ""


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def unescape(text: str) -> str:
    return re.sub(r"\\(.)", lambda m: "\n" if m[1] == "n" else m[1], text)


def music_row(video: dict, shows: dict[str, str]) -> dict[str, str]:
    first, *rest = video["description"].strip().splitlines()
    m = CONCERT.match(first.strip())
    if not m:
        raise ValueError(f"{video['id']}: not a concert description: {first!r}")
    head, _, song = video["title"].partition(" - ")
    tour = m["tour"] or (re.search(r"\(([^)]*Tour)\)", head) or [None, ""])[1]
    return {
        "id": video["id"],
        "band": m["band"],
        "origin": (m["origin"] or "").removeprefix("from "),
        "song": song.strip(),
        "venue": m["venue"],
        "city": m["city"],
        "date": full_date(m["date"]),
        "tour": tour.strip(),
        "note": " ".join(line.strip() for line in rest if line.strip()),
        "playlist": shows.get(video["id"], ""),
    }


def gaming_row(video: dict) -> dict[str, str]:
    note, music = [], []
    for line in video["description"].strip().splitlines():
        if m := CREDIT.match(line.strip()):
            if m[1] not in music:
                music.append(m[1])
        elif line.strip() or (note and note[-1]):
            note.append(line.rstrip())
    return {"id": video["id"], "note": escape("\n".join(note).strip("\n")), "music": "; ".join(music)}


def render_music(r: dict[str, str]) -> str:
    out = [f"{r['song']} by {r['band']}, live at {r['venue']} in {r['city']}, on {r['date']}.", ""]
    label = "Festival" if "Festival" in r["tour"] else "Tour"
    extra = [f"{label}: {r['tour']}" if r["tour"] else "", f"{r['band']} is from {r['origin']}." if r["origin"] else ""]
    extra.append(r["note"])
    if extra := [line for line in extra if line]:
        out += [*extra, ""]
    if r["playlist"]:
        out.append(f"Full show: {PLAYLIST}{r['playlist']}")
    tags = [hashtag(r["band"]), "#LiveMusic", hashtag(r["city"].split(",")[0]), "#Concert"]
    out += [CHANNEL, "", " ".join(t for t in tags if t)]
    return "\n".join(out) + "\n"


def render_gaming(r: dict[str, str]) -> str:
    out = unescape(r["note"]).split("\n") if r["note"] else []
    if r["music"]:
        out += ["", *(f"Music: {m}" for m in r["music"].split("; "))]
    return "\n".join(out).strip("\n") + "\n"


def read(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write(path: pathlib.Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["id"]))


def descriptions() -> dict[str, str]:
    """Every Tier 2 and Tier 3 description, by video id."""
    out = {r["id"]: render_music(r) for r in read(MUSIC)}
    out.update({r["id"]: render_gaming(r) for r in read(GAMING)})
    return out


def extract(meta: pathlib.Path, playlists: pathlib.Path) -> None:
    shows = {}
    for line in playlists.read_text(encoding="utf-8").splitlines():
        pid, title, vid = line.split("\t")
        if " @ " in title:
            shows[vid] = pid
    tier1 = {p.name.removesuffix("-description.txt") for p in (HERE / "tier1").glob("*-description.txt")}
    music, gaming, dropped = [], [], []
    for line in meta.read_text(encoding="utf-8").splitlines():
        video = json.loads(line)
        if video["id"] in tier1:
            continue
        if video.get("categories") == ["Gaming"]:
            gaming.append(gaming_row(video))
        elif CONCERT.match(video["description"].strip().splitlines()[0] if video["description"].strip() else ""):
            music.append(music_row(video, shows))
        else:
            dropped.append(video["id"])
    if dropped:
        raise SystemExit(f"no tier for {', '.join(dropped)}: add a tier1 description or fix the first line")
    write(MUSIC, MUSIC_FIELDS, music)
    write(GAMING, GAMING_FIELDS, gaming)
    print(f"{len(music)} concert uploads, {len(gaming)} gaming clips")


def main(argv: list[str]) -> int:
    if argv[:1] == ["extract"] and len(argv) == 3:
        extract(pathlib.Path(argv[1]), pathlib.Path(argv[2]))
    elif argv[:1] == ["render"] and len(argv) == 2:
        out = pathlib.Path(argv[1])
        out.mkdir(parents=True, exist_ok=True)
        texts = descriptions()
        for vid, text in texts.items():
            (out / f"{vid}-description.txt").write_text(text, encoding="utf-8")
        print(f"{len(texts)} descriptions in {out}")
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
