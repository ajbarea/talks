# Every talk is a folder holding an index.html; `site` lays them all out as one Pages site.
# SPHRAGIS points at a sphragis checkout for the talks whose figures come from it.
.PHONY: help setup lint fix test videos-check script-length figures figures-check qr qr-check fonts slides-script slides-check render exports site check

SLIDES ?= ../techne/plugins/graphe/skills/slides/scripts/slides.py
# The browser command and the list of talks each come from the one place that defines them.
# On Linux the gates and renders draw text only in DejaVu (scripts/fonts.conf), the font CI draws,
# so a slide that fits here fits there.
# Exports keep the machine's own fonts, so a glyph DejaVu lacks still draws in the published files.
FONTS = FONTCONFIG_FILE="$(CURDIR)/scripts/fonts.conf"
BROWSER = $(shell python3 -c "import runpy; print(runpy.run_path('$(SLIDES)')['WITH_BROWSER'])" 2>/dev/null)
B = $(FONTS) $(BROWSER)
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

videos-check:      ## Lint every video script against videos/vids-rules.md
	python3 videos/check_script.py

script-length:     ## Each talk's spoken script in words and minutes; fails a talk over its cap
	@for t in $(TALKS); do python3 scripts/script_length.py $$t || exit 1; done

figures:           ## Regenerate every talk's figures from its artifacts
	@for f in */figures.py; do echo ">>> $$f"; python3 $$f || exit 1; done

figures-check:     ## Fail if a talk's committed figures are stale
	@for f in */figures.py; do echo ">>> $$f"; python3 $$f --check || exit 1; done

qr:                ## Write each talk's QR codes into its index.html
	uv run python scripts/qr.py

qr-check:          ## Fail if a talk's QR codes are missing or stale
	uv run python scripts/qr.py --check

fonts:             ## Fail unless the gates' fonts resolve to DejaVu, as CI's do (Linux only)
	@[ "$$(uname)" = Linux ] || { echo "fonts: not Linux; the gates measure this machine's own fonts"; exit 0; }; \
	bad=; for f in system-ui system-ui:bold sans-serif Helvetica; do \
	  test "$$($(FONTS) fc-match -f '%{family[0]}' $$f)" = "DejaVu Sans" || bad=1; done; \
	test "$$($(FONTS) fc-match -f '%{family[0]}' monospace)" = "DejaVu Sans Mono" || bad=1; \
	test -z "$$bad" || { echo "the gates' fonts do not resolve to DejaVu; install it: apt-get install fonts-dejavu-core" >&2; exit 1; }; \
	echo "text drawn in DejaVu Sans (this machine's own: $$(fc-match -f '%{family[0]}' system-ui))"

slides-script:
	@test -f "$(SLIDES)" || { echo "no graphe:slides script at $(SLIDES); set SLIDES" >&2; exit 1; }

slides-check: slides-script fonts ## Run the graphe:slides gates on every talk
	@test -n "$(TALKS)" || { echo "no talks found" >&2; exit 1; }
	@for t in $(TALKS); do echo ">>> $$t"; $(B) python $(SLIDES) check $$t/index.html || exit 1; done

render:            ## Render one talk's slides and phone views: make render TALK=federated-agents OUT=/tmp/web-render
	@[ -n "$(TALK)" ] && [ -n "$(OUT)" ] || { echo "set TALK and OUT" >&2; exit 1; }
	@$(MAKE) --no-print-directory slides-script fonts site
	$(B) python $(SLIDES) render _site/$(TALK)/index.html $(OUT)

exports: slides-script ## Export every talk's .pptx, .pdf and preview into _exports/
	$(BROWSER) python scripts/exports.py _exports --slides $(SLIDES)

site:              ## Lay out every talk under _site/, with the exports when they are built
	python3 scripts/site.py _site $(if $(wildcard _exports/.talks-exports),--exports _exports)

check: lint test figures-check qr-check slides-check exports site   ## Everything CI runs
