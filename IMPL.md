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

## Claude Duet talk (claude-duet/), LDQIS Fri Nov 6
- ✅ #52 / #54 merged 11-01; live at https://ajbarea.github.io/talks/claude-duet/.
- 🔄 #63 (branch duet-revise): AJ's slide-by-slide read. Done in the working tree: LDQIS kicker; new title; dancing robot SVG; agenda of five parts with a question pause (slide 8) and a discussion pause (slide 12); slide 3 is now the five-apps map (contribution); slide 4 shows a real Duet card; slide 7 table adds chat and Science; slide 10 reworded for Dr. Reznik, registered report replaced by hook moments (33 vs rivals 6 to 21, data in deck-data.js `hooks`). Script 1398 words (cap 1400).
- 📋 Next: `make slides-check` and render (both behind /tmp/fleet-heavy.lock), look at every slide at 1920 and phone, fresh-reader review (cap 3), PR assigned to ajbarea, merge, shots of slides 1, 2, 7, 10 to fleet-briefing/shots/2026-11-02/.
- 📋 techne graphe:slides question vs discussion pause: branch slides-pauses in techne.
- 📋 Present Fri 11-06 about 2:00; live demo script in `claude-duet/README.md`.
