"""
Paint high-resolution eurorack faceplates + screens with PIL.
Features exact HP dimensions, radial dial ticks, vector-grade typography,
and realistic anodized aluminum texture.
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from module_spec import MODULES

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "textures")
os.makedirs(OUT, exist_ok=True)

H = 2048  # High-resolution 2048px height
FONT_DIR = r"C:\Windows\Fonts"


def font(name, size):
    candidates = (
        name,
        "segoeuib.ttf",
        "segoeui.ttf",
        "arialbd.ttf",
        "arial.ttf",
        "consola.ttf",
        "consolab.ttf",
    )
    for fn in candidates:
        path = os.path.join(FONT_DIR, fn)
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


F_TITLE = font("segoeuib.ttf", 68)
F_TITLE_COMPACT = font("segoeuib.ttf", 54)
F_MODEL = font("segoeui.ttf", 26)
F_HP = font("segoeuib.ttf", 28)
F_BRAND = font("segoeuib.ttf", 22)
F_KNOB_MAIN = font("segoeuib.ttf", 34)
F_KNOB_SUB = font("segoeui.ttf", 24)
F_JACK = font("segoeuib.ttf", 28)
F_TICK = font("segoeui.ttf", 20)
F_MICRO = font("segoeui.ttf", 22)


def aluminum_texture(w, h):
    """Anodized matte dark brushed aluminum texture with subtle vertical grain."""
    img = Image.new("RGBA", (w, h), (18, 20, 26, 255))
    px = img.load()
    for y in range(h):
        grain_y = (y % 4 == 0) * 3 + ((y * 7) % 11 == 0) * 2
        for x in range(w):
            noise = ((x * 19 + y * 23) ^ (x * y * 7)) & 7
            val = 18 + noise + grain_y
            px[x, y] = (val, val + 2, val + 5, 255)
    return img


def draw_dial_ticks(draw, cx, cy, r_inner, r_outer, num_ticks=9, accent=(255, 255, 255), angle_span=270):
    """Draw radial graduation tick marks spanning 270 degrees (-135 to +135 deg)."""
    start_angle = -135
    step = angle_span / (num_ticks - 1)
    
    # Arc trail under the ticks
    bbox = (cx - r_outer - 4, cy - r_outer - 4, cx + r_outer + 4, cy + r_outer + 4)
    draw.arc(bbox, start=start_angle - 90, end=start_angle + angle_span - 90, fill=(*accent[:3], 70), width=2)

    for i in range(num_ticks):
        deg = start_angle + i * step
        rad = math.radians(deg - 90)
        
        is_major = (i == 0 or i == num_ticks - 1 or i == (num_ticks - 1) // 2)
        r_in = r_inner - (4 if is_major else 0)
        r_out = r_outer + (4 if is_major else 0)
        
        x1 = cx + r_in * math.cos(rad)
        y1 = cy + r_in * math.sin(rad)
        x2 = cx + r_out * math.cos(rad)
        y2 = cy + r_out * math.sin(rad)
        
        col = (*accent[:3], 230) if is_major else (140, 150, 168, 180)
        w = 3 if is_major else 2
        draw.line([(x1, y1), (x2, y2)], fill=col, width=w)
        
        # Min / Max / Center dot markers
        if is_major:
            r_dot = r_out + 10
            dx = cx + r_dot * math.cos(rad)
            dy = cy + r_dot * math.sin(rad)
            draw.ellipse((dx - 3, dy - 3, dx + 3, dy + 3), fill=(*accent[:3], 240))


def draw_screw(draw, sx, sy):
    """Eurorack M3 hex socket cap screw graphic."""
    draw.ellipse((sx - 18, sy - 18, sx + 18, sy + 18), fill=(10, 12, 16), outline=(65, 72, 82), width=2)
    draw.ellipse((sx - 14, sy - 14, sx + 14, sy + 14), fill=(38, 42, 50), outline=(90, 98, 110), width=2)
    hex_pts = []
    for a in range(6):
        ang = math.radians(a * 60 + 30)
        hex_pts.append((sx + 7 * math.cos(ang), sy + 7 * math.sin(ang)))
    draw.polygon(hex_pts, fill=(12, 14, 18), outline=(60, 68, 78))


def paint_panel(spec):
    # 8HP -> 640px for H=2048 (exact 1:1 aspect ratio with Eurorack dimensions 128.5mm x 5.08mm*HP)
    w = int((spec["hp"] / 8.0) * 640)
    img = aluminum_texture(w, H)
    d = ImageDraw.Draw(img, "RGBA")
    ac = tuple(int(c * 255) for c in spec["accent"])

    # 1. Top and bottom rail accent borders
    d.rectangle((0, 0, w, 14), fill=ac)
    d.rectangle((0, H - 14, w, H), fill=ac)
    d.rectangle((0, 14, w, 18), fill=(*ac, 90))
    d.rectangle((0, H - 18, w, H - 14), fill=(*ac, 90))

    # 2. Side bevel hairline highlights
    d.line([(1, 0), (1, H)], fill=(*ac, 120), width=2)
    d.line([(w - 2, 0), (w - 2, H)], fill=(*ac, 120), width=2)

    # 3. Mounting Screws (positioned at top/bottom corners with exact padding)
    screw_margin_x = 34
    screw_margin_y = 48
    screws = [
        (screw_margin_x, screw_margin_y),
        (w - screw_margin_x, screw_margin_y),
        (screw_margin_x, H - screw_margin_y),
        (w - screw_margin_x, H - screw_margin_y),
    ]
    for sx, sy in screws:
        draw_screw(d, sx, sy)

    # 4. Header Section (Inset to guarantee ZERO overlap with screws)
    title = spec["title"]
    model = spec.get("model", f"MG-{spec['id']}")
    is_compact = (spec["hp"] <= 6)
    f_t = F_TITLE_COMPACT if is_compact else F_TITLE

    # Inset title safely away from top-left screw (sx = 34, r = 18 -> right edge of screw is 52px)
    title_x = 76 if not is_compact else (w // 2 - d.textlength(title, font=f_t) // 2)
    title_y = 38 if not is_compact else 32
    d.text((title_x, title_y), title, font=f_t, fill=ac)

    # HP Badge (Pill) - safely inset from top-right screw (w - 34, r = 18 -> left edge of screw is w - 52px)
    if not is_compact:
        hp_str = f"{spec['hp']}HP"
        hp_w = d.textlength(hp_str, font=F_HP)
        badge_x = w - hp_w - 76
        d.rounded_rectangle((badge_x - 8, 44, badge_x + hp_w + 8, 80), 6, fill=(28, 32, 42), outline=(*ac, 180), width=2)
        d.text((badge_x, 48), hp_str, font=F_HP, fill=(210, 220, 235))
    
    # Sub-header: Brand & Model
    sub_y = 118 if not is_compact else 96
    if not is_compact:
        d.text((76, sub_y), "MODULAR GENESIS", font=F_BRAND, fill=(110, 128, 148))
        model_w = d.textlength(model, font=F_MODEL)
        d.text((w - model_w - 76, sub_y), model, font=F_MODEL, fill=(130, 145, 165))
    else:
        bw = d.textlength(model, font=F_MODEL)
        d.text((w // 2 - bw // 2, sub_y), model, font=F_MODEL, fill=(130, 145, 165))

    # Divider line
    div_y = 156 if not is_compact else 134
    d.line([(24, div_y), (w - 24, div_y)], fill=(*ac, 80), width=2)

    def uv_to_px(u, v):
        x = int(u * (w - 1))
        y = int((1.0 - v) * (H - 1))
        return x, y

    # 5. OLED Screen Bezel & Silkscreen Framing
    if spec.get("screen"):
        s_info = spec["screen"]
        sx_mid, sy_mid = uv_to_px(s_info["u"], s_info["v"])
        sw_px = int(s_info["w"] * w)
        sh_px = int(s_info["h"] * H)
        box = (
            sx_mid - sw_px // 2 - 8,
            sy_mid - sh_px // 2 - 8,
            sx_mid + sw_px // 2 + 8,
            sy_mid + sh_px // 2 + 8,
        )
        d.rounded_rectangle(box, 14, fill=(10, 14, 20), outline=(*ac, 220), width=3)
        inner_box = (box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6)
        d.rounded_rectangle(inner_box, 10, fill=(6, 8, 14), outline=(45, 55, 70), width=2)
        
        lbl = "OLED OSCILLOSCOPE" if spec["id"] == "VCO" else ("STEP MATRIX" if spec["id"] == "CLK" else "FFT SPECTRUM & SCOPE")
        lw = d.textlength(lbl, font=F_MICRO)
        d.text((sx_mid - lw / 2, box[1] - 30), lbl, font=F_MICRO, fill=(140, 160, 185))

    # 6. Knobs & Potentiometer Silkscreen
    for k in spec.get("knobs", []):
        cx, cy = uv_to_px(k["u"], k["v"])
        is_large = (k.get("size") == "large")
        
        r_inner = 68 if is_large else 52
        r_outer = 84 if is_large else 66
        num_ticks = 13 if is_large else 9
        
        # Recessed socket
        d.ellipse((cx - r_inner - 6, cy - r_inner - 6, cx + r_inner + 6, cy + r_inner + 6), fill=(12, 14, 18), outline=(*ac, 140), width=2)
        d.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), fill=(8, 10, 14), outline=(40, 46, 56), width=2)
        
        # Radial Dial graduations
        draw_dial_ticks(d, cx, cy, r_inner + 6, r_outer, num_ticks, ac)
        
        # Main label
        lbl = k.get("label", k["key"])
        font_main = F_KNOB_MAIN
        lw = d.textlength(lbl, font=font_main)
        d.text((cx - lw / 2, cy + r_outer + 16), lbl, font=font_main, fill=(235, 242, 252))
        
        # Unit / Sub-label
        unit = k.get("unit", "")
        if unit:
            uw = d.textlength(unit, font=F_KNOB_SUB)
            d.text((cx - uw / 2, cy + r_outer + 56), unit, font=F_KNOB_SUB, fill=(*ac, 220))

    # 7. Jacks (Eurorack Standard)
    for j in spec.get("jacks", []):
        cx, cy = uv_to_px(j["u"], j["v"])
        r = 38
        is_out = (j.get("type") == "out")
        
        d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(10, 12, 16), outline=(*ac, 160) if is_out else (90, 100, 115), width=3)
        
        hex_pts = []
        for a in range(6):
            ang = math.radians(a * 60)
            hex_pts.append((cx + (r + 2) * math.cos(ang), cy + (r + 2) * math.sin(ang)))
        d.polygon(hex_pts, outline=(*ac, 140) if is_out else (75, 84, 96), fill=(14, 16, 22))
        
        d.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=(6, 7, 10), outline=(*ac, 220) if is_out else (120, 132, 148), width=2)
        
        if is_out:
            d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(*ac, 90))
        
        lbl = j["label"]
        lw = d.textlength(lbl, font=F_JACK)
        d.text((cx - lw / 2, cy - r - 42), lbl, font=F_JACK, fill=(245, 248, 255) if is_out else (180, 195, 212))

    # 8. LEDs & Step Indicators
    for li, led in enumerate(spec.get("leds", [])):
        cx, cy = uv_to_px(led["u"], led["v"])
        r = 16
        d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(18, 20, 26), outline=(80, 90, 105), width=2)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*ac, 160), outline=(*ac, 240), width=2)
        if spec["id"] == "CLK":
            step_lbl = str(li + 1)
            sw = d.textlength(step_lbl, font=F_MICRO)
            d.text((cx - sw / 2, cy + r + 8), step_lbl, font=F_MICRO, fill=(160, 175, 195))

    # 9. Faders (MIX)
    if spec.get("faders"):
        for f in spec["faders"]:
            cx, _ = uv_to_px(f["u"], 0.5)
            _, top_y = uv_to_px(f["u"], f["v_top"])
            _, bot_y = uv_to_px(f["u"], f["v_bot"])
            
            d.rounded_rectangle((cx - 8, top_y, cx + 8, bot_y), 6, fill=(8, 10, 14), outline=(60, 68, 80), width=2)
            d.line([(cx, top_y + 8), (cx, bot_y - 8)], fill=(20, 24, 32), width=4)
            
            for step_i, db_label in enumerate(["+6", "0", "-6", "-12", "-inf"]):
                ty = top_y + step_i * (bot_y - top_y) / 4
                d.line([(cx - 24, ty), (cx - 12, ty)], fill=(120, 130, 145), width=2)
                d.line([(cx + 12, ty), (cx + 24, ty)], fill=(120, 130, 145), width=2)
                if cx < w * 0.3:
                    d.text((cx - 58, ty - 10), db_label, font=F_MICRO, fill=(110, 125, 140))
            
            ch_lbl = f["label"]
            d.rounded_rectangle((cx - 20, bot_y + 16, cx + 20, bot_y + 52), 6, fill=(24, 28, 36), outline=(*ac, 180), width=2)
            cw = d.textlength(ch_lbl, font=F_JACK)
            d.text((cx - cw / 2, bot_y + 20), ch_lbl, font=F_JACK, fill=ac)

    # 10. Module Custom Decorative Schematics
    if spec["id"] == "ENV":
        curve_box = (w // 2 - 90, int(H * 0.42), w // 2 + 90, int(H * 0.42) + 50)
        pts = [
            (curve_box[0], curve_box[3]),
            (curve_box[0] + 40, curve_box[1]),
            (curve_box[0] + 80, curve_box[1] + 25),
            (curve_box[0] + 130, curve_box[1] + 25),
            (curve_box[2], curve_box[3]),
        ]
        d.line(pts, fill=(*ac, 200), width=3)
        d.text((w // 2 - 40, int(H * 0.42) - 30), "ADSR CURVE", font=F_MICRO, fill=(130, 145, 165))
    
    elif spec["id"] == "FLT":
        d.text((w // 2 - 58, int(H * 0.42) - 30), "24dB / OCT", font=F_MICRO, fill=(*ac, 220))
        d.arc((w // 2 - 70, int(H * 0.42) - 10, w // 2 + 70, int(H * 0.42) + 70), start=180, end=330, fill=(*ac, 180), width=3)

    elif spec["id"] == "RND":
        cx, cy = uv_to_px(0.50, 0.46)
        d.rounded_rectangle((cx - 100, cy - 40, cx + 100, cy + 40), 8, fill=(12, 14, 20), outline=(*ac, 120), width=2)
        st_pts = [
            (cx - 85, cy + 20), (cx - 55, cy + 20),
            (cx - 55, cy - 15), (cx - 25, cy - 15),
            (cx - 25, cy + 10), (cx + 5, cy + 10),
            (cx + 5, cy - 25), (cx + 35, cy - 25),
            (cx + 35, cy + 5), (cx + 85, cy + 5)
        ]
        d.line(st_pts, fill=(*ac, 180), width=2)
        d.text((cx - 45, cy - 65), "SAMPLE & HOLD", font=F_MICRO, fill=(150, 165, 185))

    elif spec["id"] == "LFO":
        cx, cy = uv_to_px(0.50, 0.42)
        d.text((cx - 95, cy - 10), "/\\", font=F_KNOB_MAIN, fill=(*ac, 180))
        d.text((cx + 65, cy - 10), "[]", font=F_KNOB_MAIN, fill=(*ac, 180))

    elif spec["id"] == "VCO":
        cx, cy = uv_to_px(0.72, 0.35)
        d.text((cx - 85, cy - 80), "~", font=F_TITLE, fill=(*ac, 160))
        d.text((cx + 60, cy - 70), "/|", font=F_KNOB_MAIN, fill=(*ac, 160))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    path = os.path.join(OUT, f"panel_{spec['id']}.png")
    img.save(path, "PNG", compress_level=6)
    return path


def paint_screens():
    """Paint crisp high-contrast OLED screen textures."""
    img1 = Image.new("RGBA", (1024, 512), (6, 10, 18, 255))
    d1 = ImageDraw.Draw(img1)
    for gx in range(0, 1024, 64):
        d1.line([(gx, 0), (gx, 512)], fill=(16, 28, 44, 255), width=1)
    for gy in range(0, 512, 64):
        d1.line([(0, gy), (1024, gy)], fill=(16, 28, 44, 255), width=1)
    d1.line([(0, 256), (1024, 256)], fill=(30, 55, 85, 255), width=2)
    d1.line([(512, 0), (512, 512)], fill=(30, 55, 85, 255), width=2)
    pts = []
    for x in range(1024):
        t = x / 1023
        y = 256 + 120 * math.sin(t * math.tau * 3.0) + 40 * math.sin(t * math.tau * 7.0)
        pts.append((x, y))
    d1.line(pts, fill=(255, 140, 30, 90), width=8)
    d1.line(pts, fill=(255, 190, 80, 255), width=4)
    f_scr = font("consola.ttf", 36)
    d1.text((32, 28), "VCO 1: MORPH SAW->SQR", font=f_scr, fill=(255, 170, 40, 230))
    d1.text((32, 440), "FREQ: 440.00 Hz   1V/OCT", font=f_scr, fill=(140, 180, 220, 200))
    img1.save(os.path.join(OUT, "screen_wave.png"), "PNG")

    img2 = Image.new("RGBA", (1024, 380), (6, 10, 18, 255))
    d2 = ImageDraw.Draw(img2)
    f_scr2 = font("consola.ttf", 32)
    d2.text((32, 24), "8-STEP CHASE SEQUENCER", font=f_scr2, fill=(40, 230, 180, 230))
    for i in range(8):
        x = 42 + i * 120
        h = 60 + (i * 37 + 23) % 180
        is_active = (i == 2)
        fill_col = (40, 240, 190, 255) if is_active else (20, 85, 75, 200)
        border_col = (100, 255, 220, 255) if is_active else (40, 130, 110, 220)
        d2.rounded_rectangle((x, 320 - h, x + 96, 320), 8, fill=fill_col, outline=border_col, width=3)
        d2.text((x + 36, 332), str(i + 1), font=f_scr2, fill=(180, 220, 210) if is_active else (80, 120, 110))
    img2.save(os.path.join(OUT, "screen_steps.png"), "PNG")

    img3 = Image.new("RGBA", (1024, 512), (6, 10, 18, 255))
    d3 = ImageDraw.Draw(img3)
    for gy in range(0, 512, 64):
        d3.line([(0, gy), (1024, gy)], fill=(16, 32, 50, 255), width=1)
    f_scr3 = font("consola.ttf", 36)
    d3.text((32, 24), "24-BAND FFT SPECTRUM ANALYZER", font=f_scr3, fill=(40, 210, 255, 240))
    for i in range(24):
        x = 36 + i * 40
        h = int(50 + 320 * math.exp(-((i - 7) ** 2) / 36) + (i * 13) % 45)
        d3.rounded_rectangle((x, 440 - h, x + 30, 440), 4, fill=(20, 185, 255, 220), outline=(90, 230, 255, 255), width=2)
        d3.rectangle((x, 440 - h - 12, x + 30, 440 - h - 8), fill=(255, 240, 120, 255))
    d3.text((32, 460), "L: -12.4 dB   R: -14.1 dB   THD: 0.02%", font=font("consola.ttf", 28), fill=(120, 170, 210))
    img3.save(os.path.join(OUT, "screen_spec.png"), "PNG")


def main():
    print("Generating high-resolution Eurorack panel textures...")
    for spec in MODULES:
        p = paint_panel(spec)
        print("Generated:", p)
    paint_screens()
    print("Successfully generated all panel and screen textures.")


if __name__ == "__main__":
    main()
