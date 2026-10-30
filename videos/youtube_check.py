"""Check a YouTube upload: its description before it goes up, and its public page after.

Usage:
  python3 videos/youtube_check.py [FILE ...] [--duration S] [--ai]   lint description.txt files
                                                                      (default: every videos/**/*description.txt)
  python3 videos/youtube_check.py --live=ID [--ai] [--auto-thumbnail] check the public watch page (needs Pillow)

The rules and their sources are in videos/youtube-director/references/upload-package.md.
"""

import argparse
import json
import pathlib
import re
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
#: YouTube Data API: a description is at most 5,000 bytes and may not contain < or >.
MAX_BYTES = 5000
#: The hook line has to fit the search and mobile preview, which cuts at about 100 to 150 characters.
HOOK_MAX = 150
#: Chapters: the first at 0:00, at least 3, each at least 10 seconds long (YouTube Help 9884579).
MIN_CHAPTERS = 3
MIN_CHAPTER_SECONDS = 10
#: House cap; YouTube shows three above the title and ignores every hashtag past 60.
MAX_HASHTAGS = 8
#: Mean grey-level difference (0-255) below which the shown thumbnail is one of YouTube's own frames.
SAME_FRAME = 3.0

STAMP = r"(?:\d{1,2}:)?\d{1,2}:\d{2}"
CHAPTER = re.compile(rf"^\s*({STAMP})\s*[-–—:]?\s+(\S.*)$")
ANY_STAMP = re.compile(rf"(?<![\d:]){STAMP}(?![\d:])")
URL = re.compile(r"https?://\S+")
HASHTAG = re.compile(r"(?<![\w/&#])#[^\W\d_][\w]*")
DISCLOSURE = re.compile(r"\bAI[- ](?:avatar|clone|voice)\b", re.I)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def seconds(stamp: str) -> int:
    total = 0
    for part in stamp.split(":"):
        total = total * 60 + int(part)
    return total


