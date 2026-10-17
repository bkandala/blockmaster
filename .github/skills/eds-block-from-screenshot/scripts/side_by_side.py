#!/usr/bin/env python3
"""Label and stitch a reference image and a render into one comparison image.

Usage:
  python side_by_side.py reference.png render.png compare.png [--width 800]

Both images are scaled to the same width (default: the render's width, capped at
1280) so their layouts line up, then placed side by side under REFERENCE / RENDER
labels. Needs Pillow: pip install pillow (add pillow-avif-plugin for .avif input).
"""
import argparse
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('Pillow is missing: pip install pillow')
try:
    import pillow_avif  # noqa: F401  (optional: lets Pillow open .avif references)
except ImportError:
    pass

LABEL_H = 36
GAP = 24


def font(size):
    for name in ('DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf', 'Helvetica.ttc'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def panel(path, label, width):
    img = Image.open(path).convert('RGB')
    img = img.resize((width, max(1, round(img.height * width / img.width))), Image.LANCZOS)
    out = Image.new('RGB', (width, img.height + LABEL_H), 'white')
    out.paste(img, (0, LABEL_H))
    ImageDraw.Draw(out).text((10, 8), f'{label}  ({path.split("/")[-1]})', fill='black', font=font(16))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('reference')
    ap.add_argument('render')
    ap.add_argument('out')
    ap.add_argument('--width', type=int, help='width of each panel in px')
    a = ap.parse_args()

    width = a.width or min(Image.open(a.render).width, 1280)
    left = panel(a.reference, 'REFERENCE', width)
    right = panel(a.render, 'RENDER', width)
    height = max(left.height, right.height)
    sheet = Image.new('RGB', (width * 2 + GAP, height), (210, 210, 210))
    sheet.paste(left, (0, 0))
    sheet.paste(right, (width + GAP, 0))
    sheet.save(a.out)
    print(f'wrote {a.out} ({sheet.width}x{sheet.height})')


if __name__ == '__main__':
    main()
