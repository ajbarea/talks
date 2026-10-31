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
