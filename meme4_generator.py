#!/usr/bin/env python3
"""Meme #4: 'MISSING' poster for GTA VI.

A lost-person poster taped to a wall: big MISSING header, a procedural
Vice City sunset scene (gradient sky, sun, skyline, palm silhouettes),
last-seen line, and a tear-off tab strip at the bottom.

Everything is drawn with PIL primitives -- no photos, no copyrighted art,
no Rockstar logos, characters, or official fonts. Deterministic: fixed
coordinates, no randomness, no timestamps.
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

ANTON = os.path.join(ASSETS, "Anton-Regular.ttf")
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W = H = 1080
OUT = os.path.join(HERE, "meme-4.png")

# ------------------------------------------------------------------ palette
WALL_TOP = (44, 52, 64)
WALL_BOT = (24, 28, 36)
PAPER = (245, 238, 218)
PAPER_EDGE = (30, 28, 24)
INK = (22, 20, 18)
RED = (178, 24, 28)
MUTED = (110, 100, 84)
TAPE = (235, 230, 200, 150)
SKY = [(59, 29, 94), (150, 52, 110), (232, 84, 96), (255, 140, 66), (255, 209, 102)]
SUN = (255, 233, 168)
SUN_GLOW = (255, 200, 110, 90)
SILHOUETTE = (36, 21, 53)
WATER = (255, 140, 66)


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(DEJAVU_BOLD, size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def center_text(draw, cx, y, text, font, fill):
    draw.text((cx - text_w(draw, text, font) / 2, y), text, font=font, fill=fill)


def vertical_gradient(img, box, stops):
    """Fill box with a vertical gradient through the given color stops."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    n = len(stops) - 1
    tmp = Image.new("RGB", (1, h))
    px = tmp.load()
    for yy in range(h):
        t = yy / max(h - 1, 1) * n
        i = min(int(t), n - 1)
        f = t - i
        c = tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3))
        px[0, yy] = c
    img.paste(tmp.resize((x1 - x0, h)), (x0, y0))


