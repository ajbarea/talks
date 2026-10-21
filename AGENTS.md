# talks

AJ Barea's research talks as web decks (reveal.js), one folder per talk, published to https://ajbarea.github.io/talks/. Humans start with [README.md](README.md), which covers the layout, adding a talk, motion and checks.

## Commands

`make help` lists every target. Before a PR run `make lint`, `make test` and `make check` (everything CI runs). `make setup` installs the dev tools.

## Rules

- Work in a git worktree on a branch and open a pull request.
- Never commit `COMMITS.md` (a local scratchpad), `_site/` or `_exports/`; the `.pptx`, `.pdf` and preview exports are built in CI.
- Figures on a slide come from the talk's `figures.py` into its `data/`; never type one by hand. `make figures` regenerates them and `make figures-check` fails on stale ones.
- `vendor/reveal/` is reveal.js, shared by every talk; do not edit it.
- Shared behaviour and base styles live in `shared/`; a talk's own `deck.css` holds only what is particular to it.
- Each talk needs a `<title>` and a `<meta name="description">`; the index page lists the talk by them.
- A talk's spoken script has a length cap (`CAP_MINUTES` in `scripts/script_length.py`); `make script-length` reports it.
- The slide gates and renders expect DejaVu text on Linux; `make fonts` checks it.

## State

`federated-agents/README.md` holds that talk's own notes.
