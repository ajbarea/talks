# talks

AJ Barea's research talks as web decks, published at https://ajbarea.github.io/talks/.

| Talk | Link |
|---|---|
| Federated Agents | https://ajbarea.github.io/talks/federated-agents/ |

Each talk opens in any browser, with no network needed once loaded. Press `S` for the speaker
view (the script, a timer and the next slide), `O` for the overview and `F` for full screen. A
link like `.../federated-agents/#/5` opens a given slide.

## Layout

- One folder per talk, holding its `index.html`, `deck.css`, `deck.js` and `data/`. The folder
  name is the talk's address.
- `vendor/reveal/`: reveal.js, shared by every talk.
- `scripts/site.py`: lays every talk out as one site and writes the index page, listing each talk
  by its own `<title>` and description.

## Adding a talk

1. Start from the `/graphe:slides` starter deck in a new folder, and point its `vendor/reveal/`
   links at `../vendor/reveal/`.
2. Give the page a `<title>` and a `<meta name="description">`; the index lists the talk by them.
3. If its figures come from research artifacts, add a `figures.py` that writes them into `data/`
   and fails with `--check` when they are stale, as `federated-agents/figures.py` does. No figure
   is typed onto a slide by hand.

## Checks

`make check` runs what CI runs: lint, tests, every talk's figures against their artifacts, the
`graphe:slides` gates on every talk, and the site layout. CI runs it on every pull request, on
`main`, and daily, since a talk's figures can go stale through a change in another repository.
A run on `main` that passes publishes the site; one that fails publishes nothing, and the site
keeps its last good version.

`SPHRAGIS` points at a sphragis checkout (default `../sphragis`) and `SLIDES` at the
`graphe:slides` script in a techne checkout (default `../techne/...`).
