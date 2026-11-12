# IMPL: three talks, each a stronger version of itself, light by default, 2026-11-09

Branch fix/deck-looks-rollback, PR #96. Builds on the rollback commit a1494ff (the shared forge look undone).

## Slice
Each talk gets its own strong identity on a light ground for lit rooms, and every slide is audited against the bar: text 4.5:1 and up (aim 7:1), marks 3:1 or a darker outline, pale fills tested under room light, one meaning per colour, no leftover forge token. `checking-the-checker/`, `shared/deck.css` and `shared/deck.js` stay unchanged.

## Done
- ✅ claude-tooling (second pass, AJ's verdict on the orange bands): warm paper, near-black ink, Source Serif 4 titles (self-hosted, OFL), neutral cards with thin borders, clay only as accent; quiet text-tab rail with a clay underline; the dancing robot in clay on the paper. Slide 9 key still says Orange; the Desktop folders stay blue because its key says Blue.
- ✅ claude-tooling product icons beside the app names, chat, Desktop and Duet from official listings and product pages, Code, Science, Cowork and Design supplied by AJ (f046caf); sources in `claude-tooling/README.md`. Closing slide: "Product names and icons belong to Anthropic."
- ✅ Each deck's chapter rail is its own (rules in that deck's `deck.css` only): claude-tooling text tabs, federated-agents a connected progress track with nodes, kourai-khryseai small caps with lozenges and a Greek key under the current chapter.
- ✅ federated-agents: blue is shared and travels, orange is what stays private, rivals are grey, AJ's own work navy, wrong or attack raspberry, right ink with its tick. `script.md` and notes: gold/green/blue words moved to blue/orange/grey; "Mine, in blue and orange" (the split dot on slide 7).
- ✅ kourai-khryseai: marble ground with veins, Greek key under titles and along the title and closing feet, Marcellus for titles with digits in Atkinson via unicode-range, gold and bronze, Aegean blue for context, terracotta for risk. Golden Maidens cut out of their dark ground (`img/golden-maidens-light.webp`), halo kept, no Hephaestus portrait.
- ✅ Light by default on all three: `dark` classes and dark background attributes removed from title and closing slides. Reveal copies a section's classes to its background element, so the deck.css title pseudo-elements are scoped to `section.`.
- ✅ Audit tool in the session scratchpad (per-slide contrast and mark sampling); room-light closest-pair test reproduces PR #92's 7.6 and 20.7.
- ✅ README look section updated.

- ✅ Review fixes (11-10): closing slides centered again (`fit-content(620px) 424px`, shared `justify-content: center`); claude-tooling back on system `--sans`/`--mono`; every slides-check WARN cleared (kicker, owner line and PR chips 0.64em; phone kicker, owner, details table, FAQ, back link and backup `.small` raised to 12px+); README and this file match the code.

## Next
- 📋 Independent Opus verify of the review fixes; then Heph and AJ merge. Icon nits for AJ: faint edge on `icon-claude-science.png`, square corners on `icon-claude-design.png`.

## Verify
- `SLIDES=<techne>/plugins/graphe/skills/slides/scripts/slides.py SPHRAGIS=<sphragis> make check`, then `make lint`.
- Render every slide at 1920x1080 and on a phone; read the sheets. `document.getAnimations()` on each title: robot, motif `m-flow`, halo `k-ring`; none under reduced motion.
- Per-slide text against main: only the title byline moved (earlier pass) and the colour words above changed.

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

### Now: the lab as its own page, issue #116, PR #117, branch talk/qml-lab-app
Spec: issue #116; Heph's addendum 2 (points 1-6) and fixes 1-5; bar: techne `plugins/graphe/_shared/exemplars.md`; model: Pharos explorer.
- ✅ A-D. `lab/` page: six tabs, hash state, timeline (play/pause/step/scrub/speed), restart table, 1×8 vs 8×1 race, many-draw rows in a Worker, every paper run; `figures.py` writes `lab/data/runs.js` (+ `settings`: seeds, restarts, budget restarts; `bestSmall` = best of the paper's usual restarts).
- ✅ E. Deck lab slides: `iframe.lab-frame[data-lab-src]` loaded only by `lab-embed.js` (Reveal lazy-loads and unloads `data-src`). Same-origin messages, origin + source checked. Still (paper figure at 600 px + https "Try it live" link) from file://, in print, on phones/sideways (deck.js's own queries) and in speaker previews. Embed: forced light, "Toy" tag on the panel, keys handed to the deck stop there.
- ✅ Review round 1 (Opus): fixed the blocker (a tab switch froze the other view's rows: jobs now cancel cleanly and rerun on show; Worker failure resumes on the main thread) and every should-fix (listener leaks on reroute, one document key handler for the shown view, typing in the embedded number box, paper captions from data, runs tab roving tabindex + 24 px targets, per-frame DOM work cached, frame shrinks, CSV `\r`).
- ✅ Review round 2 (fresh Opus): nothing blocking; fixed both should-fixes (controls and many-draw rows resync to the shared state when a tab is shown again: knob `.sync()`, `ensure()` reruns on a count mismatch) and the nits (Worker hears `{cancel:id}`, failed Worker terminated, toy literals from `Q.TOY`). Commit 7ca17d0.
- ✅ Verify pass on round 2: fixes confirmed (jsdom harness); new should-fixes fixed in the last commit: the job runner moved to `lab/jobs.js` (no DOM) and is tested in CI by `tests/qfl_jobs_harness.js` (real worker.js in a vm, fake Worker; supersede, midway, cancel alone, Worker failure, no Worker, shouldRun; six mutants all caught); in a slide the shots list blurs only after a pointer pick (keyboard users keep it); toy-note test checks the restart count too.
- 📋 Next session: (1) browser smoke of the last commit, under the heavy lock with `playwright==1.63.0`, serving the worktree (`python3 -m http.server <free port>`): lab reps tab n=200, switch to Shots and back, rows finish "in a background thread", no console errors; deck shots slide, focus the frame's select, ArrowUp twice changes it twice and the slide does not move. (2) One verify pass (fresh Opus) on the last commit's diff only. (3) Mark #117 ready, CI green, merge (squash), wait for deploy, live check https://ajbarea.github.io/talks/qfl-privacy/ and /lab/ at 1920 and 390, console clean. (4) Report to Heph (`fleet send`, orchestrator.pane): PR, merge SHA, live URL checked, measurements below. (5) Queue line ✅, Desktop `CSCI-739 talk/` PDF refresh if exports changed, `fleet done`.

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
- 📋 After Nov 20: recheck the "still open" list (slide 13), the GitHub replication's members, and `figures-check` for drift.
