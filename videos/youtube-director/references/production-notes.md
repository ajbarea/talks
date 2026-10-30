<!-- budget: 500 words -->
# Production notes

Lessons from making the earthquake video (ISTE-782 A3, October 2026).

## Voice

- **One narrator for the whole video.** A cut from the avatar's voice to a recorded one is audible to every viewer.
- **When the avatar quota runs out**, record your own voice in Vids (Record voiceover, which uses no AI quota). Record one take per scene, so each overlay cue stays tied to its scene.
- **Vids avatar limits reset monthly**, on the 1st at 00:00 Pacific ([Workspace AI usage limits](https://support.google.com/a/users/answer/14796585)). Plan generations so a deadline week does not land after the quota is spent.

## Overlays

- Fade each card in and out over about 0.5 seconds.
- Cue the fade-in on the first spoken word of the line it supports, and the fade-out after the last.
- Hold a card for the whole take it belongs to; a card that drops mid-sentence reads as a glitch.

## Slow zoom

ffmpeg's `zoompan` rounds its crop to whole pixels, so a slow zoom on a still visibly steps. [`../../tools/kenburns.py`](../../tools/kenburns.py) resamples each frame at a sub-pixel box and pipes raw frames to ffmpeg:

```
python3 videos/tools/kenburns.py still.png --seconds 20 |
  ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 30 -i - -c:v libx264 -pix_fmt yuv420p zoom.mp4
```

## Maps in QGIS

- Run PyQGIS headless on Windows through the OSGeo4W `python-qgis-ltr.bat`, not WSL's Python.
- Render the basemap once, and the data layer per frame on a transparent background; composite them afterwards.
- Set the extent in EPSG:3857 at exactly 16:9, so the frame fills with no white bands.
- Never name a script `inspect.py` (or any standard-library module name): it shadows the module and PyQGIS fails at import.

## Thumbnail

A custom thumbnail from real frames beat every auto frame YouTube offered. No generative AI on a data video's thumbnail: the image is a claim about the data. The recipe is in [upload-package.md](upload-package.md#the-thumbnail).
