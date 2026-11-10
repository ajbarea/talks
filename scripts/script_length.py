#!/usr/bin/env python3
"""How long each talk's spoken script takes to read aloud, failing a talk that runs over its cap.

    python3 scripts/script_length.py federated-agents            # words and minutes, exit 1 over the cap
    python3 scripts/script_length.py federated-agents --check    # also: a section per talk slide, data for each figure
    python3 scripts/script_length.py federated-agents --print    # the script with today's figures, to practise from

The script is the talk's `script.md`: one `## ` section per talk slide, in order, holding the words
said on that slide. The slides' speaker notes are short prompts; the script is the practice file.
A figure is written `{readings.team_openstack}` and counts as one word whatever it prints, so the
length does not move when a figure does. A sentence that holds only when a flag does is written
`{if readings.planted_all}...{/if}` or `{unless ...}...{/unless}`; every branch counts.

A talk with no `script.md` is measured from its speaker notes (`<aside class="notes">`) up to the
first backup slide: the FAQ index (`<section id="faq">`) or a slide with class `backup`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORDS_PER_MINUTE = 140
CAP_MINUTES = {"federated-agents": 10, "claude-tooling": 10, "checking-the-checker": 7, "federated-agents-step-one": 10}
# Tags that end a word even with no space around them; inline ones such as <b> do not.
BREAKS = {"br", "p", "li", "ul", "ol", "div", "section", "aside", "td", "tr"}
VOID = {"br", "img", "hr", "wbr"}

FIGURE = re.compile(r"\{([A-Za-z_][\w.]*)\}")
BRANCH = re.compile(r"\{(if|unless) ([A-Za-z_][\w.]*)\}(.*?)\{/\1\}", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)


class _Notes(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self._in_notes = False
        self._past_talk = False
        self._open: list[tuple[str, str]] = []  # (tag, "figure" | "branch" | "") open in the notes

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "section" and (a.get("id") == "faq" or "backup" in (a.get("class") or "").split()):
            self._past_talk = True
        if tag == "aside" and "notes" in (a.get("class") or "").split():
            self._in_notes, self._open = True, []
            self.text.append(" ")
            return
        if not self._in_notes or self._past_talk:
            return
        in_figure = any(kind == "figure" for _, kind in self._open)
        kind = ""
        if not in_figure and "data-value" in a:
            kind = "figure"
        elif not in_figure and ("data-if" in a or "data-unless" in a):
            kind = "branch"
        if kind == "figure":
            self.text.append(" FIGURE")
        elif not in_figure and (kind or tag in BREAKS):
            self.text.append(" ")
        if tag not in VOID:
            self._open.append((tag, kind))

    def handle_endtag(self, tag: str) -> None:
        if tag == "aside":
            self._in_notes = False
            self.text.append(" ")
            return
        if not self._in_notes or not any(t == tag for t, _ in self._open):
            return
        while self._open:
            t, kind = self._open.pop()
            if t == tag:
                break
        if kind == "branch" or tag in BREAKS:
            self.text.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_notes and not self._past_talk and not any(k == "figure" for _, k in self._open):
            self.text.append(data)


def words(html: str) -> int:
    """Words in the speaker notes of a deck's talk slides."""
    parser = _Notes()
    parser.feed(html)
    parser.close()
    return len("".join(parser.text).split())


def sections(md: str) -> list[tuple[str, str]]:
    """The script's (heading, body) pairs, one per `## ` section; comments dropped."""
    out: list[tuple[str, str]] = []
    for line in COMMENT.sub("", md).splitlines():
        if line.startswith("## "):
            out.append((line[3:].strip(), ""))
        elif out and not line.startswith("# "):
            out[-1] = (out[-1][0], out[-1][1] + line + "\n")
    return out


def script_words(md: str) -> int:
    """Words in a script.md: every branch counted, each figure one word, headings left out."""
    body = " ".join(b for _, b in sections(md))
    body = BRANCH.sub(lambda m: f" {m.group(3)} ", body)
    body = FIGURE.sub(" FIGURE ", body)
    return len(body.split())


