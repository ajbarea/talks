<!-- budget: 750 words -->
# The Terminal That Haunted Me: upload metadata

Two uploads from one cut: the 16:9 video and a 9:16 Short. Paste each description from its `.txt` file in a plain editor, never from a rendered view, so the line breaks (and the chapters) survive. Media lives in `Desktop/spooky-youtube/` and is never committed.

## 16:9 video

**File:** `spooky-16x9-remaster.mp4` (video stream copied from the Vids export, audio remastered to -14 LUFS, captions corrected).

**Title:** The Terminal That Haunted Me at 3 AM 👻

**Description:** [description.txt](description.txt) (lint: `python3 videos/youtube_check.py videos/05-haunted-terminal/description.txt --duration 50 --ai`, 0 problems).

**Chapters:** five, one per 10-second beat, the first at 00:00. The last runs 0:40 to 0:50, exactly YouTube's 10-second minimum; `make videos-verify` confirms the scrub bar shows all five.

**Captions:** upload `spooky.en.srt` as English (Subtitles, Upload file, With timing). The mp4 also carries the same text as its caption track.

**Thumbnail:** `thumb-A-ghost.jpg` (pick). Alternates: `thumb-B-loop.jpg`, `thumb-C-kill.jpg`.

| File | Frame | Words | At 320 px |
|---|---|---|---|
| thumb-A-ghost.jpg | 0:09.15, the wide-eyed close-up | IT WASN'T A GHOST | reads; strongest face |
| thumb-B-loop.jpg | 0:09.15 face beside the red terminal at 0:22.5 (`videos/tools/thumbnail.py`) | IT WAS A LOOP / NOT A GHOST | headline reads; the small line is the weakest |
| thumb-C-kill.jpg | 0:30.5, the hooded face under projected code | KILL THE GHOST | reads |

**Pinned comment:**

> What's the spookiest code bug you've ever hunted down? Mine was a debug loop I forgot to kill, spawning threads at 3 AM (0:20). To keep your own agents from haunting you, klepsydra shows every Claude Code session and its background agents on one wall, with a button to end one: https://github.com/ajbarea/klepsydra

**Studio tags:** haunted terminal, coding horror, debugging, recursive function, infinite loop, kill -9, runaway process, programming humor, developer life, halloween coding, 3am coding, AI agents, Claude Code, klepsydra

**End screen (0:40 to 0:50, all 10 s):**

| Element | Where | Why there |
|---|---|---|
| Video: Best for viewer (swap to the agent-fleet video once it is up) | left, over the left monitor (about x 3 to 38%, y 30 to 62%) | clear of the face (x 42 to 67%) and below the baked 'Pinned Comment' card (top left) |
| Subscribe | right, over the right monitor (about x 80%, y 45%) | clear of the face and above the baked subscribe chip (bottom right) |

**Settings:** Not made for kids. Category: Comedy. Language and caption language: English. **AI use (Altered or synthetic content): Yes.**

**Publish:** Saturday, October 31, 2026, 10:00 AM ET (schedule it in Studio). Buffer's study of 1.8 million videos puts Saturday's best long-form slots at 12 PM, then 10 AM ([Buffer](https://buffer.com/resources/best-time-to-post-on-youtube/)); going live at 10 AM gives the upload two hours before that peak on Halloween morning. Check Studio's 'When your viewers are online' card first; the channel's own data wins over a cross-channel study.

## 9:16 Short

**File:** `spooky-9x16-short.mp4` (1080x1920, 50 s, same audio). A square or vertical upload up to 3 minutes is classed as a Short; the 16:9 file stays a regular video ([YouTube Help 15424877](https://support.google.com/youtube/answer/15424877)).

**Title:** My Router Was Haunted at 3 AM 👻

**Description:** [short-description.txt](short-description.txt).

**Related video:** the 16:9 video (Studio, Details, Related video). Links in Shorts descriptions and comments are not clickable ([Tubefilter, 2023](https://tubefilter.com/2023/08/10/youtube-shorts-comments-spam/)); the related-video link is the one tappable path to the long video and its repo link ([Search Engine Journal](https://www.searchenginejournal.com/youtube-adds-shorts-links-limits-links-elsewhere/495463)).

**Pinned comment:**

> What's the spookiest code bug you've ever hunted down? The repo from the end of this Short is in the full video's pinned comment: tap the related video link.

**Captions:** `spooky.en.srt` (same timeline).

**Settings:** Not made for kids. Comedy. **AI use (Altered or synthetic content): Yes.** No end screen (Shorts have none).

**Publish:** Saturday, October 31, 2026, 12:00 PM ET, after the 16:9 video is live so the related-video link resolves.

## Not in the files

- **Loudness:** -16.1 LUFS and +0.4 dBTP before; -14.0 LUFS (loudnorm) / -13.9 (ebur128) and -1.6 dBTP after, in both mp4s. Recipe in [TOOLING-NOTES.md](TOOLING-NOTES.md).
- **Captions fixed:** single spaces; 'three a.m.' to '3 AM,'; 'Smart Home Hub' to 'smart-home hub'; 'Spectre' to 'specter'. Every cue time is unchanged.
