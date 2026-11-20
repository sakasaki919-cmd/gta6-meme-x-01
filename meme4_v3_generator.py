#!/usr/bin/env python3
"""Meme #4 (rebuild v3): BACHELOR'S DEGREE CERTIFICATE for waiting for GTA VI.

Concept (ours, per user: "sertifikat sarjana"): Leonida University confers
the degree of Bachelor of Waiting in GTA VI Studies upon the fans.
Style: luxurious official certificate -- ornate double frame, paper
texture, circular university seal, round rubber stamp + ribbon, signatures.
All art is procedural (PIL); the make.fun ghost mark is composited from
the press-kit asset in assets/mark-1024.png. 1080x1080, deterministic.
"""
import math
import random
from datetime import date

from PIL import Image, ImageDraw, ImageFont, ImageChops

W = H = 1080
OUT = "meme-4.png"
ASSETS = "assets"
ANTON = f"{ASSETS}/Anton-Regular.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (26, 34, 64)
NAVY_D = (18, 25, 45)
CREAM = (244, 236, 216)
INK = (24, 24, 28)
RED = (178, 34, 34)
MAGENTA = (176, 24, 92)
GOLD = (176, 141, 68)
GOLD_L = (201, 168, 92)

TODAY = date(2026, 11, 20)  # fixed so re-runs are byte-identical


def font(path, size):
    return ImageFont.truetype(path, size)


def text_center(draw, cx, y, s, f, fill, spacing=0):
    """Draw text centred on cx."""
    if spacing:
        widths = [draw.textlength(ch, font=f) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x = cx - total / 2
        for ch, w in zip(s, widths):
            draw.text((x, y), ch, font=f, fill=fill)
            x += w + spacing
        return total
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)
    return w


def arc_text(base, cx, cy, r, text, f, fill, a0, a1, bottom=False):
    """Draw text along a circle. a0..a1 in degrees, 0 = top (or bottom)."""
    n = len(text)
    for i, ch in enumerate(text):
        t = a0 + (a1 - a0) * (i / max(1, n - 1)) if n > 1 else (a0 + a1) / 2
        th = math.radians(t)
        if bottom:
            x = cx + r * math.sin(th)
            y = cy + r * math.cos(th)
            rot = t
        else:
            x = cx + r * math.sin(th)
            y = cy - r * math.cos(th)
            rot = -t
        tile = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((30, 30), ch, font=f, fill=fill, anchor="mm")
        tile = tile.rotate(rot, expand=False, resample=Image.BICUBIC, center=(30, 30))
        base.paste(tile, (int(x - 30), int(y - 30)), tile)


def star(draw, cx, cy, r_out, r_in, fill):
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        ang = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def paper_texture(base, rng_seed=11):
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


