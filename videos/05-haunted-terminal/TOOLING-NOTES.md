<!-- budget: 2000 words -->
# Tooling notes: the Halloween package, step by step

Harvest material for a video-editing plugin. Every command below ran on this package (ffmpeg 6.1.1, Ubuntu WSL). `SRC` is the Google Vids export; scratch files sat in a scratch folder, never in the repo.

## Probe

- Streams, rates, frame count: `ffprobe -v error -show_streams -show_format SRC | grep -E "codec_name|width|height|r_frame_rate|duration=|sample_rate|channels|bit_rate|TAG:handler|TAG:language|nb_frames"`. Vids exports: h264 1920x1080 30 fps, AAC 44.1 kHz stereo 126 kbps, an English `mov_text` caption track, moov at the end of the file.
- Edit lists and moov position: a 30-line Python box walker (read `moov/trak/edts/elst`, print `(segment_duration, media_time)` per track, and the `moov` offset). Vids writes one single-entry `elst` per track: video media_time 6000 (the B-frame offset), audio 0. ffmpeg rewrites them on output: the 16:9 remux keeps the video's 6000 and sets the audio's to 1024 (AAC priming); the re-encoded Short has 1024 on both. YouTube's encoding page asks for 'No Edit Lists' ([YouTube Help 1722171](https://support.google.com/youtube/answer/1722171)); these single-entry lists are a deviation from that, kept because the Vids export already carries them and YouTube processes those uploads. Writing without them (`-use_editlist 0`) leaves the 1024 AAC priming samples (21 ms at 48 kHz) audible as a lead-in; not tried here. Gate: fail on any `elst` with more than one entry.

## Loudness

- Measure: `ffmpeg -hide_banner -nostats -i SRC -map 0:a -af ebur128=peak=true -f null - 2>&1 | tail -14` (integrated, LRA, true peak). Source: -16.1 LUFS, LRA 2.4, +0.4 dBTP.
- Why plain two-pass loudnorm was not enough: raising -16.16 LUFS to -14 adds 2.16 dB, which puts a +0.37 dBTP peak at +2.5, above the -1.5 target. loudnorm then drops to dynamic mode and landed at -14.6 LUFS. Rule: linear mode needs `measured_TP + (target_I - measured_I) <= target_TP`, i.e. a peak-to-loudness ratio of at most 12.5 dB for -14 / -1.5.
- Pre-limit to bring the ratio under 12.5 (4x oversampled so the sample-peak limiter approximates true peak): `ffmpeg -hide_banner -nostats -y -i SRC -map 0:a -af "aresample=192000,alimiter=limit=0.53:attack=0.5:release=40:level=disabled,aresample=48000" -c:a pcm_f32le lim.wav`. Settings tried, ratio (TP minus I) each: `0.56:1:60` 12.5, `0.56:0.5:30` 12.3, `0.6:0.5:20` 12.5, `0.53:0.5:40` 12.0 (chosen, 0.5 dB margin). The limiter cost about 1.4 LU of loudness, which the gain stage restores.
- Pass 1: `ffmpeg -hide_banner -nostats -i lim.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | grep -A12 "^{"` gave input_i -17.61, input_tp -5.50, input_lra 2.60, input_thresh -27.97, target_offset -0.07.
- Pass 2 (linear): `ffmpeg -hide_banner -nostats -y -i lim.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=-17.61:measured_TP=-5.50:measured_LRA=2.60:measured_thresh=-27.97:offset=-0.07:linear=true:print_format=summary,aresample=48000" -c:a pcm_f32le norm.wav`. Gate: the summary must say `Normalization Type: Linear`; it printed -13.9 LUFS, -1.9 dBTP.
- Encode toward YouTube's stereo recommendation, AAC-LC 48 kHz 384 kbps ([YouTube Help 1722171](https://support.google.com/youtube/answer/1722171)): `-c:a aac -b:a 384k -ar 48000` asks for 384 kbps, and ffmpeg's native AAC encoder delivered about 306 kbps on this speech; the AAC encode raised the true peak from -1.9 to -1.6 dBTP (ebur128 on `norm.wav`, then on the mp4), which is why the target is -1.5 and not -1.0.
- Verify on the final mp4, both meters: the ebur128 line above (-13.9 LUFS, -1.6 dBFS true peak) and `ffmpeg -i OUT -map 0:a -af loudnorm=print_format=json -f null - 2>&1 | grep -E 'input_(i|tp|lra)'` (-14.01, -1.55, 2.60). Gate: |I + 14| <= 0.5 and TP <= -1.0.
- Sync: decode source and output to mono 48 kHz f32 (`ffmpeg -v error -y -i FILE -map 0:a -ac 1 -ar 48000 -f f32le a.raw`), FFT cross-correlate with numpy, report the peak lag. Result: -24 samples (0.5 ms). Gate: |lag| under one frame (33 ms); in practice under 2 ms.
- YouTube's -14 LUFS reference is community-measured, not documented ([Production Advice](https://productionadvice.co.uk/stats-for-nerds/)); the check after upload is Stats for nerds 'content loudness' near 0 dB.

