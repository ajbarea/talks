# talks

AJ Barea's research talks as web decks (reveal.js), one folder per talk, published to https://ajbarea.github.io/talks/. Humans start with [README.md](README.md), which covers the layout, adding a talk, motion and checks.

## Commands

`make help` lists every target; `make setup` installs the dev tools. Before a PR run `make check`, which is everything CI runs (lint, tests, figures, QR codes, the slide gates, exports and the site) and drives Chromium. It reads `SLIDES` (the `graphe:slides` script, default `../techne/...`) and `SPHRAGIS` (default `../sphragis`); from a worktree under `.claude/worktrees/`, set both to the real checkouts, or the figure tests skip and the gates stop.

## Rules

- Work in a git worktree on a branch and open a pull request.
- Never commit `COMMITS.md` (a local scratchpad), `_site/` or `_exports/`; the `.pptx`, `.pdf` and preview exports are built in CI.
- A talk whose figures come from research artifacts has a `figures.py` that writes them into its `data/` (`federated-agents`, from sphragis); no figure is typed by hand. `make figures` regenerates them and `make figures-check` fails on stale ones.
- `vendor/reveal/` is reveal.js (version in `vendor/reveal/VERSION`), shared by every talk; changes go in `shared/` or the talk's own `deck.css`.
- Each talk's QR codes are generated into its `index.html`: `make qr` rewrites them and `make qr-check` fails on stale ones. A passing run on `main` publishes the site.
- Shared behaviour and base styles live in `shared/`; a talk's own `deck.css` holds only what is particular to it.
- Each talk needs a `<title>` and a `<meta name="description">`; the index page lists the talk by them.
- A talk's spoken script has a length cap (`CAP_MINUTES` in `scripts/script_length.py`); `make script-length` reports it.
- The slide gates and renders expect DejaVu text on Linux; `make fonts` checks it.
- A video script in `videos/` follows `videos/vids-rules.md`; `make videos-check` lints it and every upload `description.txt`, and `make test` runs the same lints. After an upload, `make videos-verify ID=...` checks the public page.

## State

`federated-agents/README.md` holds that talk's own notes.