def talk_slides(html: str) -> int:
    """How many top-level slides come before the first backup slide."""
    count, depth, past = 0, 0, False
    for m in re.finditer(r"<(/?)section\b([^>]*)>", COMMENT.sub("", html)):
        closing, attrs = m.group(1), m.group(2)
        if closing:
            depth -= 1
            continue
        if depth == 0 and not past:
            if re.search(r'id="faq"', attrs) or re.search(r'class="[^"]*\bbackup\b', attrs):
                past = True
            else:
                count += 1
        depth += 1
    return count


def deck_data(talk: str) -> dict:
    """window.DECK_DATA as the deck builds it, read by running its data files in node."""
    html = (ROOT / talk / "index.html").read_text(encoding="utf-8")
    files = [ROOT / talk / src for src in re.findall(r'<script src="(data/[^"]+\.js)"', html)]
    if not files:
        return {}
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("node is needed to read the deck's data files")
    prog = (
        "const vm=require('vm'),fs=require('fs');const ctx={window:{}};vm.createContext(ctx);"
        "for(const f of process.argv.slice(1))vm.runInContext(fs.readFileSync(f,'utf8'),ctx);"
        "process.stdout.write(JSON.stringify(ctx.window.DECK_DATA||{}));"
    )
    out = subprocess.run([node, "-e", prog, *map(str, files)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def lookup(data: dict, path: str) -> object:
    value: object = data
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(path)
        value = value[key]
    return value


def show(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int | float):
        return f"{value:,}"
    return str(value)


def render(md: str, data: dict) -> str:
    """The script as it will be said today: branches chosen, figures filled in."""

    def branch(m: re.Match[str]) -> str:
        flag = lookup(data, m.group(2))
        keep = flag is True if m.group(1) == "if" else flag is False
        return m.group(3) if keep else ""

    text = BRANCH.sub(branch, COMMENT.sub("", md))
    return FIGURE.sub(lambda m: show(lookup(data, m.group(1))), text)


def problems(talk: str) -> list[str]:
    """What is wrong with a talk's script.md: a section count off the slides, a figure with no data."""
    md = COMMENT.sub("", (ROOT / talk / "script.md").read_text(encoding="utf-8"))
    html = (ROOT / talk / "index.html").read_text(encoding="utf-8")
    found = []
    n, slides = len(sections(md)), talk_slides(html)
    if n != slides:
        found.append(f"{talk}/script.md has {n} sections for {slides} talk slides")
    data = deck_data(talk)
    paths = {m.group(1) for m in FIGURE.finditer(md)} | {m.group(2) for m in BRANCH.finditer(md)}
    for path in sorted(paths):
        try:
            lookup(data, path)
        except KeyError:
            found.append(f"{talk}/script.md: no data at {path}")
    return found


def minutes(n_words: int) -> float:
    return n_words / WORDS_PER_MINUTE


def cap_words(talk: str) -> int | None:
    """The most words a talk's script may hold, or None when it has no cap."""
    cap = CAP_MINUTES.get(talk)
    return None if cap is None else int(cap * WORDS_PER_MINUTE)


def count(talk: str) -> tuple[int, str]:
    script = ROOT / talk / "script.md"
    if script.exists():
        return script_words(script.read_text(encoding="utf-8")), "script.md"
    return words((ROOT / talk / "index.html").read_text(encoding="utf-8")), "speaker notes"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("talk", help="a talk folder, such as federated-agents")
    ap.add_argument("--check", action="store_true", help="also check the script against the slides and data")
    ap.add_argument("--print", dest="show", action="store_true", help="print the script with today's figures")
    args = ap.parse_args(argv)
    talk = pathlib.Path(args.talk).name
    if args.show:
        md = (ROOT / talk / "script.md").read_text(encoding="utf-8")
        sys.stdout.write(render(md, deck_data(talk)))
        return 0
    n, source = count(talk)
    limit = cap_words(talk)
    cap = "" if limit is None else f" (cap {CAP_MINUTES[talk]} minutes, {limit} words)"
    print(f"{talk}: {n} words, {minutes(n):.2f} minutes at {WORDS_PER_MINUTE} a minute, from {source}{cap}")
    status = 0
    if limit is not None and n > limit:
        print(f"{talk}: over the cap by {n - limit} words", file=sys.stderr)
        status = 1
    if args.check and (ROOT / talk / "script.md").exists():
        for line in problems(talk):
            print(line, file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