## Remux with the video untouched

- `ffmpeg -hide_banner -v error -y -i SRC -i norm.wav -i spooky.en.srt -map 0:v:0 -map 1:a:0 -map 2:s:0 -c:v copy -c:a aac -b:a 384k -ar 48000 -c:s mov_text -metadata:s:a:0 language=eng -metadata:s:s:0 language=eng -movflags +faststart OUT.mp4`
- Never add `-shortest` with a caption input: the SRT's last cue ends at 50.000 s, so `-shortest` cut the video to 49.90 s and its stream MD5 changed. (Without the SRT, `-shortest` kept all 1501 frames.)
- Gate, video untouched: `ffmpeg -v error -i SRC -map 0:v -c copy -f md5 -` equals the same on OUT, and `nb_frames` matches.
- `+faststart` moves moov to the front, as YouTube asks.

## Captions

- Extract: `ffmpeg -v error -y -i SRC -map 0:s:0 orig.srt`. Vids writes two spaces between words and its own spellings ('three a.m.', 'Smart Home Hub', 'Spectre').
- Clean (Python, timing lines and cue numbers untouched): collapse `[ \t]+` to one space and strip each text line; then the house fixes as regexes, `\bthree a\.m\.` to `3 AM,`, `\bSmart Home Hub\b` to `smart-home hub`, `\bSpectre\b` to `specter`. Write LF line ends, UTF-8.
- Gates: `diff <(grep -- '-->' orig.srt) <(grep -- '-->' clean.srt)` is empty; `grep -c '  ' clean.srt` is 0; none of the old spellings remain; `ffmpeg -i clean.srt -f srt -` parses it.
- Check against the audio, locally: `ffmpeg -i SRC -map 0:a -ac 1 -ar 16000 speech16k.wav`, then faster-whisper `small.en` (CPU, int8, beam 5, `word_timestamps=True`) through `uv run --no-project --with faster-whisper`. Pass the audio as a numpy float32 array read with the `wave` module: the PyAV that faster-whisper pulled rejects its `metadata_errors` argument. It took under a minute for 50 s. Diff the words with the captions (it heard 'fans' for 'fan', the only difference).
- Speaking rate per beat from the word timestamps: 174, 181, 218, 146 and 213 wpm. `check_script.py` times lines at 150 wpm and would have rejected four of the five; Vids fit them by speaking faster. Worth a calibration question for the lint, not a change here.

## Contact sheets and shot list

- Overview, one frame a second, 10 per sheet: `ffmpeg -v error -y -i SRC -vf "fps=1,scale=384:-1,tile=5x2" -frames:v 5 sheet-%02d.png`.
- Shot cuts: `select='gt(scene,0.3)'` found none (Vids cuts score 0.13 to 0.44). This worked: `ffmpeg -hide_banner -i SRC -an -sn -vf "scale=320:-1,select='gt(scene,0.12)',metadata=print:file=scenes.txt" -f null -`, then `grep -oE "pts_time:[0-9.]+|scene_score=[0-9.]+" scenes.txt | paste - -`. 19 cuts; every 10 s beat boundary showed up.
- A cut the detector missed (a hard cut to a near-black 'PROCESS KILLED' screen): mean luma per frame, `ffmpeg -v error -i SRC -ss 32.4 -t 1.4 -vf "scale=96:54,format=gray,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -f null -`; YAVG jumps 39.4 to 28.6 at 33.4 s.
- Per-shot sheet with a 10% grid for reading crop positions: for each shot, three frames (start + 0.08 s, middle, end - 0.1 s) through `-vf "scale=384:-1,drawgrid=w=iw/10:h=ih:t=1:c=yellow@0.6,drawtext=text='s$i $t':x=4:y=4:fontcolor=white:fontsize=14:box=1:boxcolor=black"`, tiled with `-pattern_type glob -i 'shots/s0[1-9]*.png' -vf tile=3x9`.
- Timestamped frames: `-ss` before `-i` resets pts, so `drawtext=text='%{pts\:hms}'` prints time since the seek, not the video time. Add the seek offset by hand, or seek after `-i`.

## Thumbnails

