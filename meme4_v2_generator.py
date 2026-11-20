#!/usr/bin/env python3
"""Meme #4 (rebuild v2): MISSING poster for GTA VI, 1080x1080, deterministic.

Concept (ours): a lost-person poster for GTA VI taped to a wall.
Visual style borrowed from two reference images (style only, never their
concepts): rich official-document density -- paper texture, ornate double
frame, file number, stat boxes, rotated rubber stamp, strong colours.
All art is procedural; the make.fun ghost mark is composited from the
press-kit asset in assets/mark-1024.png.
"""
import math
import random
from datetime import date

from PIL import Image, ImageDraw, ImageFont, ImageChops

W = H = 1080
OUT = "meme-4.png"
ASSETS = "assets"
ANTON = f"{ASSETS}/Anton-Regular.ttf"
SERIF_IT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (26, 34, 58)
NAVY_D = (18, 25, 45)
CREAM = (244, 236, 216)
INK = (24, 24, 28)
RED = (178, 34, 34)
MAGENTA = (176, 24, 92)
GOLD = (176, 141, 68)
DUSK_TOP = (44, 24, 86)
DUSK_MID = (146, 44, 110)
DUSK_LOW = (232, 110, 68)
SUN = (252, 214, 120)

WAIT_START = date(2013, 9, 17)   # GTA V launch; the wait began here
TODAY = date(2026, 11, 20)       # fixed so re-runs are byte-identical
DAYS_WAITING = (TODAY - WAIT_START).days  # 4,812


def font(path, size):
    return ImageFont.truetype(path, size)


def text_center(draw, cx, y, s, f, fill, spacing=0):
    """Draw text centred on cx; returns (width, height)."""
    if spacing:
        widths = [draw.textlength(ch, font=f) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x = cx - total / 2
        for ch, w in zip(s, widths):
            draw.text((x, y), ch, font=f, fill=fill)
            x += w + spacing
        return total, f.size
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)
    return w, f.size


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, y), (x1, y)], fill=c)


def paper_texture(base, rng_seed=42):
    """Subtle paper grain tiled over the poster."""
    tile = Image.effect_noise((270, 250), 14).convert("L")
    tile = tile.point(lambda v: 128 + (v - 128) // 6)
    tex = Image.new("L", base.size, 128)
    for ty in range(0, base.size[1], 250):
        for tx in range(0, base.size[0], 270):
            tex.paste(tile, (tx, ty))
    fib = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fib)
    rng = random.Random(rng_seed)
    for _ in range(90):
        x, y = rng.randint(0, W), rng.randint(0, H)
        ln = rng.randint(12, 60)
        ang = rng.uniform(0, math.pi)
        fd.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))],
                fill=(120, 100, 60, 26), width=1)
    out = ImageChops.add(base.convert("RGB"), Image.merge("RGB", (tex, tex, tex)),
                         scale=1.0, offset=-128)
    out.paste(fib, (0, 0), fib)
    return out


