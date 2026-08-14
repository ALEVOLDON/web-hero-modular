"""Paint eurorack faceplates + mini-screens with PIL. Run from host Python."""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from module_spec import MODULES

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "textures")
os.makedirs(OUT, exist_ok=True)

W, H = 384, 768
FONT_DIR = r"C:\Windows\Fonts"


def font(name, size):
    for fn in (name, "consola.ttf", "consolab.ttf", "segoeui.ttf", "arial.ttf"):
        path = os.path.join(FONT_DIR, fn)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F_TITLE = font("consolab.ttf", 44)
F_SMALL = font("consola.ttf", 16)
F_MICRO = font("consola.ttf", 13)
F_HP = font("consola.ttf", 14)


def aluminum():
    img = Image.new("RGB", (W, H), (14, 16, 20))
    px = img.load()
    for y in range(H):
        for x in range(W):
            n = ((x * 13 + y * 7) ^ (x * y * 3)) & 15
            g = 12 + n
            # faint horizontal mill
            g += 4 if (y % 3 == 0) else 0
            px[x, y] = (g, g + 1, g + 3)
    return img


def ring(draw, cx, cy, r, fill, width=3):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)


def uv(u, v):
    return int(u * (W - 1)), int((1.0 - v) * (H - 1))


def paint_panel(spec):
    img = aluminum()
    d = ImageDraw.Draw(img, "RGBA")
    ac = tuple(int(c * 255) for c in spec["accent"])
    # top rail
    d.rectangle((0, 0, W, 10), fill=ac)
    d.rectangle((0, 10, W, 12), fill=(0, 0, 0, 180))
    # side ticks
    d.rectangle((0, 0, 3, H), fill=(*ac, 80))
    d.rectangle((W - 3, 0, W, H), fill=(0, 0, 0, 90))

    title = spec["title"]
    d.text((22, 28), title, font=F_TITLE, fill=ac)
    d.text((W - 78, 38), f"{spec['hp']}HP", font=F_HP, fill=(120, 132, 148))
    d.text((22, 78), "MODULAR GENESIS", font=F_MICRO, fill=(90, 104, 118))

    # screws
    for sx, sy in ((18, 18), (W - 18, 18), (18, H - 18), (W - 18, H - 18)):
        d.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), fill=(28, 30, 34), outline=(70, 74, 80))
        d.line((sx - 4, sy, sx + 4, sy), fill=(90, 94, 100), width=1)

    for label, u, v in spec.get("knobs", []):
        cx, cy = uv(u, v)
        r = 34
        d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(8, 9, 11))
        ring(d, cx, cy, r, (*ac, 200), 2)
        ring(d, cx, cy, r - 10, (40, 44, 50), 2)
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=ac)
        tw = d.textlength(label, font=F_SMALL)
        d.text((cx - tw / 2, cy + r + 8), label, font=F_SMALL, fill=(170, 180, 192))

    for i, (label, u, v) in enumerate(spec.get("jacks", [])):
        cx, cy = uv(u, v)
        r = 16
        d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(6, 7, 8))
        ring(d, cx, cy, r, (90, 96, 104), 3)
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(4, 4, 5))
        tw = d.textlength(label, font=F_MICRO)
        d.text((cx - tw / 2, cy + r + 6), label, font=F_MICRO, fill=(140, 150, 160))

    nled = spec.get("leds", 0)
    if nled:
        y = 118 if spec["id"] == "CLK" else 168
        gap = (W - 48) / max(1, nled)
        for i in range(nled):
            cx = 24 + gap * i + gap * 0.35
            col = ac if spec["id"] == "CLK" else (40, 80, 70)
            d.rounded_rectangle((cx, y, cx + 18, y + 10), 2, fill=(*col, 90), outline=(*ac, 160))

    if spec.get("faders"):
        n = spec["faders"]
        top, bot = 200, 560
        for i in range(n):
            x = int(W * (0.18 + i * 0.20))
            d.rectangle((x - 3, top, x + 3, bot), fill=(8, 8, 10), outline=(70, 76, 84))
            d.text((x - 4, bot + 8), str(i + 1), font=F_MICRO, fill=(140, 150, 160))

    if spec.get("screen"):
        if spec["id"] == "VIS":
            box = (36, 110, W - 36, 250)
        elif spec["id"] == "VCO":
            box = (40, 118, W - 40, 200)
        else:
            box = (28, 150, W - 28, 210)
        d.rounded_rectangle(box, 6, fill=(4, 8, 12), outline=(*ac, 180))

    img = img.filter(ImageFilter.SMOOTH)
    path = os.path.join(OUT, f"panel_{spec['id']}.png")
    img.save(path, "PNG")
    print("panel", path)
    return path


def paint_wave():
    img = Image.new("RGBA", (512, 220), (4, 10, 16, 255))
    d = ImageDraw.Draw(img)
    pts = []
    for x in range(512):
        t = x / 511
        y = 110 + 48 * math.sin(t * math.tau * 3.2) + 18 * math.sin(t * math.tau * 9)
        pts.append((x, y))
    d.line(pts, fill=(40, 200, 255, 255), width=2)
    img.save(os.path.join(OUT, "screen_wave.png"), "PNG")


def paint_steps():
    img = Image.new("RGBA", (512, 160), (4, 10, 16, 255))
    d = ImageDraw.Draw(img)
    for i in range(8):
        x = 18 + i * 62
        h = 30 + (i * 17 + 11) % 90
        fill = (40, 230, 180, 220) if i == 2 else (20, 80, 70, 180)
        d.rounded_rectangle((x, 140 - h, x + 46, 140), 3, fill=fill)
    img.save(os.path.join(OUT, "screen_steps.png"), "PNG")


def paint_spec():
    img = Image.new("RGBA", (512, 256), (4, 10, 16, 255))
    d = ImageDraw.Draw(img)
    for i in range(36):
        x = 8 + i * 14
        h = 20 + int(180 * abs(math.sin(i * 0.33)) * (0.4 + 0.6 * math.sin(i * 0.11)))
        d.rectangle((x, 240 - h, x + 10, 240), fill=(30, 190, 255, 210))
    img.save(os.path.join(OUT, "screen_spec.png"), "PNG")


if __name__ == "__main__":
    for spec in MODULES:
        paint_panel(spec)
    paint_wave()
    paint_steps()
    paint_spec()
    print("OK", OUT)
