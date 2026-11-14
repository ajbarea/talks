# IMPL: the talks landing page as a cover flow, 2026-11-11

Branch feat/coverflow, issue #101, PR #102 (assigned ajbarea). Only the index page changes (`scripts/site.py`, `scripts/index/`, the loop count in `scripts/exports.py`); no deck is touched. Do NOT merge: AJ approves the look first.

## Slice
The deck picker is a cover flow: centered talk large, neighbours turned in 3D with reflections on a dark stage that fades into the page; keys, swipe, trackpad, wheel over the covers, mouse drag and clicks glide; the centered talk plays its loop once; title, description, one "Open the deck" and small labelled chips below. No script: the old cards.

## Done
- ✅ Scroll-snap strip + CSS view timelines (transform/opacity only); script settles on scrollend, APG carousel roles, inert, one polite announcement, focus carried to the new talk.
- ✅ Four review rounds (a11y, perf, UX, verify x3); every Blocking and Should-fix fixed or kept by a documented choice in the PR body; Copilot's two points declined with reasons.
- ✅ `make site-check` (in `make check` and CI): 40+ checks incl. axe in both themes, fold for every talk, resize, drags, focus rings, chip borders; new checks mutation-proven.
- ✅ Frame timing: p95 16.7 ms at 1920 and on a 4x phone; 44rem cover cap and flat shade chosen by measurement.
- ✅ Shots in fleet-briefing/shots/2026-11-11/talks-coverflow-*.

## Next
- 📋 Round-5 read (ceiling) result; then AJ judges the look on #102; merge only on his yes.

## Verify
- With `_exports/` present: `make site`, `flock -o /tmp/fleet-heavy.lock make site-check SLIDES=...`, `make lint`, `uv run pytest -q tests/test_site.py`.
- Frame timing: the rAF + trace script from the PR's Measurements section (headless Chromium, 1920 and 390x844 at 4x CPU).

## Next (not started)
- Custom thumbnails for Tier 1 uploads that still show an auto frame (upload-package.md recipe).
- New uploads: write `description.txt`, lint, upload, `make videos-verify`.

## How the refresh was applied (reuse for the next sweep)
- Studio through the Playwright MCP browser; if Studio shows "Create channel", pick @AJBarea in /channel_switcher.
- Type descriptions line by line (`keyboard.insertText` + Enter); `fill` does not register in Studio. Tags: insertText, then a real "," key per tag.
- The Studio renderer reached 3.5 GB within about a dozen edits (ps, 10-30) against a 5 GB session cap: batches of 6 videos, `browser_close` between batches.
- Read every edit back after a reload; skip Save when nothing changed, so reruns are safe.
- `videos/channel/refresh.py extract META PLAYLISTS` rebuilds the tables from a fresh `yt-dlp` pull (`uvx yt-dlp --js-runtimes node ...`); it refuses an upload that fits no tier.

## QFL privacy talk (qfl-privacy/), CSCI-739 QML
#110 (a5b7cfe) and round 2 #113 (4544e62) merged; live at https://ajbarea.github.io/talks/qfl-privacy/ (checked 11-12 at 1920/1366/1280/390: zero overlap, console clean). Desktop `CSCI-739 talk/`: deck PDF, explainer PDF (rebuilt after #113), `live-url.txt`. Talks Tue Dec 1, 13 to 15 min. `QFL` = `~/ajsoftworks/csci739-qfl-privacy/.claude/worktrees/qml-src` (detached at origin/main).

