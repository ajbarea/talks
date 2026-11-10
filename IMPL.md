# IMPL: three talks, each a stronger version of itself, light by default, 2026-11-09

Branch fix/deck-looks-rollback, PR #96. Builds on the rollback commit a1494ff (the shared forge look undone).

## Slice
Each talk gets its own strong identity on a light ground for lit rooms, and every slide is audited against the bar: text 4.5:1 and up (aim 7:1), marks 3:1 or a darker outline, pale fills tested under room light, one meaning per colour, no leftover forge token. `checking-the-checker/`, `shared/deck.css` and `shared/deck.js` stay unchanged.

## Done
- ✅ claude-tooling (second pass, AJ's verdict on the orange bands): warm paper, near-black ink, Source Serif 4 titles (self-hosted, OFL), neutral cards with thin borders, clay only as accent; quiet text-tab rail with a clay underline; the dancing robot in clay on the paper. Slide 9 key still says Orange; the Desktop folders stay blue because its key says Blue.
- ✅ claude-tooling product icons beside the app names, chat, Desktop, Code and Duet from official listings and product pages, Science, Cowork and Design supplied by AJ (f046caf); sources in `claude-tooling/README.md`. Closing slide: "Product names and icons belong to Anthropic."
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

## FA deck slide 5 audit (#61, PR #62 merged 11-02)
- ✅ Slide 5 matches sphragis main b9e8ccd; live. `foreign_sized` flips to "sized" when sphragis#246 merges; no deck edit needed then.
- 📋 Refresh routine guardrails (in #61) wait on AJ's personal login (needs-you.md).

