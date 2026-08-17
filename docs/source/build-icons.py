#!/usr/bin/env python3
"""Generate every favicon and app icon from one definition of the Ascent mark.

Why these are not all the same drawing
--------------------------------------
The brand guide sets a 24px floor for the three-chevron mark. A browser tab icon
is drawn at 16px, well under it: at that size the chevrons blur into each other
and the 30%-opacity one disappears against cream. So the small sizes use a
**single solid chevron** and the large ones use the **full three-chevron mark**.
That split is deliberate and is recorded in the brand-guide corrections note.

    16 / 32 / 48   favicon.ico      single chevron
    180            apple-touch      three chevrons
    192 / 512      Android/PWA      three chevrons, inset for maskable cropping

What this fixes
---------------
`/favicon.ico` and the manifest were absent, so both 404'd. Modern browsers use
the inline SVG `<link rel="icon">` and never notice, but Safari only gained SVG
favicon support in version 16 -- older Safari falls back to `/favicon.ico` and
found nothing. Android had no manifest, so "Add to Home Screen" had no declared
icon to use.

Maskable icons: Android crops adaptive icons to a circle or squircle and only
the middle ~80% is guaranteed visible. The 192/512 icons therefore draw the mark
at 62% of the canvas, centred, so it survives the crop either way.

Usage:
    python3 docs/source/build-icons.py
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'assets')

CREAM = (250, 242, 236)      # #FAF2EC
CORAL = (228, 121, 90)       # #E4795A

# Coordinates are the brand mark's own 100x100 viewBox, straight from the SVG.
SINGLE = [(50, 18), (96, 64), (74, 64), (50, 40), (26, 64), (4, 64)]
TRIPLE = [
    ([(50, 8),  (92, 50), (76, 50), (50, 24), (24, 50), (8, 50)], 1.00),
    ([(50, 30), (92, 72), (76, 72), (50, 46), (24, 72), (8, 72)], 0.62),
    ([(50, 52), (92, 94), (76, 94), (50, 68), (24, 94), (8, 94)], 0.30),
]

SS = 8  # supersample factor; the chevrons are all diagonals and alias badly


def render(size, shapes, inset=1.0):
    """Draw `shapes` on a cream square. `inset` scales the mark within the canvas."""
    big = size * SS
    img = Image.new('RGBA', (big, big), CREAM + (255,))

    span = big * inset
    off = (big - span) / 2

    def scale(pts):
        return [(off + x / 100 * span, off + y / 100 * span) for x, y in pts]

    for pts, alpha in shapes:
        # Composite each chevron over only its own area. Image.blend would mix
        # the whole canvas, so drawing the 62% chevron would wash out the 100%
        # one already painted -- which is exactly what it did the first time.
        # Painting in list order reproduces the SVG, where later polygons
        # overlap earlier ones.
        layer = Image.new('RGBA', (big, big), (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(scale(pts), fill=CORAL + (round(alpha * 255),))
        img = Image.alpha_composite(img, layer)

    # Flatten: the .ico must stay opaque, since some Windows shells composite an
    # alpha channel onto white and lose the cream ground.
    return img.convert('RGB').resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(ASSETS, exist_ok=True)

    # --- favicon.ico: single chevron, three sizes in one file ---------------
    ico_path = os.path.join(ROOT, 'favicon.ico')
    frames = [render(n, [(SINGLE, 1.0)]) for n in (48, 32, 16)]
    frames[0].save(ico_path, format='ICO',
                   sizes=[(48, 48), (32, 32), (16, 16)])
    print(f'  favicon.ico          16+32+48  {os.path.getsize(ico_path):,} bytes')

    # --- apple-touch-icon: full mark, no inset (iOS applies its own mask) ----
    apple = os.path.join(ASSETS, 'apple-touch-icon.png')
    render(180, TRIPLE).save(apple, format='PNG', optimize=True)
    print(f'  apple-touch-icon.png 180       {os.path.getsize(apple):,} bytes')

    # --- Android / PWA: full mark, inset so a maskable crop cannot clip it ---
    for n in (192, 512):
        p = os.path.join(ASSETS, f'icon-{n}.png')
        render(n, TRIPLE, inset=0.62).save(p, format='PNG', optimize=True)
        print(f'  icon-{n}.png{" " * (9 - len(str(n)))}{n}       {os.path.getsize(p):,} bytes')


if __name__ == '__main__':
    main()
