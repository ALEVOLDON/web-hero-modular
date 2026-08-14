"""
Paint eurorack faceplates + mini-screens with PIL with exact HP dimensions and crisp graphics.
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from module_spec import MODULES

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "textures")
os.makedirs(OUT, exist_ok=True)

H = 1024
FONT_DIR = r"C:\Windows\Fonts"


def font(name, size):
    for fn in (name, "consola.ttf", "consolab.ttf", "segoeui.ttf", "arial.ttf"):
        path = os.path.join(FONT_DIR, fn)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F_TITLE = font("consolab.ttf", 46)
F_SUB = font("consola.ttf", 20)
F_SMALL = font("consola.ttf", 18)
F_MICRO = font("consola.ttf", 15)
F_HP = font("consola.ttf", 16)


def aluminum(w, h):
    img = Image.new("RGB", (w, h), (16, 18, 24))
    px = img.load()
    for y in range(h):
        for x in range(w):
            n = ((x * 17 + y * 11) ^ (x * y * 5)) & 15
            g = 14 + n
            if y % 3 == 0:
                g += 4
            px[x, y] = (g, g + 1, g + 3)
    return img


def ring(draw, cx, cy, r, fill, width=3):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)


def paint_panel(spec):
    # Width proportional to HP (8HP -> 320px for H=1024)
    w = int((spec["hp"] / 8.0) * 320)
    img = aluminum(w, H)
    d = ImageDraw.Draw(img, "RGBA")
    ac = tuple(int(c * 255) for c in spec["accent"])

    # Top and bottom color accent lines
    d.rectangle((0, 0, w, 8), fill=ac)
    d.rectangle((0, H - 8, w, H), fill=ac)

    # Side hairline borders
    d.rectangle((0, 0, 2, H), fill=(*ac, 90))
    d.rectangle((w - 2, 0, w, H), fill=(*ac, 90))

    # Header: Title & HP
    title = spec["title"]
    d.text((18, 24), title, font=F_TITLE, fill=ac)
    d.text((w - 56, 32), f"{spec['hp']}HP", font=F_HP, fill=(120, 136, 154))
    d.text((18, 76), "MODULAR GENESIS", font=F_MICRO, fill=(84, 98, 114))

    # Mounting screw indicators
    for sx, sy in ((16, 16), (w - 16, 16), (16, H - 16), (w - 16, H - 16)):
        d.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(26, 28, 34), outline=(60, 66, 74))
        d.line((sx - 5, sy, sx + 5, sy), fill=(80, 86, 96), width=2)

    def uv_to_px(u, v):
        x = int(u * (w - 1))
        y = int((1.0 - v) * (H - 1))
        return x, y

    # Knobs Silk-screen Graphics
    for label, u, v in spec.get("knobs", []):
        cx, cy = uv_to_px(u, v)
        r = 38
        d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(10, 12, 16))
        ring(d, cx, cy, r, (*ac, 180), 2)
        ring(d, cx, cy, r - 8, (45, 50, 60), 2)
        tw = d.textlength(label, font=F_SMALL)
        d.text((cx - tw / 2, cy + r + 8), label, font=F_SMALL, fill=(190, 200, 214))

    # Jacks Silk-screen Graphics
    for i, (label, u, v) in enumerate(spec.get("jacks", [])):
        cx, cy = uv_to_px(u, v)
        r = 20
        d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=(8, 10, 14))
        ring(d, cx, cy, r, (110, 120, 134), 3)
        tw = d.textlength(label, font=F_MICRO)
        d.text((cx - tw / 2, cy + r + 8), label, font=F_MICRO, fill=(160, 172, 186))

    # LEDs
    nled = spec.get("leds", 0)
    if nled:
        y = 124 if spec["id"] == "CLK" else 170
        gap = (w - 40) / max(1, nled)
        for i in range(nled):
            cx = 20 + gap * i + gap * 0.25
            col = ac if spec["id"] == "CLK" else (40, 80, 70)
            d.rounded_rectangle((cx, y, cx + 18, y + 10), 3, fill=(*col, 100), outline=(*ac, 180))

    # Faders
    if spec.get("faders"):
        n = spec["faders"]
        top, bot = int(H * 0.28), int(H * 0.76)
        for i in range(n):
            x = int(w * (0.18 + i * 0.21))
            d.rectangle((x - 4, top, x + 4, bot), fill=(10, 12, 16), outline=(75, 82, 94))
            d.text((x - 4, bot + 10), str(i + 1), font=F_MICRO, fill=(160, 170, 184))

    # Screen Bezel
    if spec.get("screen"):
        if spec["id"] == "VIS":
            box = (28, 120, w - 28, 270)
        elif spec["id"] == "VCO":
            box = (32, 128, w - 32, 220)
        else:
            box = (24, 160, w - 24, 230)
        d.rounded_rectangle(box, 6, fill=(6, 10, 16), outline=(*ac, 200))

    img = img.filter(ImageFilter.SMOOTH)
    path = os.path.join(OUT, f"panel_{spec['id']}.png")
    img.save(path, "PNG")
    return path


def paint_screens():
    # 1. Waveform
    img1 = Image.new("RGBA", (512, 256), (4, 8, 14, 255))
    d1 = ImageDraw.Draw(img1)
    pts = []
    for x in range(512):
        t = x / 511
        y = 128 + 54 * math.sin(t * math.tau * 3.0) + 20 * math.sin(t * math.tau * 7)
        pts.append((x, y))
    d1.line(pts, fill=(40, 200, 255, 255), width=3)
    img1.save(os.path.join(OUT, "screen_wave.png"), "PNG")

    # 2. Steps
    img2 = Image.new("RGBA", (512, 180), (4, 8, 14, 255))
    d2 = ImageDraw.Draw(img2)
    for i in range(8):
        x = 18 + i * 62
        h = 35 + (i * 19 + 11) % 100
        fill = (40, 230, 180, 230) if i == 2 else (20, 80, 70, 180)
        d2.rounded_rectangle((x, 150 - h, x + 48, 150), 3, fill=fill)
    img2.save(os.path.join(OUT, "screen_steps.png"), "PNG")

    # 3. Spectrum
    img3 = Image.new("RGBA", (512, 256), (4, 8, 14, 255))
    d3 = ImageDraw.Draw(img3)
    for i in range(24):
        x = 16 + i * 20
        h = int(30 + 180 * math.exp(-((i - 6) ** 2) / 30) + (i * 7) % 25)
        d3.rectangle((x, 230 - h, x + 15, 230), fill=(20, 180, 255, 220))
    img3.save(os.path.join(OUT, "screen_spec.png"), "PNG")


def main():
    for spec in MODULES:
        p = paint_panel(spec)
        print("Generated panel:", p)
    paint_screens()
    print("Generated all screen textures.")


if __name__ == "__main__":
    main()
