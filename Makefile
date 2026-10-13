# Every talk is a folder holding an index.html; `site` lays them all out as one Pages site.
# SPHRAGIS points at a sphragis checkout for the talks whose figures come from it.
.PHONY: help setup lint fix test figures figures-check slides-check exports site check

SLIDES ?= ../techne/plugins/graphe/skills/slides/scripts/slides.py
# The browser command and the list of talks each come from the one place that defines them.
B = $(shell python3 -c "import runpy; print(runpy.run_path('$(SLIDES)')['WITH_BROWSER'])" 2>/dev/null)
TALKS = $(shell python3 scripts/site.py --list)

help:              ## List targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

setup:             ## Install the dev tools
	uv sync

lint:              ## Ruff, check and format
	uv run ruff check . && uv run ruff format --check .

fix:               ## Ruff, fixing what it can
	uv run ruff check --fix . && uv run ruff format .

test:              ## Run the tests
	uv run pytest -q

figures:           ## Regenerate every talk's figures from its artifacts
	@for f in */figures.py; do echo ">>> $$f"; python3 $$f || exit 1; done

figures-check:     ## Fail if a talk's committed figures are stale
	@for f in */figures.py; do echo ">>> $$f"; python3 $$f --check || exit 1; done

slides-check:      ## Run the graphe:slides gates on every talk
	@test -f "$(SLIDES)" || { echo "no graphe:slides script at $(SLIDES); set SLIDES" >&2; exit 1; }
	@test -n "$(TALKS)" || { echo "no talks found" >&2; exit 1; }
	@for t in $(TALKS); do echo ">>> $$t"; $(B) python $(SLIDES) check $$t/index.html || exit 1; done

exports:           ## Export every talk's .pptx, .pdf and preview into _exports/
	@test -f "$(SLIDES)" || { echo "no graphe:slides script at $(SLIDES); set SLIDES" >&2; exit 1; }
	$(B) python scripts/exports.py _exports --slides $(SLIDES)

site:              ## Lay out every talk under _site/, with the exports when they are built
	python3 scripts/site.py _site $(if $(wildcard _exports/.talks-exports),--exports _exports)

check: lint test figures-check slides-check exports site   ## Everything CI runs
