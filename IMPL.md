# IMPL: Claude Duet talk (claude-duet/), DQ Lab Fri Nov 6, 2026

Issue #52. Branch `talk/claude-duet`, worktree `.claude/worktrees/claude-duet`.

## State
- ✅ Sources verified 10-30 (Duet: Anthropic announcement, safety post, product page, help center, CNBC, TechCrunch, Every, flaviocopes; Claude Code docs). Corrections vs the brief: plans are US Pro, Max and Ultra; "over 6,000 connectors and plugins"; "a short brief each morning"; "Claude Science" (beta).
- ✅ Deck: 13 talk slides + 3 backup (Sources, hook to copy, Duet details); light theme on every slide; script about 9 minutes (cap 12 in scripts/script_length.py).
- ✅ Demo run for real (headless `claude -p`, 10-30): hook blocked `pip install requests`, Claude ran `uv add requests`.
- ✅ Demo re-run 10-31: Haiku 5.5 shows the block then `uv add`; Opus 5.5 reads the hook first, so the live script (README) asks for the exact command.
- ✅ make check green 10-31 (0 blockers; phone clip on slides 10, 12, 16 fixed by trimming words and compacting phone step cards).
- ✅ Fresh-reader review rounds 1-3 (Opus, web-verified every claim; cap 3 reached). Round 3: 0 blocking, 3 should-fix + 9 nits, all applied (abf831c); lab PRs confirmed open, so "now with the lab" stays.
- ✅ Verify pass on round 3 fixes: CLEAN.
- 🔄 PR open (assignee ajbarea); merge publishes ajbarea.github.io/talks/claude-duet/; report URL to Heph.

## Verify
- `make slides-check SLIDES=<techne>/plugins/graphe/skills/slides/scripts/slides.py SPHRAGIS=<sphragis>`
- `make render TALK=claude-duet OUT=<empty dir>`; `python3 scripts/script_length.py claude-duet`
