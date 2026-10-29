"""Lint a Google Vids script: every segment fits one clip and states what Vids would otherwise invent.

Usage: python3 videos/check_script.py [script.md ...]   (default: every videos/*/script.md)
The rules it enforces are in videos/vids-rules.md.
"""

import pathlib
import re
import sys
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).resolve().parent
#: A Gemini Omni clip in Vids runs at most 10 seconds.
MAX_SECONDS = 10
#: US conversational rate, about 150 words a minute; a spoken line is timed at it.
WORDS_PER_MINUTE = 150
#: Each segment's required fields, matched against its bullet labels.
FIELDS = {
    "Environment & Lighting": re.compile(r"environment", re.I),
    "Avatar (Wardrobe & Physicality)": re.compile(r"wardrobe|physicality", re.I),
    "Visual Overlay": re.compile(r"overlay", re.I),
    "Spoken Script": re.compile(r"spoken", re.I),
    "Vocal Direction": re.compile(r"vocal", re.I),
}
SEGMENT = re.compile(r"^#{2,4}\s+(?:Segment|Scene)\b", re.I)
SPAN = re.compile(r"\((\d+):(\d{2})\s*[–—-]\s*(\d+):(\d{2})\)")
END = re.compile(r"^(#{1,4}\s|---\s*$)")
BULLET = re.compile(r"^[*-]\s+(.*)$")
LABEL = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$|^\*\*(.+?)\*\*:\s*(.*)$|^([^:`'\"*]{2,60}):\s*(.*)$")
DOUBLE = re.compile(r"[\"“”]")
QUOTED = re.compile(r"[\"“]([^\"“”]*)[\"”]")
WORD = re.compile(r"\w[\w'’-]*")
BACKREF = re.compile(r"\b(same as|as above|as before|see segment)\b", re.I)


@dataclass
class Segment:
    line: int
    heading: str
    fields: list[tuple[str, int, str]] = field(default_factory=list)
    loose: list[tuple[int, str]] = field(default_factory=list)


def segments(text: str) -> list[Segment]:
    """Each segment heading with its fields: (label, line, text), continuation lines folded in."""
    out: list[Segment] = []
    seg: Segment | None = None
    for n, raw in enumerate(text.splitlines(), 1):
        if SEGMENT.match(raw):
            seg = Segment(n, raw)
            out.append(seg)
            continue
        if seg is None:
            continue
        if END.match(raw):
            seg = None
            continue
        bullet = BULLET.match(raw)
        label = LABEL.match(bullet.group(1)) if bullet else None
        if label:
            groups = label.groups()
            name, body = next((groups[i], groups[i + 1]) for i in (0, 2, 4) if groups[i])
            seg.fields.append((name.strip(), n, body))
        elif seg.fields and raw.strip():
            name, line, body = seg.fields[-1]
            seg.fields[-1] = (name, line, f"{body}\n{raw}")
        elif raw.strip():
            seg.loose.append((n, raw))
    return out


def seconds(match: re.Match[str]) -> int:
    a, b, c, d = (int(g) for g in match.groups())
    return (c * 60 + d) - (a * 60 + b)


def check(text: str) -> list[tuple[int, str]]:
    """Every problem as (line, message); an empty list means the script passes."""
    segs = segments(text)
    if not segs:
        return [(1, "no '### Segment N (m:ss – m:ss)' headings found")]
    problems: list[tuple[int, str]] = []
    for seg in segs:
        span = SPAN.search(seg.heading)
        length = seconds(span) if span else None
        if length is None:
            problems.append((seg.line, "heading has no (m:ss – m:ss) span"))
        elif not 0 < length <= MAX_SECONDS:
            problems.append((seg.line, f"segment runs {length} s; a clip is 1 to {MAX_SECONDS} s"))
        if DOUBLE.search(seg.heading):
            problems.append((seg.line, "double quotes in the heading get voiced; use single quotes"))
        for name, rule in FIELDS.items():
            if not any(rule.search(label) and body.strip() for label, _, body in seg.fields):
                problems.append((seg.line, f"missing {name}"))
        for n, raw in seg.loose:
            if DOUBLE.search(raw):
                problems.append((n, "double quotes outside the spoken line get voiced; use single quotes"))
        for label, n, body in seg.fields:
            if BACKREF.search(body):
                problems.append((n, f"{label} points elsewhere; each clip is generated alone, so say it in full"))
            if not FIELDS["Spoken Script"].search(label):
                if DOUBLE.search(body):
                    problems.append((n, f"double quotes in {label} get voiced; use single quotes or backticks"))
                continue
            spans = QUOTED.findall(body)
            if len(DOUBLE.findall(body)) != 2 or len(spans) != 1:
                problems.append((n, "the spoken line needs exactly one double-quoted span; each one is voiced"))
            spoken = " ".join(spans)
            if "[" in spoken or "]" in spoken:
                problems.append((n, "a [direction] inside the spoken quotes is voiced; move it to Vocal Direction"))
            need = len(WORD.findall(spoken)) * 60 / WORDS_PER_MINUTE
            room = min(length or MAX_SECONDS, MAX_SECONDS)
            if need > room:
                problems.append((n, f"spoken line needs {need:.1f} s at {WORDS_PER_MINUTE} wpm; the clip has {room} s"))
    return sorted(problems)


def main(argv: list[str]) -> int:
    paths = [pathlib.Path(a) for a in argv] or sorted(HERE.glob("*/script.md"))
    if not paths:
        print("no scripts found", file=sys.stderr)
        return 1
    failed = 0
    for path in paths:
        problems = check(path.read_text(encoding="utf-8"))
        for line, message in problems:
            print(f"{path}:{line}: {message}", file=sys.stderr)
        failed += bool(problems)
        if not problems:
            print(f"{path}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