- Full-res frame: `ffmpeg -v error -y -ss 9.15 -i SRC -frames:v 1 f9.15.png`. The wide-eyed close-up sits at 8.65 to 9.65 s.
- One-frame layout (Pillow, Inter Display Black): crop box, scale to 1280x720 with Lanczos, gamma lift for dark AI footage (`v' = 255 (v/255)^0.72`), a horizontal black gradient up to 50% behind the words, words 140 to 150 px with a 10 px black stroke, the last line in orange (255, 140, 26). Settings used: A `--box 0 110 1500 844 --side left --lift 0.72 --shade 0.5`, C `--box 300 60 1600 900 --side right --lift 0.85`.
- Two-panel layout: `python3 videos/tools/thumbnail.py face.png term.png thumb-B-loop.jpg "IT WAS" "A LOOP" "KILL -9" --font /usr/share/fonts/opentype/inter/InterDisplay-Black.otf`, with the face pre-cropped to 840x945 and the terminal to 780x1080 (the full frame put a stray hand in the panel). The tool sets the last line at 70%, so the payoff word must not go last.
- 320 px check, all three side by side: `ffmpeg -v error -y -i A-320.png -i B-320.png -i C-320.png -filter_complex "[0]pad=330:180[a];[1]pad=330:180[b];[a][b][2]hstack=3" all-320.png`, then look.
- Gates: 1280x720, JPEG or PNG, under 2 MB (Pillow `Image.open().size`, `os.path.getsize`).

## 9:16 Short

- Crop math: 9:16 of a 1080-high frame is 607.5 px; use 608 (even). Scale 608x1080 to 1080x1920 with Lanczos (1.78x up).
- One static crop per shot, frame-exact with `trim=start_frame:end_frame`, then `concat`; a Python script builds the graph from a table `(first_frame, end_frame, crop_x[, wide_w])` and asserts `x` even and `0 <= x <= 1920 - w`. The table used:

  ```
  (0,30,368) (30,65,656) (65,95,464) (95,133,752) (133,153,560) (153,213,580) (213,254,656)
  (254,300,618) (300,491,752) (491,511,886) (511,600,752) (600,674,1002) (674,763,752)
  (763,795,810) (795,900,1002) (900,928,656) (928,1002,0) (1002,1013,560,800) (1013,1200,656)
  (1200,1501,810)
  ```

- Per shot: `[sN]trim=start_frame=A:end_frame=B,setpts=PTS-STARTPTS,crop=608:1080:X:0,scale=1080:1920:flags=lanczos,setsar=1[vN]`. A wide shot (text wider than 608 px): `crop=800:1080:560:0,scale=1080:-2:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x05070c`.
- The Gemini mark is cut off by most crops, so it is redrawn: alpha from the dark frame at 13 s, `clip((luma - 6) / (70 - 6), 0, 1) * 0.52` over gray 135 (the mark measured 70 over black and 82 over a 25 background, so about 52% opaque), scaled to 128 px, overlaid with `-loop 1 -i gemini-mark.png` and `overlay=x=906:y=220:format=auto,format=yuv420p` (top right, clear of the Shorts buttons).
- Encode: `-c:v libx264 -preset slow -crf 17 -profile:v high -r 30 -frames:v 1501 -c:a aac -b:a 384k -ar 48000 -movflags +faststart`, audio from `norm.wav`. Tag the audio language too (`-metadata:s:a:0 language=eng`); the first render came out `und` and was fixed with a stream-copy remux.
- Tried and dropped: pasting the outro's baked 'Pinned Comment' card into the vertical frame as a live crop (`crop=646:138:70:78`, overlay at 1.2x). The card animates in and fades out, so the paste showed garbled text and then an empty beige box over the hair.
- Gates: 1080x1920, `nb_frames` equal to the source, duration under 3 minutes ([YouTube Help 15424877](https://support.google.com/youtube/answer/15424877)), ebur128 equal to the 16:9 file.

## Checks a script could gate (done by hand here)

- Loudness and true peak on the final file; `Normalization Type: Linear` in pass 2.
- Video stream MD5 and frame count unchanged after a remux.
- Audio offset to the source by cross-correlation.
- Caption timing lines identical, no double spaces, banned spellings absent, transcript diff against ASR.
- Thumbnail size, format and bytes; a 320 px preview written.
- Short: every crop inside the frame, every shot covered once (end of one equals start of the next, last equals `nb_frames`).
- Description lint (`videos/youtube_check.py`, already a gate) with `--duration` taken from ffprobe and rounded down.
- `elst` boxes with more than one entry; moov before mdat.

## Where a person (or a vision model) had to look

- Picking thumbnail frames (eyes open, expression, motion blur) and judging each at 320 px.
- Placing each 9:16 crop: face or screen in frame at the start, middle and end of each shot; the camera drifts inside shots.
- Spotting the missed cut at 33.4 s and the text that overflowed the 608 px crop.
- Seeing that the pasted card failed.
- Reading generated on-screen text for gibberish or anything private.
- End-screen zones: where the face and the baked overlays sit in the outro (a 10% grid on one frame).
