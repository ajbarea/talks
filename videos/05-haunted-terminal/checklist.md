<!-- budget: 450 words -->
# Upload checklist

Files in `Desktop/spooky-youtube/`; text in this folder. The review pass in [upload-package.md](../youtube-director/references/upload-package.md#the-review-pass-before-upload) is done (results below).

## Before upload (done)

- [x] Audio: two-pass loudnorm; the final mp4s read -14.0 LUFS on loudnorm's meter and -13.9 LUFS, -1.6 dBTP on ebur128; video stream byte-identical to the Vids export (stream MD5 match), 1501 frames.
- [x] Audio sync: 0.5 ms offset to the source by cross-correlation.
- [x] Captions: single spaces, the three fixes, every cue time unchanged; text matches a faster-whisper `small.en` transcript word for word (it hears 'fans' where the captions and script say 'fan').
- [x] Contact sheets at 1 s and per shot: no private repository, account, email or key; terminal text above 'KILL -9 14022' is generated gibberish.
- [x] Thumbnails: 1280x720 JPEG, 76 to 203 KB, each read at 320 px.
- [x] Short: a frame from every shot checked; face or screen in frame in each.
- [x] `python3 videos/youtube_check.py` on both descriptions: 0 problems.

## Upload: 16:9 video

- [ ] Upload `spooky-16x9-remaster.mp4`; set it to Schedule, Sat Oct 31, 10:00 AM ET.
- [ ] Title and description from [metadata.md](metadata.md) and [description.txt](description.txt), pasted from a plain editor.
- [ ] Thumbnail `thumb-A-ghost.jpg`.
- [ ] Not made for kids; Comedy; English.
- [ ] AI use (Altered or synthetic content): **Yes**.
- [ ] Tags from metadata.md.
- [ ] Subtitles: upload `spooky.en.srt`, With timing.
- [ ] End screen 0:40 to 0:50: video element left, Subscribe right (metadata.md).
- [ ] After it goes live: post and pin the comment; run `make videos-verify ID=<id> AI=1`.

## Upload: 9:16 Short

- [ ] Upload `spooky-9x16-short.mp4`; Schedule, Sat Oct 31, 12:00 PM ET.
- [ ] Title and [short-description.txt](short-description.txt).
- [ ] Related video: the 16:9 upload.
- [ ] AI use: **Yes**; not made for kids; captions `spooky.en.srt`.
- [ ] After it goes live: post and pin the Short's comment.

## After both are live

- [ ] `make videos-verify ID=<long id> AI=1`: description, 5 chapters, the AI label, a custom thumbnail.
- [ ] Stats for nerds on the long video: 'content loudness' near 0 dB confirms the -14 LUFS master.
- [ ] Add `Short: <Short URL>` above the 'More videos' line of the 16:9 description, re-run `python3 videos/youtube_check.py` on it, and paste it again.
- [ ] Rebuild the channel tables from a fresh pull (`videos/channel/refresh.py extract`, see IMPL.md).