### Done: the lab as its own page, #116, PR #117, merged da6bf34 (11-12)
Live at https://ajbarea.github.io/talks/qfl-privacy/lab/ and in the deck's lab slides (6-8). Checked live 11-12 at 1920 and 390: six tabs, 200-input rows in a background thread (2.4 s), deck frames load on slides 6-8, phone deck shows the paper's figure and "Try it live", no sideways scroll, console clean; the PDF prints every lab slide as the figure plus the link. Desktop `CSCI-739 talk/`: deck PDF and explainer PDF refreshed. Shots: fleet-briefing `shots/2026-11-12/talks-116-*`.
- Review: three Opus rounds plus four verify passes; the last ones fixed clicker keys from a frame (they move the deck as Reveal's own keys do; keys Reveal ignores stay with the browser; a list picked by mouse, touch or label hands the arrows back after one change, Tab keeps it) and the many-draw job tests (thread-path cancel, failure after cancel, every key handler leaves Ctrl, Meta and Alt alone).
- Next for this talk: the companion pages job (fleet queue "Paper companion pages"), paper follow-up csci739-qfl-privacy#31, rehearsal before Tue 12-01.

Measured (toy, hidden inputs 1-200): restarts that hit 82/75/68/55% at 1×8/2×4/4×2/8×1, best-of-10 recovers 198-200 at every setting (stated on the page); restarts 1/2/5/10/20 → 113/161/191/200/200 recovered; shots 10/100/1000/exact → 147/193/200/200 within 0.2 rad. One search 4.5 s + 0.4 s fade. Script 10.7 of 15 min.

### Verify
- `QFL=<checkout> uv run pytest -q tests/test_qfl_lab.py`; `QFL=<checkout> python3 qfl-privacy/figures.py --check`; `python3 scripts/script_length.py qfl-privacy --check`.
- Gates as CI runs them: techne pinned in `.github/workflows/site.yml` (`git archive <pin> plugins/graphe`), then under `flock -o /tmp/fleet-heavy.lock`: `make check SLIDES=<that slides.py> SPHRAGIS=<sphragis> QFL=<checkout>`.
- Drive scripts (session scratchpad, recreate if lost; pin `playwright==1.63.0`, graphe's pin, whose browsers are installed): each lab slide at 1920/1366 over http, 390/360 (still), file:// (still); app tabs at 1920 and 390 (no sideways scroll); tab switch mid-run; Back/Forward then Space once.

## Checking the Checker talk (checking-the-checker/), CISC-810 Group 1
- ✅ #82: 8 main slides + 12 backup, from the revised manuscript and its evidence/ only (every value in `data/deck-data.js` with its source); `figs.js` draws the charts and recounts the counts the titles state. Script 966 words, cap 7 minutes.
- ✅ Five rounds of independent Opus review against the rubric and the manuscript; round 5 clean.
- ✅ #83 conclusion slide (key results, open problems); marked `data-conclusion` on style/forge.
- 📋 Upload `Desktop/CISC-810 talk/checking-the-checker.pdf` to myCourses by Mon Nov 9 23:59 (AJ); revised slides due Nov 18. Rehearsal brief in the same folder.
- 📋 Title says "November 2026": set the exact date once AJ's slot (Nov 10, 12 or 17) is known.
- 📋 The manuscript folder is outside this repo, so CI cannot recheck the numbers; recheck by hand if the paper changes before Nov 18.

## Claude Duet talk (claude-tooling/), LDQIS Fri Nov 6
- ✅ #52 / #54 merged 11-01; ✅ #63 / #64 merged 11-02 (AJ's slide-by-slide read: LDQIS, the five Claude apps, robot title, question pause on slide 8 and discussion pause on slide 12, slide 10 for Dr. Reznik with the hooks card). Live at https://ajbarea.github.io/talks/claude-tooling/; 14 talk slides and 4 backup.
- ✅ techne#269 / #270 merged: graphe:slides tells a question pause from a discussion pause.
- ✅ #70 / #71 third pass from AJ's notes (11-02): slide 6 map has Claude Design inside Claude chat and Cowork moving in by plan (Team and Free not yet); "your lab"; slide 13 "Four steps put Claude Code to work in your own repository" with an accurate privacy line; the pip demo became a `.env` hook adapted from Anthropic's hooks guide (real Opus 5.5 run). Script 1,398 of 1,400 words.
- ✅ #73 retitle merged; ✅ #76 deck/duet-rebalance (11-03, AJ: "cover them all briefly, then Claude Code in depth", "chronological order", title "Five Claude apps, one favorite"): five apps in launch order on slide 3 (Jul 2023, Oct 2024, Feb 2025, Jun 2026, Oct 2026, each checked against Anthropic's announcements); map now slide 4; Duet down to one slide (5); old "can't see your files" table and the cut Duet facts moved to backup. 12 talk slides, 5 backup; pause slide 6, demo 9, discussion 10.
- ✅ #80 deck/duet-no-pauses (11-04, AJ: no agenda mentions pauses; no mid-talk question or discussion stops; questions at the end): pause slide cut, agenda "Five parts in about ten minutes", discussion slide moved to the first backup slot for a quiet Q&A. 10 talk slides, 6 backup; Duet 5, demo 8.
- ✅ #81 one main point; style/forge adds its conclusion slide and cuts the script to 1,169 words.
- 📋 FILL for AJ: his own example for Claude chat (slide 3) and Claude Science (slide 6); both slides say "A lab could" until then.
- 📋 Before 11-06: recheck whether the Cowork merge reached Team plans (claude.com/resources/articles/cowork-is-now-claude; 11-04: Enterprise only, Team still to follow).
- 📋 Present Fri 11-06 about 2:00; live demo script in `claude-tooling/README.md`.
- 📋 Hook counts on slide 9: Claude Code 33 rechecked 11-04, rivals as of 11-02 (data/deck-data.js `hooks`); recount from each tool's hooks page before any later reuse.
- 📋 Optional YouTube cut (youtube-director Mode B): notes are the narration; each slide's `Sources:` line goes in the description.

## Federated Agents deck accuracy pass (#99, PR #100, branch deck/fa-big-accuracy)
- ✅ Every slide, note, script line and FAQ agrees with papers 1b6e349: development verdicts cut (slide 8 rewritten, forest slide cut, FAQ statuses gone), H2 = Qt's C++ vs Chromium, novelty = the report's sentence, planted check over three orgs (figures.py reads Qt), N fixed, VENUE dates, two of four attacks built (min-loss, disaggregation planned), "house style".
- ✅ figures.py: unbound dev-verdict derivations and their tests removed; forest/trend CSS removed. 15 talk slides, 17 backups; script 1,054 words.
- ✅ 5 Opus rounds + 2 verify passes, last clean; Copilot's 4 rows rejected (federated-design scope). `make check` green, PDF 0 overlaps.
- 📋 Heph merges and deploys PR #100.
- Verify: `make check` with SLIDES=<techne>/plugins/graphe/skills/slides/scripts/slides.py SPHRAGIS=<sphragis main>; renders at 1920 and phone; overlap check = pdftotext -bbox-layout lines overlapping by over half a line.

## Federated Agents: Step One (federated-agents-step-one/), LDQIS Fri Nov 13
- 📋 Branch talk/federated-agents-step-one (#97, open, Heph merges): lab explainer deck, IBM Plex on white, spot inks with one job each (ultramarine the plan, magenta hatch sealed or open, green found, yellow the lab, grey and ink context). Present Nov 13, 2 pm.
- ✅ 11-10 orchestrator review, all four fixed: aligned with papers 1b6e349 (H2 = Qt vs Chromium everywhere; null table = the paper's Table II; dev-verdict backup replaced by "How small an effect can each test detect?" from the same sizing artifacts harvest.py reads); slides cut to claim + evidence (max ~90 words incl. figure labels); builds on slides 6, 9, 10, 11, 15 (▶ in script.md marks each click; reduced motion keeps the steps, drops the fade); PDF footnote overlap fixed in this talk's deck.css (reveal print sets padding 0 !important).
- Verify: `make check` with SLIDES (newest graphe cache, `ls -td`) and SPHRAGIS=~/ajsoftworks/sphragis; `python3 scripts/script_length.py federated-agents-step-one --check` (cap 1,400 words; at ~1,390, so any added sentence needs a cut); render and read every slide at 1920 and phone; PDF text-overlap check = pdftotext -bbox-layout, lines overlapping by more than half a line.
- ✅ 11-12 slide 5 "What Sphragis builds" (#118, PR #119 merged ea6dfb3): one OpenStack training-window example (code only; sphragis publishes no review text), examples per organization, the label audit on OpenStack's 77 checked items as the report quotes it (the pooled 152 was withdrawn in sphragis, research log 2026-10-15). `figures.py` generates it all and checks each count against `label-audit-v2-openstack.json`; tests in `tests/test_fa_step_one_example.py`.
- ▶ 11-12 polish (#120, PR #121): dot-plot labels, caption stacking, focus ring, phone timeline; plus round-4 minors. Then live check at 1920/1280 and the stepped PDF to Desktop "To review/Friday lab explainer.pdf" (`scripts/stepped_export.py`).
- Worktrees need `SPHRAGIS=~/ajsoftworks/sphragis` (the default path resolves wrongly inside .claude/worktrees). Live check helper: `~/.local/state/sphragis-slide/livecheck.py`.
- 📋 After Nov 20: recheck the "still open" list (slide 13), the GitHub replication's members, and `figures-check` for drift.
