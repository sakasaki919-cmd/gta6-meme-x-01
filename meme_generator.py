#!/usr/bin/env python3
"""Generate 3 original GTA 6 memes for the make.fun bounty gta6-meme-x-01.

Everything is drawn procedurally with PIL: flat vector-style characters,
buildings, a balance scale and a store shelf. No GTA screenshots, no official
artwork. The only photographic asset is make.fun's own ghost mark from the
press kit (assets/mark-1024.png), composited into every scene so the judge's
criterion #1 (make.fun in the picture) is met.

Captions come from captions.json. All caption text is rendered with Anton
(Impact-style, OFL) in white with a thick black outline, sized to stay
readable when the picture is shrunk to 480x480 (the size the judge sees).

Usage:  python3 meme_generator.py            # writes meme-1/2/3.png (1080x1080)
        python3 meme_generator.py --check    # also writes 480px previews
"""

import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
W = H = 1080

# ---------------------------------------------------------------- fonts

ANTON = os.path.join(ASSETS, "Anton-Regular.ttf")
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(DEJAVU_BOLD, size)


def caption_font(size):
    return font(ANTON, size)


def small_font(size):
    return font(DEJAVU_BOLD, size)


# ---------------------------------------------------------------- helpers

def gradient(img, box, top, bottom):
    """Vertical gradient inside box=(x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(x0, y), (x1, y)], fill=c)


def outlined_text(d, xy, text, fnt, fill=(255, 255, 255), stroke=(0, 0, 0), sw=None):
    """White meme text with a thick black outline."""
    if sw is None:
        sw = max(2, fnt.size // 12)
    d.text(xy, text, font=fnt, fill=fill, stroke_width=sw, stroke_fill=stroke)


def fit_lines(lines, max_w, start, minimum=28):
    """Largest Anton size (<= start) where every line fits max_w."""
    size = start
    while size > minimum:
        fnt = caption_font(size)
        ok = True
        for ln in lines:
            bbox = fnt.getbbox(ln)
            if bbox[2] - bbox[0] > max_w:
                ok = False
                break
        if ok:
            return fnt
        size -= 2
    return caption_font(minimum)


def draw_caption(d, lines, y, max_w, start=92, color=(255, 255, 255)):
    """Centered multi-line caption starting at y. Returns y after the block."""
    fnt = fit_lines(lines, max_w, start)
    for ln in lines:
        bbox = fnt.getbbox(ln)
        w = bbox[2] - bbox[0]
        outlined_text(d, ((W - w) // 2, y), ln, fnt, fill=color)
        y += int(fnt.size * 1.08)
    return y


def paste_ghost(img, cx, cy, size):
    """Paste the real make.fun ghost mark, centred at (cx, cy)."""
    ghost = Image.open(os.path.join(ASSETS, "mark-1024.png")).convert("RGBA")
    ghost = ghost.resize((size, size), Image.LANCZOS)
    img.paste(ghost, (int(cx - size // 2), int(cy - size // 2)), ghost)


def draw_person(d, cx, ground_y, s, skin=(255, 205, 165), shirt=(25, 118, 180),
                pants=(45, 45, 70), hair=(60, 40, 25), backpack=None,
                beard=False, glasses=False, cap=None, point=False):
    """Simple flat character, facing forward, feet at ground_y. s = head radius."""
    # legs
    leg_w = int(s * 0.34)
    leg_h = int(s * 1.05)
    hip_y = ground_y - leg_h
    d.rectangle([cx - leg_w - int(s * 0.12), hip_y, cx - int(s * 0.12), ground_y],
                fill=pants)
    d.rectangle([cx + int(s * 0.12), hip_y, cx + leg_w + int(s * 0.12), ground_y],
                fill=pants)
    # shoes
    d.ellipse([cx - leg_w - int(s * 0.22), ground_y - int(s * 0.16),
               cx - int(s * 0.05), ground_y + int(s * 0.10)], fill=(30, 30, 30))
    d.ellipse([cx + int(s * 0.05), ground_y - int(s * 0.16),
               cx + leg_w + int(s * 0.22), ground_y + int(s * 0.10)], fill=(30, 30, 30))
    # torso (rounded)
    torso_w = int(s * 1.15)
    torso_h = int(s * 1.35)
    top_y = hip_y - torso_h
    d.rounded_rectangle([cx - torso_w, top_y, cx + torso_w, hip_y + int(s * 0.15)],
                        radius=int(s * 0.35), fill=shirt)
    # backpack (behind torso, drawn on the left side)
    if backpack:
        d.rounded_rectangle([cx - torso_w - int(s * 0.55), top_y + int(s * 0.25),
                             cx - torso_w + int(s * 0.25), hip_y - int(s * 0.1)],
                            radius=int(s * 0.25), fill=backpack)
    # arm pointing right (toward the poster)
    if point:
        d.line([(cx + torso_w - int(s * 0.1), top_y + int(s * 0.45)),
                (cx + torso_w + int(s * 1.05), top_y + int(s * 0.15))],
               fill=shirt, width=int(s * 0.32))
        d.ellipse([cx + torso_w + int(s * 0.85), top_y - int(s * 0.05),
                   cx + torso_w + int(s * 1.25), top_y + int(s * 0.35)], fill=skin)
    else:
        d.line([(cx - torso_w + int(s * 0.1), top_y + int(s * 0.4)),
                (cx - torso_w - int(s * 0.25), hip_y - int(s * 0.2))],
               fill=shirt, width=int(s * 0.3))
    # head
    head_r = s
    head_cy = top_y - int(s * 0.85)
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
              fill=skin)
    # hair (top half of head)
    d.pieslice([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
               start=180, end=360, fill=hair)
    d.rectangle([cx - head_r, head_cy - int(s * 0.25), cx + head_r, head_cy],
                fill=hair)
    # cap
    if cap:
        d.pieslice([cx - head_r - int(s * 0.1), head_cy - head_r - int(s * 0.25),
                    cx + head_r + int(s * 0.1), head_cy + int(s * 0.35)],
                   start=180, end=360, fill=cap)
        d.rectangle([cx + head_r - int(s * 0.2), head_cy - int(s * 0.35),
                     cx + head_r + int(s * 0.75), head_cy - int(s * 0.05)], fill=cap)
    # beard: chin only, so the smile still shows
    if beard:
        d.pieslice([cx - int(head_r * 0.85), head_cy + int(s * 0.25),
                    cx + int(head_r * 0.85), head_cy + head_r + int(s * 0.2)],
                   start=0, end=180, fill=hair)
    # glasses
    if glasses:
        gr = int(s * 0.34)
        gy = head_cy - int(s * 0.1)
        for gx in (cx - int(s * 0.48), cx + int(s * 0.48)):
            d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr],
                      outline=(20, 20, 20), width=max(2, int(s * 0.09)))
        d.line([(cx - int(s * 0.14), gy), (cx + int(s * 0.14), gy)],
               fill=(20, 20, 20), width=max(2, int(s * 0.09)))
    # eyes
    er = max(2, int(s * 0.09))
    ey = head_cy - int(s * 0.15)
    for ex in (cx - int(s * 0.42), cx + int(s * 0.42)):
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(20, 20, 20))
    # smile
    d.arc([cx - int(s * 0.35), head_cy + int(s * 0.15),
           cx + int(s * 0.35), head_cy + int(s * 0.75)],
          start=15, end=165, fill=(20, 20, 20), width=max(2, int(s * 0.08)))
    return head_cy


def draw_school(d, x, y, w, h, dark=False):
    """Simple school building with windows and a flag."""
    wall = (150, 90, 70) if not dark else (110, 65, 55)
    roof = (120, 60, 50) if not dark else (90, 45, 40)
    d.rectangle([x, y, x + w, y + h], fill=wall)
    d.polygon([(x - 12, y), (x + w // 2, y - 42), (x + w + 12, y)], fill=roof)
    win = (255, 240, 180) if not dark else (255, 220, 130)
    for r in range(2):
        for c in range(3):
            wx = x + 24 + c * (w // 3)
            wy = y + 30 + r * (h // 2 - 10)
            d.rectangle([wx, wy, wx + 44, wy + 44], fill=win)
    # flag pole + flag
    px = x + w // 2
    d.line([(px, y - 42), (px, y - 95)], fill=(40, 40, 40), width=5)
    d.polygon([(px, y - 95), (px + 52, y - 82), (px, y - 69)], fill=(230, 0, 126))


def draw_poster(d, x, y, w, h, title, year, dark=False):
    """Poster board on two legs: big GTA VI + year."""
    # legs
    d.rectangle([x + 18, y + h, x + 30, y + h + 58], fill=(90, 60, 35))
    d.rectangle([x + w - 30, y + h, x + w - 18, y + h + 58], fill=(90, 60, 35))
    # board
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=(30, 30, 30), width=6)
    # sunset strip on the poster (a nod to Vice City, drawn, not a photo)
    strip_h = int(h * 0.30)
    for yy in range(y + 6, y + 6 + strip_h):
        t = (yy - y - 6) / max(1, strip_h)
        c = (int(255 - 60 * t), int(120 + 60 * t), int(90 + 90 * t))
        d.line([(x + 6, yy), (x + w - 6, yy)], fill=c)
    # sun dot
    d.ellipse([x + w // 2 - 26, y + 22, x + w // 2 + 26, y + 74], fill=(255, 240, 180))
    # title
    tf = fit_lines([title], w - 24, 64)
    bbox = tf.getbbox(title)
    tw = bbox[2] - bbox[0]
    d.text((x + (w - tw) // 2, y + int(h * 0.38)), title, font=tf, fill=(20, 20, 30))
    # year
    yf = fit_lines([year], w - 24, 52)
    bbox = yf.getbbox(year)
    yw = bbox[2] - bbox[0]
    d.text((x + (w - yw) // 2, y + int(h * 0.68)), year, font=yf, fill=(180, 0, 90))


# ---------------------------------------------------------------- meme 1

def meme_1(cap):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # --- top caption (own band, so it never clips) ---
    draw_caption(d, cap["top"], 10, W - 60, start=72)
    # --- top panel: 2013, high school, sunset ---
    py0, py1 = 166, 525
    gradient(img, (0, py0, W, py1), (255, 126, 95), (255, 205, 130))
    d.ellipse([310, py0 + 19, 420, py0 + 129], fill=(255, 240, 180))
    # clouds (clear of the student, the ghost and the poster)
    for cx, cy, cw in ((150, py0 + 44, 150), (500, py0 + 34, 170)):
        d.ellipse([cx, cy, cx + cw, cy + 44], fill=(255, 255, 255))
    ground = py1 - 60
    d.rectangle([0, ground, W, py1], fill=(125, 180, 95))
    draw_school(d, 60, ground - 190, 220, 190)
    # year label
    yf = small_font(44)
    d.text((70, py0 + 8), "2013", font=yf, fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0))
    # young student pointing at the poster
    draw_person(d, 420, ground, 52, shirt=(25, 118, 180), backpack=(220, 60, 60),
                point=True)
    # poster: GTA VI 2025
    draw_poster(d, 700, ground - 260, 300, 220, cap["poster_top"],
                cap["poster_year_top"])
    # ghost: small, floating in the sky between student and poster
    paste_ghost(img, 620, ground - 185, 120)
    # divider
    d.rectangle([0, py1, W, py1 + 8], fill=(255, 255, 255))
    # --- bottom panel: 2026, older + kid, dusk ---
    qy0, qy1 = py1 + 8, 895
    gradient(img, (0, qy0, W, qy1), (70, 70, 140), (160, 110, 190))
    # stars + full moon
    for sx, sy in ((90, qy0 + 40), (250, qy0 + 90), (520, qy0 + 30), (760, qy0 + 80),
                   (980, qy0 + 35), (640, qy0 + 120), (380, qy0 + 55)):
        d.ellipse([sx, sy, sx + 8, sy + 8], fill=(255, 255, 255))
    d.ellipse([520, qy0 + 12, 610, qy0 + 102], fill=(240, 240, 220))
    qground = qy1 - 60
    d.rectangle([0, qground, W, qy1], fill=(70, 110, 70))
    draw_school(d, 60, qground - 190, 220, 190, dark=True)
    yf = small_font(44)
    d.text((70, qy0 + 8), "2026", font=yf, fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0))
    # older parent + kid, pointing at the same poster
    draw_person(d, 400, qground, 58, shirt=(35, 45, 90), pants=(30, 30, 45),
                hair=(90, 90, 95), beard=True, glasses=True, point=True)
    draw_person(d, 560, qground, 30, shirt=(240, 180, 40), pants=(45, 45, 70),
                hair=(60, 40, 25), backpack=(230, 0, 126), cap=(220, 60, 60))
    # poster: GTA VI 2026...
    draw_poster(d, 700, qground - 260, 300, 220, cap["poster_top"],
                cap["poster_year_bottom"], dark=True)
    # ghost: bigger now, beside the poster (it waited all these years)
    paste_ghost(img, 710, qground - 195, 150)
    # --- bottom caption (own band, so it never clips) ---
    draw_caption(d, cap["bottom"], 903, W - 60, start=72)
    return img


# ---------------------------------------------------------------- meme 2

def meme_2(cap):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    gradient(img, (0, 0, W, H), (255, 250, 238), (255, 228, 196))
    # --- top caption ---
    draw_caption(d, cap["top"], 24, W - 60, start=100)
    # --- balance scale ---
    cx, top_y, base_y = W // 2, 210, 900
    # base + pole
    d.ellipse([cx - 130, base_y - 26, cx + 130, base_y + 6], fill=(60, 60, 80))
    d.rectangle([cx - 14, top_y, cx + 14, base_y - 20], fill=(60, 60, 80))
    d.ellipse([cx - 34, top_y - 34, cx + 34, top_y + 34], fill=(230, 0, 126))
    # beam, tilted: left (game) side down, right (paycheck) side up
    lx, ly = cx - 330, top_y + 150
    rx, ry = cx + 330, top_y - 60
    d.line([(lx, ly), (rx, ry)], fill=(60, 60, 80), width=26)
    # left pan (game, heavy, low)
    d.line([(lx, ly), (lx, ly + 120)], fill=(60, 60, 80), width=8)
    d.polygon([(lx - 150, ly + 120), (lx + 150, ly + 120), (lx, ly + 190)],
              fill=(90, 60, 35))
    # game box on the left pan (tall enough for two separate labels)
    bx0, by0, bx1, by1 = lx - 140, ly, lx + 140, ly + 190
    d.rectangle([bx0, by0, bx1, by1], fill=(230, 0, 126), outline=(30, 30, 30),
                width=6)
    d.rectangle([bx0, by0, bx1, by0 + 50], fill=(255, 255, 255))
    gf = fit_lines([cap["game_label"]], bx1 - bx0 - 20, 56)
    bbox = gf.getbbox(cap["game_label"])
    d.text((bx0 + (bx1 - bx0 - (bbox[2] - bbox[0])) // 2, by0 + 62),
           cap["game_label"], font=gf, fill=(255, 255, 255))
    pf = fit_lines([cap["game_price"]], bx1 - bx0 - 20, 50)
    bbox = pf.getbbox(cap["game_price"])
    d.text((bx0 + (bx1 - bx0 - (bbox[2] - bbox[0])) // 2, by0 + 126),
           cap["game_price"], font=pf, fill=(255, 240, 180))
    # right pan (paycheck, light, high)
    d.line([(rx, ry), (rx, ry + 120)], fill=(60, 60, 80), width=8)
    d.polygon([(rx - 150, ry + 120), (rx + 150, ry + 120), (rx, ry + 190)],
              fill=(90, 60, 35))
    # thin wallet on the right pan
    wx0, wy0, wx1, wy1 = rx - 130, ry + 60, rx + 130, ry + 150
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=18, fill=(140, 95, 55),
                        outline=(30, 30, 30), width=5)
    d.rectangle([wx0, wy0 + 34, wx1, wy0 + 52], fill=(110, 70, 40))
    # wallet clasp
    d.ellipse([wx1 - 52, wy0 + 58, wx1 - 22, wy0 + 88], fill=(255, 201, 60),
              outline=(120, 85, 0), width=3)
    wf = fit_lines([cap["wallet_label"]], wx1 - wx0 - 16, 34)
    bbox = wf.getbbox(cap["wallet_label"])
    d.text((wx0 + (wx1 - wx0 - (bbox[2] - bbox[0])) // 2, ry + 200),
           cap["wallet_label"], font=wf, fill=(30, 30, 30))
    # three coins spilling from the wallet
    for i, (ccx, ccy) in enumerate(((rx - 70, ry + 30), (rx, ry + 18), (rx + 70, ry + 32))):
        d.ellipse([ccx - 30, ccy - 30, ccx + 30, ccy + 30], fill=(255, 201, 60),
                  outline=(180, 130, 0), width=4)
        cf = small_font(34)
        bbox = cf.getbbox("$")
        d.text((ccx - (bbox[2] - bbox[0]) // 2, ccy - 24), "$", font=cf,
               fill=(150, 100, 0))
    # ghost: perched on the game side of the beam, adding its weight
    paste_ghost(img, lx + 40, ly - 100, 210)
    # --- bottom caption (own band, so it never clips) ---
    draw_caption(d, cap["bottom"], 905, W - 60, start=72)
    return img


# ---------------------------------------------------------------- meme 3

def meme_3(cap):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    gradient(img, (0, 0, W, H), (205, 222, 236), (175, 200, 220))
    # --- top caption ---
    draw_caption(d, cap["top"], 24, W - 60, start=96)
    # floor
    d.rectangle([0, 880, W, H], fill=(198, 158, 110))
    d.line([(0, 880), (W, 880)], fill=(150, 110, 70), width=4)
    # --- empty shelf ---
    sx0, sx1 = 90, 990
    for sy in (330, 560):
        d.rectangle([sx0, sy, sx1, sy + 26], fill=(150, 100, 60),
                    outline=(90, 60, 35), width=4)
        # brackets
        d.rectangle([sx0 + 30, sy + 26, sx0 + 46, sy + 62], fill=(90, 60, 35))
        d.rectangle([sx1 - 46, sy + 26, sx1 - 30, sy + 62], fill=(90, 60, 35))
    # dust + cobweb on the empty top shelf
    d.ellipse([sx0 + 60, 330 - 14, sx0 + 120, 330 + 2], fill=(200, 200, 200))
    d.ellipse([sx1 - 180, 330 - 10, sx1 - 120, 330 + 2], fill=(200, 200, 200))
    for k in range(4):
        d.line([(sx0 + 40, 330), (sx0 + 40 + k * 26, 330 - 46 - k * 8)],
               fill=(255, 255, 255), width=3)
    # SOLD OUT sign hanging on the top shelf
    sign_w, sign_h = 330, 96
    sign_x, sign_y = (W - sign_w) // 2, 356
    d.line([(sign_x + 40, 330), (sign_x + 40, sign_y)], fill=(40, 40, 40), width=5)
    d.line([(sign_x + sign_w - 40, 330), (sign_x + sign_w - 40, sign_y)],
           fill=(40, 40, 40), width=5)
    d.rounded_rectangle([sign_x, sign_y, sign_x + sign_w, sign_y + sign_h],
                        radius=14, fill=(215, 38, 61), outline=(30, 30, 30), width=5)
    sf = fit_lines([cap["sign"]], sign_w - 24, 58)
    bbox = sf.getbbox(cap["sign"])
    d.text((sign_x + (sign_w - (bbox[2] - bbox[0])) // 2,
            sign_y + (sign_h - (bbox[3] - bbox[1])) // 2 - 6),
           cap["sign"], font=sf, fill=(255, 255, 255))
    # price tags left on the shelf (PS5, GTA VI) — clear of the fan and the box
    for tx, label in ((100, "PS5"), (580, "GTA VI")):
        d.rounded_rectangle([tx, 586, tx + 120, 640], radius=8, fill=(255, 255, 255),
                            outline=(30, 30, 30), width=4)
        tf = small_font(30)
        bbox = tf.getbbox(label)
        d.text((tx + (120 - (bbox[2] - bbox[0])) // 2, 600), label, font=tf,
               fill=(30, 30, 30))
    # ghost: sitting on the top shelf, holding the bad news
    paste_ghost(img, 860, 300, 200)
    # --- fan holding a GTA VI box, staring at the empty shelf ---
    draw_person(d, 300, 880, 62, shirt=(25, 118, 180), pants=(45, 45, 70),
                hair=(60, 40, 25))
    # game box in hand
    d.rectangle([380, 640, 520, 780], fill=(230, 0, 126), outline=(30, 30, 30),
                width=5)
    gf = fit_lines(["GTA VI"], 120, 44)
    bbox = gf.getbbox("GTA VI")
    d.text((380 + (140 - (bbox[2] - bbox[0])) // 2, 700), "GTA VI", font=gf,
           fill=(255, 255, 255))
    # --- scalper in the corner with a stack of consoles ---
    scx = 850
    for i in range(3):
        yy = 880 - (i + 1) * 64
        d.rectangle([scx - 70, yy, scx + 70, yy + 56], fill=(40, 45, 70),
                    outline=(255, 255, 255), width=3)
        d.text((scx - 34, yy + 12), "PS5", font=small_font(28), fill=(255, 255, 255))
    # scalper price sign leaning against the stack (clear of the head)
    d.rounded_rectangle([scx - 160, 760, scx - 70, 812], radius=10,
                        fill=(255, 201, 60), outline=(30, 30, 30), width=4)
    pf = fit_lines([cap["scalper_price"]], 80, 32)
    bbox = pf.getbbox(cap["scalper_price"])
    d.text((scx - 160 + (90 - (bbox[2] - bbox[0])) // 2, 772),
           cap["scalper_price"], font=pf, fill=(150, 60, 0))
    # scalper head peeking over the stack
    d.ellipse([scx - 34, 880 - 3 * 64 - 66, scx + 34, 880 - 3 * 64 + 2],
              fill=(255, 205, 165))
    d.pieslice([scx - 34, 880 - 3 * 64 - 66, scx + 34, 880 - 3 * 64 + 2],
               start=180, end=360, fill=(20, 20, 20))
    # --- bottom caption (own band, so it never clips) ---
    draw_caption(d, cap["bottom"], 905, W - 60, start=72)
    return img


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="also write 480px previews (judge size)")
    args = ap.parse_args()

    with open(os.path.join(HERE, "captions.json")) as f:
        caps = json.load(f)

    makers = {"meme-1": meme_1, "meme-2": meme_2, "meme-3": meme_3}
    for name, fn in makers.items():
        img = fn(caps[name])
        out = os.path.join(HERE, name + ".png")
        img.save(out, "PNG")
        print(f"wrote {out} {img.size}")
        if args.check:
            prev = img.resize((480, 480), Image.LANCZOS)
            pout = os.path.join(HERE, name + "-480.png")
            prev.save(pout, "PNG")
            print(f"wrote {pout} {prev.size}")


if __name__ == "__main__":
    main()
