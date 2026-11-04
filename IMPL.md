# IMPL: Halloween upload package (videos/05-haunted-terminal), 2026-10-30

## State
- ✅ #43/#45 upload package; ✅ #44/#46 channel refresh (all 169 public videos).
- AI disclosure: zc_W9tCGO1I (Google Vids avatar) and UtOHEHz2pWw (Microsoft Read Aloud TTS, per AJ); both have the narrator line and "AI use" set.
- ✅ 05-haunted-terminal: description.txt, short-description.txt, metadata.md, checklist.md, delivered.md, TOOLING-NOTES.md. Media (two mp4s, srt, three thumbnails) in `Desktop/spooky-youtube/`, never committed.
- 📋 Upload both cuts Sat Oct 31 (16:9 at 10:00 AM ET, Short at 12:00 PM ET), tick AI use, then `make videos-verify ID=<id> AI=1`.

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
- 📋 deck/checking-the-checker: 8 main slides + backup, from the revised manuscript and its evidence/ only (every value in `data/deck-data.js` with its source); `figs.js` draws the charts and recounts the counts the titles state. Script cap 7 minutes.
- 📋 Independent Opus review against the assignment rubric and the manuscript, until a round is clean; then PR, merge on green, confirm live.
- 📋 Upload slides to myCourses by Mon Nov 9 23:59 (AJ); PDF and .pptx in `Desktop/CISC-810 talk/`, with `rehearsal-brief.md`. Revised slides due Nov 18.
- 📋 Title says "November 2026": set the exact date once AJ's slot (Nov 10, 12 or 17) is known.

## Claude Duet talk (claude-duet/), LDQIS Fri Nov 6
- ✅ #52 / #54 merged 11-01; ✅ #63 / #64 merged 11-02 (AJ's slide-by-slide read: LDQIS, the five Claude apps, robot title, question pause on slide 8 and discussion pause on slide 12, slide 10 for Dr. Reznik with the hooks card). Live at https://ajbarea.github.io/talks/claude-duet/; 14 talk slides and 4 backup.
- ✅ techne#269 / #270 merged: graphe:slides tells a question pause from a discussion pause.
- ✅ #70 / #71 third pass from AJ's notes (11-02): slide 6 map has Claude Design inside Claude chat and Cowork moving in by plan (Team and Free not yet); "your lab"; slide 13 "Four steps put Claude Code to work in your own repository" with an accurate privacy line; the pip demo became a `.env` hook adapted from Anthropic's hooks guide (real Opus 5.5 run). Script 1,398 of 1,400 words.
- ✅ #73 retitle merged; ✅ #76 deck/duet-rebalance (11-03, AJ: "cover them all briefly, then Claude Code in depth", "chronological order", title "Five Claude apps, one favorite"): five apps in launch order on slide 3 (Jul 2023, Oct 2024, Feb 2025, Jun 2026, Oct 2026, each checked against Anthropic's announcements); map now slide 4; Duet down to one slide (5); old "can't see your files" table and the cut Duet facts moved to backup. 12 talk slides, 5 backup; pause slide 6, demo 9, discussion 10.
- ✅ #80 deck/duet-no-pauses (11-04, AJ: no agenda mentions pauses; no mid-talk question or discussion stops; questions at the end): pause slide cut, agenda "Five parts in about ten minutes", discussion slide moved to the first backup slot for a quiet Q&A. 10 talk slides, 6 backup; Duet 5, demo 8.
- 📋 talk/duet-one-point (11-04, AJ approved the structure): one main point, "each Claude app is built for a different place your work lives; pick the app by the place, and for code start with Claude Code". 12 talk slides: title, the map (contribution), one slide per app in launch order (does / use / limit), which-app table, favorite, demo, try one, thank you. No agenda slide. 9 backup. Script 1,393 of 1,400 words. Every date rechecked 11-04 on Anthropic's pages (none changed); structure, sources and the FILL list in `claude-duet/README.md`.
- 📋 FILL for AJ: his own example for Claude chat (slide 3) and Claude Science (slide 6); both slides say "A lab could" until then.
- 📋 Before 11-06: recheck whether the Cowork merge reached Team plans (claude.com/resources/articles/cowork-is-now-claude; 11-04: Enterprise only, Team still to follow).
- 📋 Present Fri 11-06 about 2:00; live demo script in `claude-duet/README.md`.
- 📋 Hook counts on slide 9: Claude Code 33 rechecked 11-04, rivals as of 11-02 (data/deck-data.js `hooks`); recount from each tool's hooks page before any later reuse.
- 📋 Optional YouTube cut (youtube-director Mode B): notes are the narration; each slide's `Sources:` line goes in the description.

## FA deck slide 5 audit (#61, PR #62 merged 11-02)
- ✅ Slide 5 matches sphragis main b9e8ccd; live. `foreign_sized` flips to "sized" when sphragis#246 merges; no deck edit needed then.
- 📋 Refresh routine guardrails (in #61) wait on AJ's personal login (needs-you.md).
