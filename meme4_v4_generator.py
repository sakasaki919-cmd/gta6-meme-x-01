#!/usr/bin/env python3
"""Meme #4 (rebuild v4): BACHELOR'S DEGREE CERTIFICATE for waiting for GTA VI,
polished + FRAMED like a diploma hung on a wall.

Concept (ours, per user: "sertifikat sarjana"): Leonida University confers
the degree of Bachelor of Waiting in GTA VI Studies upon the fans.
Style: luxurious official certificate -- ornate triple frame, paper
texture, circular university seal, round rubber stamp + ribbon, signatures,
plus a small book+palm crest and a hand-squiggle Registrar signature.
The certificate is mounted in a classic dark-wood frame with thin gold
trim on a dark wall, with a soft drop shadow.
All art is procedural (PIL); the make.fun ghost mark is composited from
the press-kit asset in assets/mark-1024.png. 1080x1080, deterministic.
"""
import math
import random
from datetime import date

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

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
WALL = (43, 47, 63)
WOOD = (62, 40, 24)
WOOD_L = (84, 56, 34)
WOOD_D = (42, 24, 12)

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


def draw_emblem(img, cx, cy, r):
    """Small round crest: palm tree over an open book (Leonida vibes)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY + (255,), width=3)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              outline=GOLD + (255,), width=1)
    # palm: trunk + fronds
    px, py = cx, cy - 2
    d.line([(px, py + 16), (px + 2, py - 8)], fill=NAVY + (255,), width=3)
    for ang in (-70, -35, 0, 35, 70):
        a = math.radians(-90 + ang)
        x2 = px + 20 * math.cos(a)
        y2 = py - 8 + 20 * math.sin(a)
        d.line([(px, py - 8), (x2, y2)], fill=NAVY + (255,), width=2)
        d.line([(x2, y2), (x2 + 4 * math.cos(a + 0.5), y2 + 6)],
               fill=NAVY + (255,), width=2)
    # open book below the palm
    by = cy + 16
    d.polygon([(cx - 18, by), (cx, by - 5), (cx, by + 6), (cx - 18, by + 11)],
              outline=NAVY + (255,), fill=(255, 252, 240, 255))
    d.polygon([(cx + 18, by), (cx, by - 5), (cx, by + 6), (cx + 18, by + 11)],
              outline=NAVY + (255,), fill=(255, 252, 240, 255))
    img.paste(layer, (0, 0), layer)


def draw_squiggle(d, cx, cy, w, fill):
    """Hand-drawn signature squiggle: wavy line + loop + flourish."""
    pts = []
    n = 100
    for i in range(n + 1):
        t = i / n
        x = cx - w / 2 + w * t
        y = cy + 6 * math.sin(t * 11.0) + 3 * math.sin(t * 27.0 + 1.0)
        pts.append((x, y))
    d.line(pts, fill=fill, width=3, joint="curve")
    lx = cx - w * 0.28
    d.arc([lx - 14, cy - 16, lx + 14, cy + 8], 0, 360, fill=fill, width=3)
    d.arc([cx - w / 2 + 10, cy + 2, cx + w / 2 - 6, cy + 26], 200, 340,
          fill=fill, width=2)


def draw_stamp(img, cx, cy, r, rot=-15, alpha=205):
    """Round magenta stamp + ribbon tails, rotated, faded ink."""
    side = 2 * r + 40
    layer = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cc = side // 2
    m = MAGENTA + (alpha,)
    d.ellipse([cc - r, cc - r, cc + r, cc + r], outline=m, width=4)
    d.ellipse([cc - r + 7, cc - r + 7, cc + r - 7, cc + r - 7], outline=m, width=2)
    f_arc = font(SANS, 13)
    arc_text(layer, cc, cc, r - 14, "LEONIDA UNIVERSITY", f_arc, m, -75, 75)
    arc_text(layer, cc, cc, r - 14, "PAID BY MY AI AGENT", f_arc, m,
             -75, 75, bottom=True)
    star(d, cc, cc - 14, 18, 8, m)
    f_y = font(ANTON, 22)
    text_center(d, cc, cc + 10, "2026", f_y, m)
    f_m = font(MONO, 13)
    text_center(d, cc, cc + 34, "MAKE.FUN", f_m, m)
    # ribbon tails below the seal (shortened so they stay inside the border)
    d.polygon([(cc - 26, cc + r - 4), (cc - 14, cc + r - 4), (cc - 20, cc + r + 12),
               (cc - 26, cc + r + 6), (cc - 32, cc + r + 12)], fill=m)
    d.polygon([(cc + 14, cc + r - 4), (cc + 26, cc + r - 4), (cc + 32, cc + r + 12),
               (cc + 26, cc + r + 6), (cc + 20, cc + r + 12)], fill=m)
    layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (cx - layer.width // 2, cy - layer.height // 2), layer)


def diamond(draw, cx, cy, s, fill):
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=fill)


def render_certificate():
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

    # ornate triple frame + corner squares
    d.rectangle([26, 26, 1054, 1054], outline=NAVY, width=4)
    d.rectangle([40, 40, 1040, 1040], outline=GOLD, width=2)
    d.rectangle([48, 48, 1032, 1032], outline=NAVY, width=1)
    for cx, cy in ((26, 26), (1054, 26), (26, 1054), (1054, 1054)):
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD, outline=NAVY, width=2)

    # university seal
    draw_seal(img, 540, 128, 72)
    d = ImageDraw.Draw(img, "RGBA")

    # small book+palm crest, top-left empty area
    draw_emblem(img, 185, 140, 42)
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

    # details grid (2 x 2) with dotted leader lines -- bigger fonts, more air
    f_lab = font(MONO, 20)
    f_val = font(SERIF, 28)
    f_val_it = font(SERIF_IT, 25)
    lab_fill = (90, 80, 60)
    grid = [((150, 655), "FIELD OF STUDY", "Waiting for GTA VI", f_val),
            ((590, 655), "DURATION OF STUDY", "13 years", f_val),
            ((150, 740), "CLASS OF", "2026", f_val),
            ((590, 740), "THESIS", "“My kid starts school first”", f_val_it)]
    for (gx, gy), lab, val, vf in grid:
        d.text((gx, gy), lab, font=f_lab, fill=lab_fill)
        d.text((gx, gy + 30), val, font=vf, fill=INK)
        vw = d.textlength(val, font=vf)
        for xx in range(gx, int(gx + vw), 8):
            d.point((xx, gy + 62), fill=(140, 125, 90))
            d.point((xx + 1, gy + 62), fill=(140, 125, 90))

    # signatures
    f_sig = font(SERIF_IT, 36)
    f_tit = font(MONO, 18)
    # Dean: italic signature as before, slightly bigger
    text_center(d, 290, 842, "Rockstar Games", f_sig, NAVY)
    d.line([(160, 886), (420, 886)], fill=NAVY, width=2)
    text_center(d, 290, 896, "DEAN", f_tit, lab_fill)
    # Registrar: hand squiggle (the real signature) + typed name below it
    draw_squiggle(d, 790, 828, 180, NAVY)
    text_center(d, 790, 852, "G. Host", font(SERIF_IT, 26), NAVY)
    d.line([(660, 886), (920, 886)], fill=NAVY, width=2)
    text_center(d, 790, 896, "REGISTRAR", f_tit, lab_fill)

    # round stamp + ribbon, bottom-right empty area, faded ink, -15 deg
    draw_stamp(img, 910, 955, 60, rot=-15, alpha=205)
    d = ImageDraw.Draw(img, "RGBA")

    # ghost mark, bottom-left corner
    ghost = Image.open(f"{ASSETS}/mark-1024.png").convert("RGBA")
    ghost.thumbnail((96, 96), Image.LANCZOS)
    img.paste(ghost, (66, 1036 - ghost.height - 8), ghost)

    return img


def draw_frame(cert):
    """Mount the certificate in a classic dark-wood frame on a dark wall."""
    img = Image.new("RGB", (W, H), WALL)
    # soft drop shadow behind the frame
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([18, 22, 1078, 1080], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # wood band
    d.rectangle([10, 10, 1070, 1070], fill=WOOD)
    rng = random.Random(7)
    for _ in range(170):
        band = rng.randrange(4)
        if band == 0:  # top, horizontal grain
            x = rng.randint(14, 1000)
            y = rng.randint(13, 55)
            ln = rng.randint(30, 120)
            d.line([(x, y), (x + ln, y)], fill=rng.choice(
                [WOOD_L + (70,), WOOD_D + (70,)]), width=rng.choice([1, 1, 2]))
        elif band == 2:  # bottom, horizontal grain
            x = rng.randint(14, 1000)
            y = rng.randint(1025, 1067)
            ln = rng.randint(30, 120)
            d.line([(x, y), (x + ln, y)], fill=rng.choice(
                [WOOD_L + (70,), WOOD_D + (70,)]), width=rng.choice([1, 1, 2]))
        elif band == 3:  # left, vertical grain
            x = rng.randint(13, 55)
            y = rng.randint(14, 1000)
            ln = rng.randint(30, 120)
            d.line([(x, y), (x, y + ln)], fill=rng.choice(
                [WOOD_L + (70,), WOOD_D + (70,)]), width=rng.choice([1, 1, 2]))
        else:  # right, vertical grain
            x = rng.randint(1025, 1067)
            y = rng.randint(14, 1000)
            ln = rng.randint(30, 120)
            d.line([(x, y), (x, y + ln)], fill=rng.choice(
                [WOOD_L + (70,), WOOD_D + (70,)]), width=rng.choice([1, 1, 2]))
    # bevel + gold trims
    d.rectangle([10, 10, 1070, 1070], outline=(28, 16, 8), width=2)
    d.rectangle([15, 15, 1065, 1065], outline=GOLD, width=2)
    d.rectangle([53, 53, 1027, 1027], outline=GOLD, width=2)
    # mount the certificate inside the frame
    small = cert.resize((964, 964), Image.LANCZOS)
    img.paste(small, (58, 58))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([58, 58, 1022, 1022], outline=(0, 0, 0, 70), width=2)
    return img


def main():
    cert = render_certificate()
    img = draw_frame(cert)
    img.save(OUT, optimize=True)
    print("saved", OUT)


if __name__ == "__main__":
    main()