def chapters(text: str) -> list[tuple[int, int, str]]:
    """Each line that starts with a timestamp: (line, seconds, title)."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if m := CHAPTER.match(line):
            out.append((n, seconds(m.group(1)), m.group(2).strip()))
    return out


def discloses_ai(text: str) -> bool:
    return bool(DISCLOSURE.search(text))


def check_description(text: str, duration: int | None = None, ai: bool = False) -> list[tuple[int, str]]:
    """Every problem as (line, message); line 0 means the whole description."""
    text = text.replace("\r\n", "\n")
    out: list[tuple[int, str]] = []
    if (size := len(text.encode())) > MAX_BYTES:
        out.append((0, f"{size} bytes; YouTube takes at most {MAX_BYTES}"))
    lines = text.splitlines()
    hook = lines[0].strip() if lines else ""
    if not hook or URL.match(hook) or hook.startswith("#") or CHAPTER.match(hook):
        out.append((1, "open with a hook sentence, not a link, hashtag or chapter"))
    elif len(hook) > HOOK_MAX:
        out.append((1, f"hook is {len(hook)} characters; the preview shows about {HOOK_MAX}"))
    for n, line in enumerate(lines, 1):
        if "<" in line or ">" in line:
            out.append((n, "YouTube rejects < and > in a description"))
        if len(ANY_STAMP.findall(line)) > 1:
            out.append((n, "two timestamps on one line: put each chapter on its own line"))
        if len(URL.findall(line)) > 1:
            out.append((n, "two links on one line: put each link on its own line"))
    marks = chapters(text)
    if marks:
        if marks[0][1] != 0:
            out.append((marks[0][0], "the first chapter must start at 0:00"))
        if len(marks) < MIN_CHAPTERS:
            out.append((marks[0][0], f"{len(marks)} chapters; YouTube needs at least {MIN_CHAPTERS}"))
        for (_, a, _), (n, b, _) in zip(marks, marks[1:], strict=False):
            if b <= a:
                out.append((n, "chapter times must go up: this one is not after the one before"))
            elif b - a < MIN_CHAPTER_SECONDS:
                out.append((n, f"the chapter before this one lasts {b - a} s; each needs {MIN_CHAPTER_SECONDS} s"))
        if duration is not None and duration - marks[-1][1] < MIN_CHAPTER_SECONDS:
            out.append((marks[-1][0], f"the last chapter lasts {duration - marks[-1][1]} s of a {duration} s video"))
    tags = [t for line in lines for t in HASHTAG.findall(URL.sub("", line))]
    if len(tags) > MAX_HASHTAGS:
        out.append((0, f"{len(tags)} hashtags; keep to {MAX_HASHTAGS} (YouTube ignores all past 60)"))
    if ai and not discloses_ai(text):
        out.append((0, "the video is AI-narrated: add a line saying an AI avatar narrates it"))
    return out


def _json_after(html: str, marker: str) -> dict:
    i = html.find(marker)
    if i < 0:
        raise ValueError(f"no {marker.strip(' =')} on the page")
    obj, _ = json.JSONDecoder().raw_decode(html, html.index("{", i))
    return obj


def _walk(obj, key: str):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v, key)


def page_facts(data: dict, player: dict) -> dict:
    """What the watch page shows: description, length, scrub-bar chapters, and the AI label if any."""
    details = player.get("videoDetails", {})
    marks = []
    for bar in _walk(data.get("playerOverlays", {}), "chapterRenderer"):
        mark = (bar.get("title", {}).get("simpleText", ""), bar.get("timeRangeStartMillis", 0) // 1000)
        if mark not in marks:
            marks.append(mark)
    made = _walk(data, "howThisWasMadeSectionViewModel")
    label = next((m.get("bodyHeader", {}).get("content", "") for m in made), "")
    return {
        "title": details.get("title", ""),
        "description": details.get("shortDescription", ""),
        "duration": int(details.get("lengthSeconds", 0)) or None,
        "chapters": marks,
        "ai_label": label,
    }


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en", "Cookie": "SOCS=CAI"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def thumbnail_kind(video: str, get=fetch) -> str:
    """'custom', or 'auto frame N' when the shown thumbnail is one of the three frames YouTube picked."""
    import io

    from PIL import Image, ImageChops, ImageStat

    def grey(name: str):
        return Image.open(io.BytesIO(get(f"https://i.ytimg.com/vi/{video}/{name}.jpg"))).convert("L").resize((96, 54))

    shown = grey("hqdefault")
    diffs = [ImageStat.Stat(ImageChops.difference(shown, grey(f"hq{n}"))).mean[0] for n in (1, 2, 3)]
    best = min(range(3), key=diffs.__getitem__)
    return f"auto frame {best + 1}" if diffs[best] < SAME_FRAME else "custom"


def verify(video: str, ai: bool = False, auto_thumbnail: bool = False, get=fetch) -> list[tuple[str, bool, str]]:
    """Each check on the public page as (check, passed, detail); ai says the video is AI-narrated."""
    html = get(f"https://www.youtube.com/watch?v={video}&hl=en").decode()
    facts = page_facts(_json_after(html, "ytInitialData = "), _json_after(html, "ytInitialPlayerResponse = "))
    desc, label = facts["description"], facts["ai_label"]
    problems = check_description(desc, facts["duration"], ai)
    out = [("description", False, f"line {n}: {p}" if n else p) for n, p in problems]
    if not out:
        out.append(("description", True, "passes the lint"))
    want = len(chapters(desc))
    got = len(facts["chapters"])
    if want:
        out.append(("chapters", got == want, f"{got} on the scrub bar, {want} in the description"))
    else:
        out.append(("chapters", True, f"none in the description ({got} automatic)"))
    want_label = "shown" if ai else "absent (pass --ai if an AI avatar narrates)"
    out.append(("AI label", bool(label) == ai, f"label {label or 'absent'}; expected {want_label}"))
    kind = thumbnail_kind(video, get)
    out.append(("thumbnail", auto_thumbnail or kind == "custom", kind))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*", type=pathlib.Path)
    ap.add_argument("--duration", type=int, help="video length in seconds, for the last chapter")
    ap.add_argument("--ai", action="store_true", help="the video is AI-narrated: require the disclosure line and label")
    ap.add_argument("--live", metavar="ID", help="check this public watch page instead (write --live=ID)")
    ap.add_argument("--auto-thumbnail", action="store_true", help="accept one of YouTube's own frames")
    args = ap.parse_args(argv)
    if args.live:
        results = verify(args.live, args.ai, args.auto_thumbnail)
        for name, ok, detail in results:
            print(f"{'PASS' if ok else 'FAIL'}  {name:<12} {detail}")
        return 0 if all(ok for _, ok, _ in results) else 1
    files = args.files or sorted(HERE.glob("**/*description.txt"))
    bad = 0
    for f in files:
        for n, problem in check_description(f.read_text(encoding="utf-8"), args.duration, args.ai):
            print(f"{f}:{n}: {problem}", file=sys.stderr)
            bad += 1
    print(f"{len(files)} description(s), {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
