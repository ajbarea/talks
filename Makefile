# Every talk is a folder holding an index.html; `site` lays them all out as one Pages site.
# SPHRAGIS points at a sphragis checkout for the talks whose figures come from it.
.PHONY: help setup lint fix test figures figures-check slides-check site check

SLIDES ?= ../techne/plugins/graphe/skills/slides/scripts/slides.py
B := uv run --no-project --quiet --with playwright==1.63.0 --with axe-playwright-python==0.1.8 --with pillow
TALKS := $(filter-out _% vendor,$(patsubst %/index.html,%,$(wildcard */index.html)))

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
	@for t in $(TALKS); do echo ">>> $$t"; $(B) python $(SLIDES) check $$t/index.html || exit 1; done

site:              ## Lay out every talk under _site/
	python3 scripts/site.py _site

check: lint test figures-check slides-check site   ## Everything CI runs
