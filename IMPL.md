# IMPL: channel refresh (talks #44), branch videos/channel-refresh

## State (2026-10-29 night)
- ✅ #43 merged as #45 (upload package, `make videos-verify ID=... [AI=1] [AUTO_THUMB=1]`).
- ✅ Tier 2 (113 concert uploads) and Tier 3 (36 gaming clips): `videos/channel/refresh.py` renders from `music.tsv` / `gaming.tsv`; `tests/test_channel_refresh.py` lints every rendered description.
- ✅ Tier 1 (20 videos) LIVE 10-30: descriptions, tags, 6 title fixes, 5 category fixes (Webots 1-5 -> Education), 19 end screens (Subscribe + named video; the 36 s clone video has none), 20 pinned questions; `make videos-verify` 4/4 on all 20. UtOHEHz2pWw is TTS-narrated (Microsoft Read Aloud, AJ via Heph): narrator line + AI use = yes.
- ✅ PR #46 opened; Heph spot-checked review.md (clean).
- 📋 Tier 2 and 3 next.

## Apply (Playwright MCP, profile signed in; pick @AJBarea in /channel_switcher if Studio says "Create channel")
1. Tier 1, one video at a time: `studio.youtube.com/video/<id>/edit`, replace description (and title where review.md says new), tags, category, Save; end screen (Subscribe + the named video); pinned comment on the watch page. Then `make videos-verify ID=<id> [AI=1] AUTO_THUMB=1` and fix what fails.
2. Report to Heph by tmux when Tier 1 is live.
3. Tier 2 and 3: `python3 videos/channel/refresh.py render <dir>`, paste each `<id>-description.txt`; bulk-set category Music on concert uploads (24 sit in Education) and Education on Webots Labs 1-5 (in Gaming).
4. Report to Heph at the end; close #44 from the PR.

## Inputs (not committed)
- `.work/meta.jsonl`: yt-dlp pull of all 169 public videos (10-29). `.work/subs/<id>.txt`: Tier 1 captions. `.work/playlists.tsv`: playlist membership.
- Re-pull: `uvx yt-dlp --js-runtimes node --flat-playlist ...`; captions: `uvx yt-dlp --js-runtimes node --write-auto-subs --skip-download`.
