<!-- budget: 1100 words -->
# The upload package

What a finished upload carries, how to check it before and after it goes up, and why each rule exists. The model is the earthquake video ([i_MyPXD6-mg](https://www.youtube.com/watch?v=i_MyPXD6-mg), 10-29): chapters, the AI label, the custom thumbnail and the pinned question all checked on its live page.

## The files

| File | Holds |
|---|---|
| `description.txt` | The description exactly as it is pasted: plain text, real line breaks, UTF-8 |
| `metadata.md` | Title, pinned comment, Studio tags, end screen, thumbnail words, and whether Altered content is ticked |
| `thumbnail.jpg` | 1280x720 from real assets, with its `thumbnail-320.png` preview |

Paste the description from `description.txt` in a plain editor, never from a rendered Markdown view. A rendered view joins lines, and YouTube then builds no chapters. That is how the earthquake video first went up with none.

[example-description.txt](example-description.txt) is the earthquake package's description.

## The description, top to bottom

1. **Hook, one line, at most 150 characters.** A real finding or the question the video answers. The search and mobile previews show the first 100 to 150 characters ([Touhfa 2026](https://touhfa.art/blog/seo/youtube-description-guide/), [Wild and Free Tools 2026](https://wildandfreetools.com/blog/youtube-description-best-practices-length-format/); vendor guides, no official cut).
2. **Summary, one or two short paragraphs.** What the video shows and how. Every number comes from the video, its data or its linked repository. State only what the sources say ("PAGER rated it green", not "it hurt no one").
3. **Disclosure line** when an AI avatar narrates: "An AI avatar of me narrates this video, with my voice." Tick **Altered or synthetic content** in Studio too (guardrail 1 in [../../README.md](../../README.md)).
4. **Chapters, one per line.** The first at `00:00`, at least 3, ascending, each at least 10 seconds ([YouTube Help 9884579](https://support.google.com/youtube/answer/9884579)). Take the times from the final export's captions (`ffmpeg -i final.mp4 -map 0:s:0 subs.srt`) or, for a published video, its own captions (`yt-dlp --write-auto-subs --skip-download`).
5. **Links, one per line**, each as `Label: URL`. Only public repositories, papers and decks.
6. **Channel line:** `More videos: https://youtube.com/@AJBarea`.
7. **Hashtags, 3 to 8, on the last line.** YouTube shows the first three above the title and ignores every hashtag on a video that has more than 60 ([YouTube Help 6390658](https://support.google.com/youtube/answer/6390658)).

The whole description stays under 5,000 bytes and has no `<` or `>`, which YouTube rejects ([YouTube Data API, `snippet.description`](https://developers.google.com/youtube/v3/docs/videos#snippet.description)).

## The rest of the metadata

- **Title:** under 70 characters for a long video, under 50 for a Short; the topic word first. Change an old title only when it is unclear: an edit keeps the URL, the views and the comments.
- **Tags:** 5 to 15, for misspellings and synonyms only. YouTube says tags "play a minimal role" in discovery ([YouTube Help 146402](https://support.google.com/youtube/answer/146402)).
- **Pinned comment:** one specific question tied to a moment in the video, plus at most one link. A specific question draws replies where "what did you think?" does not ([TubeMilestone](https://tubemilestone.com/blog/youtube-pinned-comments); vendor guidance).
- **End screen** on a video of 25 seconds or more: Subscribe plus the most related video, in the last 5 to 20 seconds ([YouTube Help 6388789](https://support.google.com/youtube/answer/6388789)). Vertical Shorts get none.

## The thumbnail

Built from the video's own material, never generated:

1. A face frame from the video (a clean, eyes-open frame, cropped above any lower third).
2. The video's own visual: its map, chart, diagram or demo screen.
3. Three to five words that add to the title rather than repeat it.

`python3 videos/tools/thumbnail.py FACE VISUAL thumbnail.jpg "2,016" "QUAKES" "IN 30 DAYS"` composes it and writes a 320 px preview; read the preview, since that is the size most viewers see. YouTube takes JPG or PNG, 16:9, at least 640 px wide, and as large as possible ([YouTube Help 72431](https://support.google.com/youtube/answer/72431)). A custom thumbnail needs a verified account.

## The review pass, before upload

1. Contact sheets every 3 to 5 seconds: `ffmpeg -i final.mp4 -vf "fps=1/4,scale=480:-1,tile=4x4" sheet-%02d.png`. Read every sheet for typos, cut-off overlays and private details.
2. The caption transcript beside the script: every spoken number checked against the data.
3. `python3 videos/youtube_check.py description.txt --duration SECONDS [--ai]` lints the description.

## The live check, after upload

`make videos-verify ID=<video id> [AI=1]` reads the public watch page and checks (set `AI=1` when an AI avatar narrates):

| Check | Passes when |
|---|---|
| description | the published text passes the lint above (with `AI=1`, including the disclosure line) |
| chapters | the scrub bar has as many chapters as the description lists |
| AI label | the "Made with AI" label is shown exactly when `AI=1` is set |
| thumbnail | the shown thumbnail is none of YouTube's three auto frames (`AUTO_THUMB=1` accepts one) |

The lint checks the hook, the 5,000-byte cap, `<` and `>`, one link and one timestamp per line, the chapter rules, the hashtag cap and, with `--ai`, the disclosure line; the 3-hashtag floor and the `Label: URL` shape are for the reviewer. An auto thumbnail picked in Studio on a new upload has not been tested against the three auto frames.

YouTube can take a few minutes to rebuild chapters after an edit. A failure that persists means the line breaks or times are wrong.

## Channel About

URLs typed into the channel's About text are not clickable. Put them in the About page's Links section.
