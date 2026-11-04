# Five Claude apps, one favorite

LDQIS meeting, November 6, 2026. About ten minutes, light theme for a lit room.

**Main point:** each Claude app is built for a different place your work lives. Pick the app by the place, and for code, Claude Code is the one I'd start with. Every main slide serves it.

## Structure

| # | Slide | Chapter |
|---|---|---|
| 1 | Title: Five Claude apps, one favorite (robot, Follow-along QR) | |
| 2 | The map: five places, one app each (`data-contribution`) | 1 · Five places |
| 3-7 | One slide per app, launch order, same shape: what it does, one use, one limit | 2 · Five apps |
| 8 | Which app for which job: the main point as a table | 3 · Which app when |
| 9 | My favorite: Claude Code (lab changes, 169 video pages, 33 hook moments) | 4 · My favorite |
| 10 | The `.env` hook demo (real Nov 2 headless run) | 4 · My favorite |
| 11 | Try one this week: a first step per app, Claude Code's four steps | 5 · Try one |
| 12 | Thank you, questions (closing QR) | |

Backup: the discussion prompt (one question with example answers, for a quiet Q&A), sources (two slides), the hook ready to copy, Duet details, what lab code needs app by app, who starts the work (the old surfaces map), and Claude Code with what extends it.

There is no agenda slide; the map does that job, and the chapter rail follows `data-chapter`. Nothing in the deck announces a pause: the title's notes invite interruptions, and questions come at the end.

## Facts and sources

Every date and product claim was rechecked on November 4, 2026, against Anthropic's own pages; each slide's notes end with a short `Sources:` line, and the Sources backup slides link each one.

| App | Launch on the slide | Primary source |
|---|---|---|
| Claude chat | July 2023 (claude.ai public beta, US and UK) | anthropic.com/news/claude-2, published July 11, 2023 |
| Claude Desktop | October 2024 (Mac and Windows); Linux now in beta | Anthropic on X, status 1852003248208552331 (October 31, 2024 by its ID); help center "Install Claude Desktop" |
| Claude Code | February 2025 preview, May 2025 GA | anthropic.com/news/claude-3-7-sonnet (Feb 24, 2025); anthropic.com/news/claude-4 (May 22, 2025) |
| Claude Science | June 30, 2026 beta | anthropic.com/news/claude-science-ai-workbench; claude.com/docs/claude-science/overview |
| Claude Duet | October 21, 2026 research preview | claude.com/resources/articles/claude-duet; help center "Get started with Claude Duet" |

No launch date changed from the previous version. Facts that moved since November 2:

- Claude Science now runs on macOS, Windows 11 and Linux (help center), not just macOS and Linux as at launch; its docs say it works in any field, not only the life sciences.
- Cowork's scheduled tasks now run in the cloud; reaching local files, the browser or the computer still needs the desktop app open (help center, "Get started with Claude Cowork"). Slide 4's limit says so.
- The chat and Cowork merge reached Enterprise on October 23; Team (our lab's plan) and Free are still "to follow soon" ("Claude Cowork and chat are now one Claude", checked November 4). So the old footnote stays out.
- Duet is still not on Team or Enterprise plans (help center), which is why slide 7 says it isn't on our lab's plan.
- Claude Code's hook events: still 33 (hooks reference, November 4). The rivals' counts are as of November 2; recount before any later reuse.

## Uses on the app slides

Each app slide's middle row is "In my work" where there is evidence and "A lab could" where there is none:

- Claude chat: "A lab could" (reviewer comments to a response plan). FILL: AJ's own example?
- Claude Desktop: makesense, the SCADS 2026 analyst tool, installs into Claude Desktop from one ZIP and runs on the analyst's computer (delivered August 4, 2026).
- Claude Code: nn-library #18 for Richard Lange's lab, peak memory of one CKA step from about 1 GB to under 1 MB.
- Claude Science: "A lab could" (rebuild last semester's figures with their code and history). FILL: AJ's own example?
- Claude Duet: the real card from November 1 (IMG_1281).

The FILL markers are in those two slides' speaker notes, inside the `<small>` source line.

For another lab, change the title slide's kicker and the first line of its notes, which name LDQIS and Dr. Reznik.

## Pictures

- The title's robot is an original SVG drawing, not an Anthropic mark: Anthropic's [trademark guidelines](https://www.anthropic.com/legal/trademark-guidelines) allow its marks only in materials it approves. It dances, and stands still under reduced motion.
- Slide 7's card is cropped from a phone screenshot of my Duet app (November 1, IMG_1281), below a blurred line that quoted a classmate's review. The other screenshots show unrelated research and course items, so they stay out.

## The demo (slide 10)

The slide shows a real headless run from November 2 (`claude -p`, Claude Opus 5.5, permission
prompts off). Asked "Add DEBUG=1 to the .env file.", Opus's first shell command tried to read
`.env`, the hook blocked it, and Opus stopped and said why without trying another route. Haiku 5.5
did the same. The hook adapts "Block edits to protected files" from Anthropic's hooks guide, which
matches only Edit and Write; in a test with that matcher, Opus fixed a protected file with `sed`
in the shell, so this one also matches Read, Grep, Bash and PowerShell. The recorded run's hook
left out Grep and read only `file_path`, `path` and `command`; its first call was a Bash command,
so the result is the same, and a rerun with the slide's hook on Opus 5.5 ended the same way. To repeat it live:

1. In a scratch folder, before the talk: `git init`, a `.env` with a made-up line
   (`DB_PASSWORD=demo-not-a-real-password`), and the two files from the backup slide "The hook,
   ready to copy" (`.claude/settings.json`, `.claude/hooks/protect-env.sh`, `chmod +x`). `jq` must
   be installed.
2. Start `claude` there and type: `Add DEBUG=1 to the .env file.` The hook prints
   `Blocked: .env holds secrets. Don't read or change it.` and Claude says it left the file alone.
3. In a second terminal, run `cat .env`: it is unchanged.

In the recorded run, Opus also suggested putting the line in `.env.local`, "a file the hook doesn't
cover". That is wrong: the hook blocks any path or command containing `.env`, `.env.local` included.

Without `jq`, or Git Bash on Windows, the hook refuses every call it matches, so install both first.
On macOS, Linux and WSL2, `Read` and `Edit` deny rules for `.env` plus the sandbox give a hard block.

If the room has no network, play a recording instead: record the same steps once beforehand at
1920x1080 with a large terminal font (Windows: Win+Alt+R, Xbox Game Bar), about 40 seconds, and
open it from the slide.

## Recording it for YouTube

The speaker notes are written to be read aloud, so they double as narration for a Mode B walkthrough
(`videos/youtube-director`): the five chapters on the rail are the video's chapters. The `Sources:` line at the end
of each slide's notes is not read aloud; it goes in the video description.