def draw_sunset(box):
    """Procedural Vice City sunset, rendered on its own layer so nothing
    can spill past the picture frame: sky, sun, two skyline rows, palms,
    water."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(layer, "RGBA")
    vertical_gradient(layer, (0, 0, w, h), SKY)
    horizon = h - 52

    # sun glow + disc
    cx, cy, r = w // 2 - 120, 78, 52
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22], fill=SUN_GLOW)
    layer.paste(glow, (0, 0), glow)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)

    # birds: tiny v-shapes in the sky
    for bx, by, s in [(560, 46, 14), (620, 70, 11), (500, 84, 9)]:
        d.line([(bx - s, by), (bx, by - 6), (bx + s, by)], fill=(40, 24, 60), width=3)

    # distant skyline (lighter): a few towers peek above the front row
    back = [(20, 90, 120), (130, 120, 170), (280, 100, 140), (410, 90, 185),
            (560, 90, 200), (680, 110, 150), (800, 60, 175)]
    for bx, bw, bh in back:
        d.rectangle([bx, horizon - bh, bx + bw, horizon], fill=(91, 42, 114))

    # front skyline silhouette (fixed building widths/heights)
    buildings = [
        (0, 150, 96), (150, 96, 150), (246, 130, 118), (376, 80, 168),
        (456, 120, 132), (576, 72, 186), (648, 110, 128), (758, 62, 158),
    ]
    for bx, bw, bh in buildings:
        d.rectangle([bx, horizon - bh, bx + bw, horizon], fill=SILHOUETTE)
    # antenna on the tallest tower
    d.line([(576 + 36, horizon - 186), (576 + 36, horizon - 214)],
           fill=SILHOUETTE, width=4)
    d.ellipse([576 + 32, horizon - 220, 576 + 40, horizon - 212], fill=(255, 90, 90))
    # lit windows: small warm dots, fixed grid
    for wx, wy in [(30, 40), (90, 70), (180, 30), (280, 60), (400, 45),
                   (480, 80), (600, 35), (690, 65), (780, 40)]:
        d.rectangle([wx, horizon - wy, wx + 7, horizon - wy + 9],
                    fill=(255, 214, 130))

    # palm silhouettes in front of the skyline: tall trunks so the crowns
    # clear the rooflines, drooping fronds as smooth polylines
    def palm(px, py, s, lean):
        trunk_h = 170 * s
        top = (px + lean, py - trunk_h)
        d.line([(px, py), top], fill=SILHOUETTE, width=int(9 * s))
        for spread in (-1.0, -0.65, -0.3, 0.3, 0.65, 1.0):
            mid = (top[0] + spread * 40 * s, top[1] - 14 * s)
            tip = (top[0] + spread * 62 * s, top[1] + 30 * s)
            d.line([top, mid, tip], fill=SILHOUETTE, width=int(5 * s), joint="curve")
        for spread in (-0.45, 0.45):
            mid = (top[0] + spread * 26 * s, top[1] - 34 * s)
            tip = (top[0] + spread * 44 * s, top[1] - 6 * s)
            d.line([top, mid, tip], fill=SILHOUETTE, width=int(5 * s), joint="curve")

    palm(60, horizon, 1.0, 14)
    palm(w - 70, horizon, 1.1, -12)

    # water strip with reflection streaks
    d.rectangle([0, horizon, w, h], fill=(64, 28, 84))
    for i, (ry, rw) in enumerate([(6, 300), (16, 180), (26, 340), (36, 150)]):
        d.rectangle([90 + i * 110, horizon + ry, 90 + i * 110 + rw,
                     horizon + ry + 4], fill=WATER)
    return layer


def draw_tape(draw, x, y, w, h, angle):
    """A piece of semi-transparent tape (rotated rectangle via polygon)."""
    import math
    cx, cy = x + w / 2, y + h / 2
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    draw.polygon(pts, fill=TAPE, outline=(200, 195, 170))


# ------------------------------------------------------------------ build
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img, "RGBA")
vertical_gradient(img, (0, 0, W, H), [WALL_TOP, WALL_BOT])

# paper poster
PX0, PY0, PX1, PY1 = 70, 48, 1010, 1032
draw.rectangle([PX0 + 6, PY0 + 8, PX1 + 6, PY1 + 8], fill=(0, 0, 0, 90))  # drop shadow
draw.rectangle([PX0, PY0, PX1, PY1], fill=PAPER, outline=PAPER_EDGE, width=4)
draw_tape(draw, PX0 - 8, PY0 - 14, 130, 44, -18)
draw_tape(draw, PX1 - 122, PY0 - 14, 130, 44, 16)

cx = (PX0 + PX1) // 2

# header
center_text(draw, cx, 84, "MISSING", load_font(ANTON, 158), INK)
draw.line([(PX0 + 120, 268), (PX1 - 120, 268)], fill=RED, width=8)
center_text(draw, cx, 292, "GRAND THEFT AUTO VI", load_font(ANTON, 62), INK)

# sunset scene in a framed box (layer pasted in, clipped to the frame)
SX0, SY0, SX1, SY1 = 130, 372, 950, 652
draw.rectangle([SX0 - 5, SY0 - 5, SX1 + 5, SY1 + 5], fill=PAPER_EDGE)
img.paste(draw_sunset((SX0, SY0, SX1, SY1)), (SX0, SY0))

# last seen
center_text(draw, cx, 678, "LAST SEEN: Trailer 1 \u2014 December 2023",
            load_font(DEJAVU_BOLD, 34), INK)
# waiting lines
center_text(draw, cx, 724, "13 YEARS OF WAITING...", load_font(ANTON, 56), RED)
center_text(draw, cx, 786, "AND COUNTING", load_font(ANTON, 56), RED)
# return line
center_text(draw, cx, 862, "IF FOUND, PLEASE RETURN TO MY PS5",
            load_font(DEJAVU_BOLD, 34), INK)
# small credit
center_text(draw, cx, 916, "Reward paid by my AI agent on make.fun",
            load_font(DEJAVU, 24), MUTED)

# tear-off tabs along the bottom edge of the poster
tab_y0, tab_y1 = 956, 1016
tab_w = (PX1 - PX0 - 40) // 10
tab_font = load_font(DEJAVU_BOLD, 20)
for i in range(10):
    tx0 = PX0 + 20 + i * tab_w
    draw.line([(tx0, tab_y0), (tx0, tab_y1)], fill=MUTED, width=2)
    center_text(draw, tx0 + tab_w // 2, tab_y0 + 26, "GTA VI", tab_font, MUTED)

img.save(OUT, format="PNG")
print("wrote", OUT, os.path.getsize(OUT), "bytes")
