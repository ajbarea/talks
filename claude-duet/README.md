# Claude Duet, the Claude apps, and my favorite: Claude Code

LDQIS meeting, November 6, 2026. About ten minutes, light theme for a lit room. Every product fact is checked against Anthropic's pages and the press coverage
of October 30, 2026 (the app map, plans, privacy and hook facts on November 2); the Sources backup slide links each one, and each slide's notes end with a
short source line.

For another lab, change the title slide's kicker and the first line of its notes, which name LDQIS and Dr. Reznik.

## Pictures

- The title's robot is an original SVG drawing, not an Anthropic mark: Anthropic's [trademark guidelines](https://www.anthropic.com/legal/trademark-guidelines) allow its marks only in materials it approves. It dances, and stands still under reduced motion.
- Slide 4's card is cropped from a phone screenshot of my Duet app (November 1, IMG_1281), below a blurred line that quoted a classmate's review. The other screenshots show unrelated research and course items, so they stay out.

## The pauses

Slide 8 is a pause for questions only. Slide 12 is the discussion: one question, example answers on the slide.

## The demo (slide 11)

The slide shows a real headless run from November 2 (`claude -p`, Claude Opus 5.5, permission
prompts off). Asked "Add DEBUG=1 to the .env file.", Opus's first shell command tried to read
`.env`, the hook blocked it, and Opus stopped and said why without trying another route. Haiku 5.5
did the same. The hook adapts "Block edits to protected files" from Anthropic's hooks guide, which
matches only Edit and Write; in a test with that matcher, Opus fixed a protected file with `sed`
in the shell, so this one also matches Read, Grep, Bash and PowerShell. The recorded run's matcher
left out Grep; its first call was a Bash command, so the result is the same. To repeat it live:

1. In a scratch folder, before the talk: `git init`, a `.env` with a made-up line
   (`DB_PASSWORD=demo-not-a-real-password`), and the two files from the backup slide "The hook,
   ready to copy" (`.claude/settings.json`, `.claude/hooks/protect-env.sh`, `chmod +x`). `jq` must
   be installed.
2. Start `claude` there and type: `Add DEBUG=1 to the .env file.` The hook prints
   `Blocked: .env holds secrets. Don't read or change it.` and Claude says it left the file alone.
3. In a second terminal, run `cat .env`: it is unchanged.

In the recorded run, Opus also suggested putting the line in `.env.local`, "a file the hook doesn't
cover". That is wrong: the hook blocks any path or command containing `.env`, `.env.local` included.

If the room has no network, play a recording instead: record the same steps once beforehand at
1920x1080 with a large terminal font (Windows: Win+Alt+R, Xbox Game Bar), about 40 seconds, and
open it from the slide.

## Recording it for YouTube

The speaker notes are written to be read aloud, so they double as narration for a Mode B walkthrough
(`videos/youtube-director`): the agenda's five parts are the chapters. The `Sources:` line at the end
of each slide's notes is not read aloud; it goes in the video description.
