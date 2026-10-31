# talks

AJ Barea's research talks as web decks, published at https://ajbarea.github.io/talks/.

| Talk | Link |
|---|---|
| Federated Agents | https://ajbarea.github.io/talks/federated-agents/ |
| Kourai Khryseai | https://ajbarea.github.io/talks/kourai-khryseai/ |
| Claude Duet, and why Claude Code is the tool I live in | https://ajbarea.github.io/talks/claude-duet/ |

Each talk opens in any browser, with no network needed once loaded. Press `S` for the speaker
view (the script, a timer and the next slide), `O` for the overview and `F` for full screen. A
link like `.../federated-agents/#/5` opens a given slide.

## Layout

- One folder per talk, holding its `index.html`, its own `deck.css` and any `data/`. The folder
  name is the talk's address.
- `vendor/reveal/`: reveal.js, shared by every talk.
- `videos/`: scripts for AJ's explainer videos, made in Google Vids; see [videos/README.md](videos/README.md).
- `shared/deck.js`, `shared/deck.css`: the behaviour and base styles every talk loads (chapter rail,
  agenda, figures from data, phone feed); a talk's own `deck.css` adds what is particular to it.
- `scripts/site.py`: lays every talk out as one site and writes the index page, listing each talk
  by its own `<title>` and description, with its preview, its PowerPoint and PDF downloads and its links.
- `scripts/exports.py`: exports each talk as `<folder>.pptx` (one picture per slide, the script in
  the speaker notes, through `graphe:slides pptx`), `<folder>.pdf` (vector, one page per slide,
  through `graphe:slides pdf`) and a preview of its title slide. The exports are built in CI,
  never committed.

## Adding a talk

1. Start from the `/graphe:slides` starter deck in a new folder, point its `vendor/reveal/` links at
   `../vendor/reveal/`, and load `../shared/deck.css` and `../shared/deck.js` in place of its own.
2. Give the page a `<title>` and a `<meta name="description">`; the index lists the talk by them.
3. To link the talk's code, documentation or a recording from the index, add a `talk.json`:
   `{"links": {"code": "https://...", "docs": "https://...", "video": "https://..."}}`, each optional.
4. If its figures come from research artifacts, add a `figures.py` that writes them into `data/`
   and fails with `--check` when they are stale, as `federated-agents/figures.py` does. No figure
   is typed onto a slide by hand.
5. Notes go in the talk's folder as Markdown (`README.md`); the site leaves every `.md`, `.py` and
   `talk.json` out, so they stay in the repository. A video made from the talk gets its script in
   [`videos/`](videos/README.md).

## Motion

`shared/motion.css` and `shared/motion.js` give every talk one vocabulary: put `data-motion` on an
element (`pop`, `rise`, `land`, `arrive`, `grow`, `growx`, `wipe`, `draw`, `flow`, `fade`, `strike`,
`count`, or `stagger` on a parent) and it plays when its slide opens, or when the fragment holding it
appears. `data-delay`, `data-dur`, `data-step`, `data-i` and `data-iter` tune it; `data-path` sends a
`flow` dot along an SVG path. The resting style is the finished state, so exports, the phone feed,
print and reduced motion show every slide built, and counters end on the bound value. Nothing plays
for more than five seconds. The index plays a talk's title-slide loop (`thumb-loop.webp`, built by
`scripts/exports.py`) when its preview is hovered, and a talk opens out of the preview.

## Checks

`make check` runs what CI runs: lint, tests, every talk's figures against their artifacts, the
`graphe:slides` gates on every talk, the PowerPoint and PDF exports, and the site layout. CI runs it on every pull request, on
`main`, and daily, since a talk's figures can go stale through a change in another repository.
A run on `main` that passes publishes the site; one that fails publishes nothing, and the site
keeps its last good version. GitHub turns off a public repository's scheduled runs after 60
days without activity; re-enable the daily run from the Actions tab if it stops.

On Linux, the gates and renders draw text only in DejaVu (`scripts/fonts.conf`), the font CI's
runner draws the decks' system font stack in. Each machine resolves that stack to its own font,
and a slide that fits in a narrower one clips in CI. `make fonts` fails when the stack does not
resolve to DejaVu (`apt-get install fonts-dejavu-core`). Chromium reads fontconfig on Linux only,
so on macOS or Windows the gates measure the system font. The exports keep the machine's own
fonts, so a glyph DejaVu lacks still draws in the published files. `make render TALK=<folder>
OUT=<dir>` writes a built talk's slides and phone views as PNGs.

`make script-length` prints each talk's spoken script in words and minutes at 140 a minute: the
speaker notes of the slides before the FAQ, every conditional branch counted, a bound figure as
one word. The tests fail a talk over its cap (`CAP_MINUTES` in `scripts/script_length.py`).

`SPHRAGIS` points at a sphragis checkout (default `../sphragis`) and `SLIDES` at the
`graphe:slides` script in a techne checkout (default `../techne/...`).