def draw_scene(draw, box, rng):
    """Procedural Vice City sunset inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    mid = y0 + int(h * 0.55)
    vgrad(draw, (x0, y0, x1, mid), DUSK_TOP, DUSK_MID)
    vgrad(draw, (x0, mid, x1, y1), DUSK_MID, DUSK_LOW)
    # sun + halo
    sx, sy, sr = x0 + int(w * 0.42), y0 + int(h * 0.52), int(h * 0.30)
    for r in (sr + 26, sr + 12):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], outline=(252, 200, 120), width=3)
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SUN)
    # stars
    for _ in range(26):
        px, py = rng.randint(x0 + 6, x1 - 6), rng.randint(y0 + 6, y0 + int(h * 0.30))
        draw.point((px, py), fill=(255, 240, 200))
    # birds
    for bx, by, s in ((x0 + int(w * 0.68), y0 + 26, 9), (x0 + int(w * 0.76), y0 + 44, 7),
                      (x0 + int(w * 0.60), y0 + 58, 6)):
        draw.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340, fill=(30, 20, 40), width=2)
        draw.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340, fill=(30, 20, 40), width=2)
    # far skyline (lighter purple)
    base = y0 + int(h * 0.66)
    x = x0
    while x < x1:
        bw = rng.randint(34, 78)
        bh = rng.randint(int(h * 0.10), int(h * 0.26))
        draw.rectangle([x, base - bh, min(x + bw, x1), base], fill=(96, 52, 110))
        if rng.random() < 0.4:
            draw.line([(x + bw // 2, base - bh), (x + bw // 2, base - bh - 16)],
                      fill=(96, 52, 110), width=2)
        x += bw + rng.randint(2, 10)
    # near skyline (dark) with lit windows
    x = x0
    while x < x1:
        bw = rng.randint(46, 96)
        bh = rng.randint(int(h * 0.20), int(h * 0.40))
        draw.rectangle([x, base - bh, min(x + bw, x1), base], fill=(34, 22, 52))
        for _ in range(rng.randint(1, 5)):
            wx = rng.randint(x + 5, max(x + 6, min(x + bw - 8, x1 - 8)))
            wy = rng.randint(base - bh + 6, base - 10)
            draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(252, 214, 120))
        x += bw + rng.randint(0, 8)
    # palms (silhouettes, long drooping fronds)
    for px in (x0 + int(w * 0.07), x0 + int(w * 0.93)):
        top = base - rng.randint(int(h * 0.34), int(h * 0.42))
        # curved trunk: 3 segments leaning slightly
        pts = [(px, base), (px + 3, base - (base - top) // 2), (px + 5, top)]
        draw.line(pts, fill=(24, 16, 38), width=7, joint="curve")
        # 5 fronds: quadratic droop curves from the crown
        for k in range(5):
            side = 1 if k % 2 == 0 else -1
            spread = (14 + 16 * k) * side
            tipx = px + 5 + spread
            tipy = top + 26 + 10 * (k % 3)
            midx = px + 5 + spread * 0.55
            midy = top - 14
            n = 12
            curve = []
            for s in range(n + 1):
                t = s / n
                qx = (1 - t) ** 2 * (px + 5) + 2 * (1 - t) * t * midx + t * t * tipx
                qy = (1 - t) ** 2 * top + 2 * (1 - t) * t * midy + t * t * tipy
                curve.append((qx, qy))
            draw.line(curve, fill=(24, 16, 38), width=3, joint="curve")
        # coconut cluster
        draw.ellipse([px + 1, top - 2, px + 11, top + 8], fill=(24, 16, 38))
    # water + sun reflection
    draw.rectangle([x0, base, x1, y1], fill=(40, 20, 64))
    for i, (rx, rw, col) in enumerate(((0.30, 0.24, (252, 150, 80)),
                                       (0.36, 0.16, (252, 180, 110)),
                                       (0.28, 0.30, (232, 110, 68)))):
        yy = base + 10 + i * 14
        draw.line([(x0 + int(w * rx), yy), (x0 + int(w * (rx + rw)), yy)],
                  fill=col, width=4)


def make_stamp():
    """Rotated rubber stamp, transparent layer (~310x133 after rotation)."""
    sw, sh = 320, 92
    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([5, 5, sw - 5, sh - 5], radius=12, outline=MAGENTA + (255,), width=4)
    d.rounded_rectangle([11, 11, sw - 11, sh - 11], radius=8, outline=MAGENTA + (255,), width=2)
    f1 = font(ANTON, 33)
    f2 = font(SANS, 17)
    text_center(d, sw // 2, 16, "STILL MISSING", f1, MAGENTA + (255,))
    text_center(d, sw // 2, 56, "BY MY AI AGENT · MAKE.FUN", f2, MAGENTA + (255,))
    return layer.rotate(-8, expand=True, resample=Image.BICUBIC)


def main():
    rng = random.Random(7)
    img = Image.new("RGB", (W, H), NAVY_D)
    d = ImageDraw.Draw(img, "RGBA")
    vgrad(d, (0, 0, W, H), NAVY, NAVY_D)

    # poster
    px0, py0, px1, py1 = 70, 36, 1010, 1044
    poster = Image.new("RGB", (px1 - px0, py1 - py0), CREAM)
    poster = paper_texture(poster)
    img.paste(poster, (px0, py0))
    d = ImageDraw.Draw(img, "RGBA")

    # ornate double frame + corner squares
    d.rectangle([px0 + 12, py0 + 12, px1 - 12, py1 - 12], outline=NAVY, width=4)
    d.rectangle([px0 + 24, py0 + 24, px1 - 24, py1 - 24], outline=GOLD, width=2)
    for cx, cy in ((px0 + 12, py0 + 12), (px1 - 12, py0 + 12),
                   (px0 + 12, py1 - 12), (px1 - 12, py1 - 12)):
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD, outline=NAVY, width=2)

    # tape corners
    for tx, flip in ((px0 - 6, 1), (px1 - 150, -1)):
        tape = Image.new("RGBA", (160, 56), (0, 0, 0, 0))
        td = ImageDraw.Draw(tape)
        td.polygon([(4, 6), (156, 2), (152, 50), (8, 54)], fill=(235, 225, 190, 150))
        tape = tape.rotate(-24 * flip, expand=True, resample=Image.BICUBIC)
        img.paste(tape, (tx, py0 - 26), tape)

    # file number (top right, mono)
    fmono = font(MONO, 21)
    d.text((px1 - 40 - d.textlength("FILE NO. VI-2013-2026", font=fmono), py0 + 44),
           "FILE NO. VI-2013-2026", font=fmono, fill=(90, 80, 60))

    # header
    f_big = font(ANTON, 148)
    text_center(d, W // 2, py0 + 62, "MISSING", f_big, INK, spacing=6)
    d.line([(px0 + 150, py0 + 228), (px1 - 150, py0 + 228)], fill=RED, width=7)
    f_sub = font(ANTON, 62)
    text_center(d, W // 2, py0 + 248, "GRAND THEFT AUTO VI", f_sub, INK, spacing=2)

    # scene
    sx0, sy0, sx1, sy1 = px0 + 48, py0 + 332, px1 - 48, py0 + 606
    d.rectangle([sx0 - 4, sy0 - 4, sx1 + 4, sy1 + 4], outline=NAVY, width=4)
    draw_scene(d, (sx0, sy0, sx1, sy1), rng)

    # ghost mark inside scene, bottom-right (press-kit asset)
    ghost = Image.open(f"{ASSETS}/mark-1024.png").convert("RGBA")
    ghost.thumbnail((118, 118), Image.LANCZOS)
    img.paste(ghost, (sx1 - 8 - ghost.width, sy1 - 8 - ghost.height), ghost)
    d = ImageDraw.Draw(img, "RGBA")

    # body copy
    f_body = font(SANS, 33)
    text_center(d, W // 2, py0 + 624, "LAST SEEN:  Trailer 1 — December 2023",
                f_body, INK)
    f_red = font(ANTON, 54)
    text_center(d, W // 2, py0 + 668, "13 YEARS OF WAITING...", f_red, RED)
    text_center(d, W // 2, py0 + 724, "AND COUNTING", f_red, RED)
    f_b2 = font(SANS, 32)
    text_center(d, W // 2, py0 + 792, "IF FOUND, PLEASE RETURN TO MY PS5",
                f_b2, INK)

    # stat boxes
    by0, by1 = py0 + 830, py0 + 898
    bw = 272
    gap = 14
    bx = px0 + 48
    stats = [("DAYS WAITING", f"{DAYS_WAITING:,}"),
             ("LAST SEEN", "DEC 2023"),
             ("REWARD", "MAKE.FUN")]
    flab = font(SANS, 18)
    fval = font(ANTON, 32)
    for lab, val in stats:
        d.rounded_rectangle([bx, by0, bx + bw, by1], radius=8,
                            outline=NAVY, width=2, fill=(238, 228, 202))
        text_center(d, bx + bw // 2, by0 + 8, lab, flab, (110, 100, 80))
        text_center(d, bx + bw // 2, by0 + 28, val, fval, NAVY)
        bx += bw + gap

    # rubber stamp, bottom-left (fits 908..1041 inside poster)
    stamp = make_stamp()
    img.paste(stamp, (px0 + 40, py0 + 908), stamp)
    d = ImageDraw.Draw(img, "RGBA")

    # tear-off strips, right side only (stamp occupies the left)
    ty0, ty1 = py1 - 58, py1 - 14
    tx_start, tx_end = px0 + 400, px1 - 48
    n_tabs = 6
    tab_w = (tx_end - tx_start) // n_tabs
    f_tab = font(SANS, 19)
    for i in range(n_tabs):
        tx0 = tx_start + i * tab_w
        d.rectangle([tx0, ty0, tx0 + tab_w - 4, ty1], outline=(120, 105, 75), width=1)
        d.line([(tx0 + tab_w // 2, ty0), (tx0 + tab_w // 2, ty0 + 8)],
               fill=(120, 105, 75), width=1)
        text_center(d, tx0 + (tab_w - 4) // 2, ty0 + 16, "GTA VI", f_tab, (110, 100, 80))

    img.save(OUT, optimize=True)
    print("saved", OUT, "days_waiting", DAYS_WAITING)


if __name__ == "__main__":
    main()
