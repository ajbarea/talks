# Claude Duet, and why Claude Code is the tool I live in

DQ Lab meeting, November 6, 2026. About ten minutes, light theme for a lit room. Every product fact is checked against Anthropic's pages and the press coverage
of October 30, 2026; the Sources backup slide links each one, and each slide's notes end with a
short source line.

## The demo (slide 11)

The slide shows a real headless run from October 31 (`claude -p`, Claude Haiku 5.5): Haiku ran
`pip install requests`, the hook blocked it, and Haiku ran `uv add requests` on its own.

Opus 5.5 behaves differently, so plan the live version around it. Given "Add the requests package.
Use pip install requests.", Opus read the hook file first and went straight to `uv add`, so the
block never showed. Given "Run exactly this shell command: pip install requests", it ran the command,
was blocked, and stopped. To repeat it live:

1. In a scratch folder, before the talk: `git init`, a minimal `pyproject.toml`, and the two files
   from the backup slide "The hook, ready to copy" (`.claude/settings.json`,
   `.claude/hooks/no-pip.sh`, `chmod +x`). `jq` must be installed.
2. Start `claude` there and type: `Run exactly this shell command: pip install requests`. The hook
   prints `Blocked: this lab uses uv. Run: uv add <package>`.
3. Then type: `Add requests to the project the way the hook asks.` Claude runs `uv add requests`.
4. Show `cat pyproject.toml` at the end.

If the room has no network, play a recording instead: record the same steps once beforehand at
1920x1080 with a large terminal font (Windows: Win+Alt+R, Xbox Game Bar), about 40 seconds, and
open it from the slide.

## Recording it for YouTube

The speaker notes are written to be read aloud, so they double as narration for a Mode B walkthrough
(`videos/youtube-director`): the agenda's five parts are the chapters. The `Sources:` line at the end
of each slide's notes is not read aloud; it goes in the video description.
