#!/usr/bin/env python3
"""How long each talk's script takes to read aloud, failing a talk that runs over its cap.

    python3 scripts/script_length.py federated-agents    # words and minutes, exit 1 over the cap

The script is the speaker notes (`<aside class="notes">`) of the slides before the FAQ index
(`<section id="faq">`); the FAQ slides are not spoken. Every `data-if` / `data-unless` branch
counts, whichever one today's figures show, and a bound figure (`data-value`, empty in the
source) counts as one word, so the length does not move when a figure does.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORDS_PER_MINUTE = 140
CAP_MINUTES = {"federated-agents": 6.5}


class _Notes(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self._in_notes = False
        self._past_talk = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "section" and a.get("id") == "faq":
            self._past_talk = True
        elif tag == "aside" and "notes" in (a.get("class") or "").split():
            self._in_notes = True
            self.text.append(" ")
        elif self._in_notes and not self._past_talk:
            if "data-value" in a:
                self.text.append(" FIGURE")
            elif "data-if" in a or "data-unless" in a:
                self.text.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "aside" and self._in_notes:
            self._in_notes = False
            self.text.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_notes and not self._past_talk:
            self.text.append(data)


def words(html: str) -> int:
    parser = _Notes()
    parser.feed(html)
    parser.close()
    return len("".join(parser.text).split())


def minutes(n_words: int) -> float:
    return n_words / WORDS_PER_MINUTE


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("talk", help="a talk folder, such as federated-agents")
    talk = pathlib.Path(ap.parse_args(argv).talk)
    n = words((ROOT / talk.name / "index.html").read_text(encoding="utf-8"))
    cap = CAP_MINUTES.get(talk.name)
    over = cap is not None and minutes(n) > cap
    limit = f" (cap {cap} minutes, {int(cap * WORDS_PER_MINUTE)} words)" if cap else ""
    print(f"{talk.name}: {n} words, {minutes(n):.2f} minutes at {WORDS_PER_MINUTE} a minute{limit}")
    if over:
        print(f"{talk.name}: over the cap by {n - int(cap * WORDS_PER_MINUTE)} words", file=sys.stderr)
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
