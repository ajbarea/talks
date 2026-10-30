"""Slow zoom on a still, without ffmpeg zoompan's jitter: each frame is resampled at a sub-pixel box.

Usage: python3 videos/tools/kenburns.py STILL [--seconds 20] [--fps 30] [--zoom 0.08] |
       ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 30 -i - -c:v libx264 -pix_fmt yuv420p out.mp4
zoompan rounds its crop to whole pixels, so a slow zoom steps visibly; a float box does not.
"""

import argparse
import sys

from PIL import Image

SIZE = (1920, 1080)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("still")
    ap.add_argument("--seconds", type=float, default=20)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--zoom", type=float, default=0.08, help="how far in at the end: 0.08 is 8%%")
    args = ap.parse_args()
    src = Image.open(args.still).convert("RGB")
    w0, h0 = src.size
    n = max(2, round(args.seconds * args.fps))
    for i in range(n):
        p = i / (n - 1)
        p = p * p * (3 - 2 * p)  # ease in and out
        z = 1 + args.zoom * p
        w, h = w0 / z, h0 / z
        x, y = (w0 - w) / 2, (h0 - h) / 2
        sys.stdout.buffer.write(src.resize(SIZE, Image.LANCZOS, box=(x, y, x + w, y + h)).tobytes())


if __name__ == "__main__":
    main()
