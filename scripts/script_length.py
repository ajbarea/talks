#!/usr/bin/env python3
"""How long each talk's script takes to read aloud, failing a talk that runs over its cap.

    python3 scripts/script_length.py federated-agents    # words and minutes, exit 1 over the cap

The script is the speaker notes (`<aside class="notes">`) of the slides before the first backup
slide: the FAQ index (`<section id="faq">`) or a slide with class `backup`, which are not spoken.
Every `data-if` / `data-unless` branch counts, whichever one today's figures show, and a bound
figure (`data-value`) counts as one word whatever its text, so the length does not move when a
figure does.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORDS_PER_MINUTE = 140
CAP_MINUTES = {"federated-agents": 10, "claude-duet": 12}
# Tags that end a word even with no space around them; inline ones such as <b> do not.
BREAKS = {"br", "p", "li", "ul", "ol", "div", "section", "aside", "td", "tr"}
VOID = {"br", "img", "hr", "wbr"}


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
    parser = _Notes()
    parser.feed(html)
    parser.close()
    return len("".join(parser.text).split())


def minutes(n_words: int) -> float:
    return n_words / WORDS_PER_MINUTE


def cap_words(talk: str) -> int | None:
    """The most words a talk's script may hold, or None when it has no cap."""
    cap = CAP_MINUTES.get(talk)
    return None if cap is None else int(cap * WORDS_PER_MINUTE)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("talk", help="a talk folder, such as federated-agents")
    talk = pathlib.Path(ap.parse_args(argv).talk).name
    n = words((ROOT / talk / "index.html").read_text(encoding="utf-8"))
    limit = cap_words(talk)
    cap = "" if limit is None else f" (cap {CAP_MINUTES[talk]} minutes, {limit} words)"
    print(f"{talk}: {n} words, {minutes(n):.2f} minutes at {WORDS_PER_MINUTE} a minute{cap}")
    if limit is not None and n > limit:
        print(f"{talk}: over the cap by {n - limit} words", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
