# IMPL: channel refresh (talks #44), done 2026-10-30

## State
- ✅ #43 merged as #45: upload package, `make videos-verify ID=... [AI=1] [AUTO_THUMB=1]`.
- ✅ #44 live on all 169 public videos (PR #46): 20 Tier 1 by hand (descriptions with caption chapters, tags, 6 title fixes, 19 end screens, 20 pinned questions), 113 concert uploads from one template, 36 gaming clips formatting only. Categories: Webots Labs 1-5 to Education, 24 concert uploads to Music.
- AI disclosure: zc_W9tCGO1I (Google Vids avatar) and UtOHEHz2pWw (Microsoft Read Aloud TTS, per AJ); both have the narrator line and "AI use" set.

## Next (not started)
- Custom thumbnails for Tier 1 uploads that still show an auto frame (upload-package.md recipe).
- New uploads: write `description.txt`, lint, upload, `make videos-verify`.

## How the refresh was applied (reuse for the next sweep)
- Studio through the Playwright MCP browser; if Studio shows "Create channel", pick @AJBarea in /channel_switcher.
- Type descriptions line by line (`keyboard.insertText` + Enter); `fill` does not register in Studio. Tags: insertText, then a real "," key per tag.
- The Studio renderer reached 3.5 GB within about a dozen edits (ps, 10-30) against a 5 GB session cap: batches of 6 videos, `browser_close` between batches.
- Read every edit back after a reload; skip Save when nothing changed, so reruns are safe.
- `videos/channel/refresh.py extract META PLAYLISTS` rebuilds the tables from a fresh `yt-dlp` pull (`uvx yt-dlp --js-runtimes node ...`); it refuses an upload that fits no tier.
