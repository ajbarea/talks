# IMPL: Claude Duet talk (claude-duet/), DQ Lab Fri Nov 6, 2026

Issue #52. Branch `talk/claude-duet`, worktree `.claude/worktrees/claude-duet`.

## State
- ✅ Sources verified 10-30 (Duet: Anthropic announcement, safety post, product page, help center, CNBC, TechCrunch, Every, flaviocopes; Claude Code docs). Corrections vs the brief: plans are US Pro, Max and Ultra; "over 6,000 connectors and plugins"; "a short brief each morning"; "Claude Science" (beta).
- ✅ Deck: 13 talk slides + 3 backup (Sources, hook to copy, Duet details); light theme on every slide; script about 9 minutes (cap 12 in scripts/script_length.py).
- ✅ Demo run for real (headless `claude -p`, 10-30): hook blocked `pip install requests`, Claude ran `uv add requests`.
- 📋 make check, fresh-reader review (cap 3 rounds), PR, report to Heph.

## Verify
- `make slides-check SLIDES=<techne>/plugins/graphe/skills/slides/scripts/slides.py SPHRAGIS=<sphragis>`
- `make render TALK=claude-duet OUT=<empty dir>`; `python3 scripts/script_length.py claude-duet`
