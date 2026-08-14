"""Shared eurorack layout for panel textures and the Blender build."""

# u,v on the face: 0..1, u left→right, v front(jacks)→back(title)
MODULES = [
    {
        "id": "CLK",
        "title": "CLK",
        "hp": 10,
        "accent": (0.20, 0.92, 0.72),
        "knobs": [("RATE", 0.30, 0.70), ("DIV", 0.70, 0.70)],
        "jacks": [("CLK", 0.18, 0.16), ("RST", 0.40, 0.16), ("TR", 0.62, 0.16), ("GT", 0.84, 0.16)],
        "leds": 8,
        "screen": "steps",
    },
    {
        "id": "VCO",
        "title": "VCO",
        "hp": 8,
        "accent": (1.00, 0.48, 0.10),
        "knobs": [("FREQ", 0.50, 0.68), ("FINE", 0.26, 0.44), ("SHP", 0.74, 0.44)],
        "jacks": [("1V", 0.22, 0.16), ("PWM", 0.50, 0.16), ("OUT", 0.78, 0.16)],
        "screen": "wave",
    },
    {
        "id": "FLT",
        "title": "VCF",
        "hp": 8,
        "accent": (0.25, 0.72, 1.00),
        "knobs": [("CUT", 0.50, 0.70), ("RES", 0.26, 0.46), ("DRV", 0.74, 0.46)],
        "jacks": [("IN", 0.22, 0.16), ("FM", 0.50, 0.16), ("OUT", 0.78, 0.16)],
    },
    {
        "id": "ENV",
        "title": "ENV",
        "hp": 8,
        "accent": (0.95, 0.22, 0.55),
        "knobs": [("A", 0.20, 0.60), ("D", 0.40, 0.60), ("S", 0.60, 0.60), ("R", 0.80, 0.60)],
        "jacks": [("GT", 0.30, 0.16), ("OUT", 0.70, 0.16)],
    },
    {
        "id": "LFO",
        "title": "LFO",
        "hp": 6,
        "accent": (0.75, 0.35, 1.00),
        "knobs": [("RATE", 0.50, 0.66), ("SHP", 0.50, 0.40)],
        "jacks": [("TRI", 0.30, 0.16), ("SQR", 0.70, 0.16)],
        "leds": 1,
    },
    {
        "id": "RND",
        "title": "S&H",
        "hp": 8,
        "accent": (0.95, 0.85, 0.15),
        "knobs": [("RATE", 0.30, 0.60), ("SPR", 0.70, 0.60)],
        "jacks": [("CLK", 0.22, 0.16), ("IN", 0.50, 0.16), ("OUT", 0.78, 0.16)],
        "leds": 1,
    },
    {
        "id": "MIX",
        "title": "MIX",
        "hp": 8,
        "accent": (0.35, 1.00, 0.45),
        "knobs": [("LVL", 0.50, 0.78)],
        "faders": 4,
        "jacks": [("1", 0.16, 0.16), ("2", 0.39, 0.16), ("3", 0.61, 0.16), ("OUT", 0.84, 0.16)],
    },
    {
        "id": "VIS",
        "title": "VIS",
        "hp": 10,
        "accent": (0.20, 0.85, 1.00),
        "knobs": [("GAIN", 0.28, 0.40), ("SMOOTH", 0.72, 0.40)],
        "jacks": [("IN L", 0.30, 0.16), ("IN R", 0.70, 0.16)],
        "screen": "spec",
    },
]

HP_TOTAL = sum(m["hp"] for m in MODULES)

# Front-bay patch routes: (src_mod, src_jack, dst_mod, dst_jack, sag, color, radius)
ROUTES = [
    ("CLK", 0, "VCO", 0, 0.18, 0, 0.0062),
    ("CLK", 2, "ENV", 0, 0.13, 2, 0.0054),
    ("CLK", 1, "RND", 0, 0.22, 1, 0.0068),
    ("VCO", 2, "FLT", 0, 0.11, 3, 0.0072),
    ("ENV", 1, "FLT", 1, 0.16, 5, 0.0050),
    ("LFO", 0, "VCO", 1, 0.24, 6, 0.0058),
    ("RND", 2, "VCO", 0, 0.20, 7, 0.0060),
    ("FLT", 2, "MIX", 2, 0.15, 4, 0.0070),
    ("MIX", 3, "VIS", 0, 0.26, 0, 0.0076),
    ("LFO", 1, "VIS", 1, 0.19, 1, 0.0052),
    ("CLK", 3, "MIX", 0, 0.21, 2, 0.0048),
]

CABLE_COLORS = [
    (0.15, 0.75, 0.95),
    (1.00, 0.45, 0.08),
    (0.85, 0.15, 0.55),
    (0.20, 0.90, 0.45),
    (0.95, 0.85, 0.15),
    (0.40, 0.35, 1.00),
    (0.95, 0.25, 0.20),
    (0.10, 0.85, 0.80),
]