def draw_seal(img, cx, cy, r):
    """Circular university seal with a graduation cap in the centre."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY + (255,), width=4)
    d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
              outline=GOLD + (255,), width=2)
    f_arc = font(SERIF, 13)
    arc_text(layer, cx, cy, r - 22, "LEONIDA UNIVERSITY", f_arc, NAVY + (255,),
             -78, 78)
    arc_text(layer, cx, cy, r - 22, "EST. 2013", f_arc, NAVY + (255,),
             -42, 42, bottom=True)
    # graduation cap: board diamond + head + tassel
    d.polygon([(cx - 26, cy - 2), (cx, cy - 18), (cx + 26, cy - 2), (cx, cy + 14)],
              fill=NAVY + (255,))
    d.polygon([(cx - 12, cy + 2), (cx + 12, cy + 2), (cx + 8, cy + 16),
               (cx - 8, cy + 16)], fill=NAVY + (255,))
    d.line([(cx + 26, cy - 2), (cx + 34, cy + 14)], fill=GOLD + (255,), width=3)
    d.ellipse([cx + 30, cy + 12, cx + 38, cy + 20], fill=GOLD + (255,))
    img.paste(layer, (0, 0), layer)


def draw_stamp(img, cx, cy, r):
    """Round magenta stamp + ribbon tails, rotated slightly."""
    w = int(r * 2.6)
    layer = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cc = w // 2
    d.ellipse([cc - r, cc - r, cc + r, cc + r], outline=MAGENTA + (255,), width=4)
    d.ellipse([cc - r + 7, cc - r + 7, cc + r - 7, cc + r - 7],
              outline=MAGENTA + (255,), width=2)
    f_arc = font(SANS, 13)
    arc_text(layer, cc, cc, r - 14, "LEONIDA UNIVERSITY", f_arc, MAGENTA + (255,),
             -75, 75)
    arc_text(layer, cc, cc, r - 14, "PAID BY MY AI AGENT", f_arc, MAGENTA + (255,),
             -75, 75, bottom=True)
    star(d, cc, cc - 14, 18, 8, MAGENTA + (255,))
    f_y = font(ANTON, 22)
    text_center(d, cc, cc + 10, "2026", f_y, MAGENTA + (255,))
    f_m = font(MONO, 13)
    text_center(d, cc, cc + 34, "MAKE.FUN", f_m, MAGENTA + (255,))
    # ribbon tails below the seal
    d.polygon([(cc - 26, cc + r - 4), (cc - 14, cc + r - 4), (cc - 20, cc + r + 22),
               (cc - 26, cc + r + 16), (cc - 32, cc + r + 22)],
              fill=MAGENTA + (255,))
    d.polygon([(cc + 14, cc + r - 4), (cc + 26, cc + r - 4), (cc + 32, cc + r + 22),
               (cc + 26, cc + r + 16), (cc + 20, cc + r + 22)],
              fill=MAGENTA + (255,))
    layer = layer.rotate(-8, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (cx - layer.width // 2, cy - layer.height // 2), layer)


def diamond(draw, cx, cy, s, fill):
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=fill)


def main():
    # paper
    img = paper_texture(Image.new("RGB", (W, H), CREAM))
    d = ImageDraw.Draw(img, "RGBA")

    # faint "VI" watermark
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((W // 2, 700), "VI", font=font(SERIF, 430), fill=GOLD + (12,),
            anchor="mm")
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ornate double frame + corner squares
    d.rectangle([26, 26, 1054, 1054], outline=NAVY, width=4)
    d.rectangle([40, 40, 1040, 1040], outline=GOLD, width=2)
    for cx, cy in ((26, 26), (1054, 26), (26, 1054), (1054, 1054)):
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD, outline=NAVY, width=2)

    # university seal
    draw_seal(img, 540, 128, 72)
    d = ImageDraw.Draw(img, "RGBA")

    # headings
    text_center(d, 540, 208, "LEONIDA UNIVERSITY", font(SERIF, 40), NAVY, spacing=8)
    text_center(d, 540, 258, "CERTIFICATE OF GRADUATION", font(SERIF, 52), NAVY,
                spacing=2)
    d.line([(240, 330), (505, 330)], fill=GOLD, width=2)
    d.line([(575, 330), (840, 330)], fill=GOLD, width=2)
    diamond(d, 540, 330, 8, MAGENTA)

    # body
    f_it = font(SERIF_IT, 27)
    text_center(d, 540, 356, "This is to certify that, after thirteen years of waiting,",
                f_it, INK)
    text_center(d, 540, 396, "the degree of", font(SERIF_IT, 24), INK)
    text_center(d, 540, 428, "BACHELOR OF WAITING", font(ANTON, 64), NAVY, spacing=2)
    d.line([(290, 500), (790, 500)], fill=MAGENTA, width=4)
    text_center(d, 540, 514, "in GTA VI Studies", font(SERIF_IT, 30), INK)
    text_center(d, 540, 556, "is hereby conferred upon", font(SERIF_IT, 26), INK)
    text_center(d, 540, 590, "THE FANS (AGED 13 YRS)", font(ANTON, 50), NAVY, spacing=1)

    # details grid (2 x 2) with dotted leader lines
    f_lab = font(MONO, 17)
    f_val = font(SERIF, 24)
    f_val_it = font(SERIF_IT, 22)
    grid = [((150, 668), "FIELD OF STUDY", "Waiting for GTA VI", f_val),
            ((590, 668), "DURATION OF STUDY", "13 years", f_val),
            ((150, 748), "CLASS OF", "2026", f_val),
            ((590, 748), "THESIS", "“My kid starts school first”", f_val_it)]
    for (gx, gy), lab, val, vf in grid:
        d.text((gx, gy), lab, font=f_lab, fill=(110, 100, 80))
        d.text((gx, gy + 26), val, font=vf, fill=INK)
        vw = d.textlength(val, font=vf)
        for xx in range(gx, int(gx + vw), 8):
            d.point((xx, gy + 54), fill=(140, 125, 90))
            d.point((xx + 1, gy + 54), fill=(140, 125, 90))

    # signatures
    f_sig = font(SERIF_IT, 34)
    f_tit = font(MONO, 17)
    for cx, name, title in ((290, "Rockstar Games", "DEAN"),
                            (790, "G. Host", "REGISTRAR")):
        text_center(d, cx, 836, name, f_sig, NAVY)
        d.line([(cx - 130, 878), (cx + 130, 878)], fill=NAVY, width=2)
        text_center(d, cx, 888, title, f_tit, (110, 100, 80))

    # round stamp + ribbon, centre-bottom
    draw_stamp(img, 540, 930, 76)
    d = ImageDraw.Draw(img, "RGBA")

    # ghost mark, bottom-left corner
    ghost = Image.open(f"{ASSETS}/mark-1024.png").convert("RGBA")
    ghost.thumbnail((96, 96), Image.LANCZOS)
    img.paste(ghost, (66, 1036 - ghost.height - 8), ghost)

    img.save(OUT, optimize=True)
    print("saved", OUT)


if __name__ == "__main__":
    main()
