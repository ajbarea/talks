"""Compose a 1280x720 thumbnail from real assets: a face frame on the left, the video's own visual on the right,
3 to 5 words right-aligned, the last line in the accent colour. Also writes OUT-320.png to judge it at search size.

Usage: python3 videos/tools/thumbnail.py FACE VISUAL OUT.jpg "2,016" "QUAKES" "IN 30 DAYS" [--font PATH]
"""

import argparse
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1280, 720
FACE_W, FADE = 640, 160
WHITE, ACCENT, INK = (255, 255, 255), (250, 204, 21), (0, 0, 0)


def bold_font() -> str:
    """The machine's bold sans (DejaVu Sans Bold on Linux), found through fontconfig."""
    return subprocess.run(["fc-match", "-f", "%{file}", "sans:bold"], capture_output=True, text=True).stdout


def compose(face: Image.Image, visual: Image.Image, words: list[str], font: str) -> Image.Image:
    out = Image.new("RGB", (W, H))
    out.paste(ImageOps.fit(visual.convert("RGB"), (W - FACE_W + FADE, H)), (FACE_W - FADE, 0))
    face = ImageOps.fit(face.convert("RGB"), (FACE_W, H), centering=(0.5, 0.3))
    mask = Image.linear_gradient("L").rotate(-90, expand=True).resize((FADE, H))  # 255 at the left edge, 0 at the right
    alpha = Image.new("L", (FACE_W, H), 255)
    alpha.paste(mask, (FACE_W - FADE, 0))
    out.paste(face, (0, 0), alpha)
    draw = ImageDraw.Draw(out)
    size = 104 if len(words) <= 3 else 84
    y = 60
    for i, word in enumerate(words):
        last = i == len(words) - 1 and len(words) > 1
        f = ImageFont.truetype(font, int(size * 0.7) if last else size)
        x = W - 40 - draw.textlength(word, font=f)
        draw.text((x, y), word, font=f, fill=ACCENT if last else WHITE, stroke_width=8, stroke_fill=INK)
        y += int(f.size * 1.12)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("face", type=pathlib.Path)
    ap.add_argument("visual", type=pathlib.Path)
    ap.add_argument("out", type=pathlib.Path)
    ap.add_argument("words", nargs="+", help="3 to 5 words, one line each")
    ap.add_argument("--font", help="a bold TrueType font (default: fontconfig's sans:bold)")
    args = ap.parse_args()
    thumb = compose(Image.open(args.face), Image.open(args.visual), args.words, args.font or bold_font())
    thumb.save(args.out, quality=95)
    thumb.resize((320, 180), Image.LANCZOS).save(args.out.with_name(args.out.stem + "-320.png"))
    print(f"{args.out} and its 320 px preview")


if __name__ == "__main__":
    main()
