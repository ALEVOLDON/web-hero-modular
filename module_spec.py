"""Shared eurorack layout for panel textures and the Blender build."""

# u,v on the faceplate: 0..1
# u: left (0.0) -> right (1.0)
# v: bottom (0.0, jacks) -> top (1.0, title/header)

MODULES = [
    {
        "id": "CLK",
        "title": "CLK",
        "model": "MG-CLK-10",
        "hp": 10,
        "accent": (0.20, 0.92, 0.72),
        "screen": {"kind": "steps", "u": 0.50, "v": 0.74, "w": 0.74, "h": 0.18},
        "knobs": [
            {"key": "RATE", "label": "TEMPO", "u": 0.30, "v": 0.44, "size": "med", "unit": "BPM"},
            {"key": "DIV", "label": "DIV", "u": 0.70, "v": 0.44, "size": "med", "unit": "/N"},
        ],
        "jacks": [
            {"label": "CLK", "u": 0.18, "v": 0.14, "type": "out"},
            {"label": "RST", "u": 0.40, "v": 0.14, "type": "in"},
            {"label": "TR", "u": 0.62, "v": 0.14, "type": "out"},
            {"label": "GT", "u": 0.84, "v": 0.14, "type": "out"},
        ],
        "leds": [
            {"u": 0.15 + i * (0.70 / 7), "v": 0.88} for i in range(8)
        ],
    },
    {
        "id": "VCO",
        "title": "VCO",
        "model": "MG-VCO-08",
        "hp": 8,
        "accent": (1.00, 0.48, 0.10),
        "screen": {"kind": "wave", "u": 0.50, "v": 0.80, "w": 0.72, "h": 0.13},
        "knobs": [
            {"key": "FREQ", "label": "FREQ", "u": 0.50, "v": 0.57, "size": "large", "unit": "Hz"},
            {"key": "FINE", "label": "FINE", "u": 0.28, "v": 0.35, "size": "med", "unit": "ct"},
            {"key": "SHP", "label": "SHAPE", "u": 0.72, "v": 0.35, "size": "med", "unit": "morph"},
        ],
        "jacks": [
            {"label": "1V/OCT", "u": 0.22, "v": 0.14, "type": "in"},
            {"label": "PWM", "u": 0.50, "v": 0.14, "type": "in"},
            {"label": "OUT", "u": 0.78, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "FLT",
        "title": "VCF",
        "model": "MG-VCF-08",
        "hp": 8,
        "accent": (0.25, 0.72, 1.00),
        "knobs": [
            {"key": "CUT", "label": "CUTOFF", "u": 0.50, "v": 0.70, "size": "large", "unit": "kHz"},
            {"key": "RES", "label": "RES", "u": 0.28, "v": 0.42, "size": "med", "unit": "Q"},
            {"key": "DRV", "label": "DRIVE", "u": 0.72, "v": 0.42, "size": "med", "unit": "sat"},
        ],
        "jacks": [
            {"label": "IN", "u": 0.22, "v": 0.14, "type": "in"},
            {"label": "FM", "u": 0.50, "v": 0.14, "type": "in"},
            {"label": "OUT", "u": 0.78, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "ENV",
        "title": "ENV",
        "model": "MG-ENV-08",
        "hp": 8,
        "accent": (0.95, 0.22, 0.55),
        "knobs": [
            {"key": "A", "label": "ATTACK", "u": 0.28, "v": 0.72, "size": "med", "unit": "ms"},
            {"key": "D", "label": "DECAY", "u": 0.72, "v": 0.72, "size": "med", "unit": "ms"},
            {"key": "S", "label": "SUSTAIN", "u": 0.28, "v": 0.44, "size": "med", "unit": "%"},
            {"key": "R", "label": "RELEASE", "u": 0.72, "v": 0.44, "size": "med", "unit": "ms"},
        ],
        "jacks": [
            {"label": "GATE", "u": 0.30, "v": 0.14, "type": "in"},
            {"label": "OUT", "u": 0.70, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "LFO",
        "title": "LFO",
        "model": "MG-LFO-06",
        "hp": 6,
        "accent": (0.75, 0.35, 1.00),
        "knobs": [
            {"key": "RATE", "label": "RATE", "u": 0.50, "v": 0.68, "size": "med", "unit": "Hz"},
            {"key": "SHP", "label": "SHAPE", "u": 0.50, "v": 0.42, "size": "med", "unit": "wave"},
        ],
        "leds": [
            {"u": 0.50, "v": 0.86}
        ],
        "jacks": [
            {"label": "TRI", "u": 0.30, "v": 0.14, "type": "out"},
            {"label": "SQR", "u": 0.70, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "RND",
        "title": "S&H",
        "model": "MG-RND-08",
        "hp": 8,
        "accent": (0.95, 0.85, 0.15),
        "knobs": [
            {"key": "RATE", "label": "RATE", "u": 0.28, "v": 0.68, "size": "med", "unit": "Hz"},
            {"key": "SPR", "label": "SPREAD", "u": 0.72, "v": 0.68, "size": "med", "unit": "slew"},
        ],
        "leds": [
            {"u": 0.50, "v": 0.46}
        ],
        "jacks": [
            {"label": "CLK", "u": 0.22, "v": 0.14, "type": "in"},
            {"label": "IN", "u": 0.50, "v": 0.14, "type": "in"},
            {"label": "OUT", "u": 0.78, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "MIX",
        "title": "MIX",
        "model": "MG-MIX-08",
        "hp": 8,
        "accent": (0.35, 1.00, 0.45),
        "knobs": [
            {"key": "LVL", "label": "MASTER", "u": 0.50, "v": 0.80, "size": "large", "unit": "dB"},
        ],
        "faders": [
            {"label": "1", "u": 0.18, "v_top": 0.64, "v_bot": 0.30},
            {"label": "2", "u": 0.39, "v_top": 0.64, "v_bot": 0.30},
            {"label": "3", "u": 0.61, "v_top": 0.64, "v_bot": 0.30},
            {"label": "4", "u": 0.82, "v_top": 0.64, "v_bot": 0.30},
        ],
        "jacks": [
            {"label": "1", "u": 0.18, "v": 0.14, "type": "in"},
            {"label": "2", "u": 0.39, "v": 0.14, "type": "in"},
            {"label": "3", "u": 0.61, "v": 0.14, "type": "in"},
            {"label": "OUT", "u": 0.84, "v": 0.14, "type": "out"},
        ],
    },
    {
        "id": "VIS",
        "title": "VIS",
        "model": "MG-VIS-10",
        "hp": 10,
        "accent": (0.20, 0.85, 1.00),
        "screen": {"kind": "spec", "u": 0.50, "v": 0.68, "w": 0.78, "h": 0.32},
        "knobs": [
            {"key": "GAIN", "label": "GAIN", "u": 0.28, "v": 0.36, "size": "med", "unit": "x"},
            {"key": "SMOOTH", "label": "SMOOTH", "u": 0.72, "v": 0.36, "size": "med", "unit": "ms"},
        ],
        "jacks": [
            {"label": "IN L", "u": 0.30, "v": 0.14, "type": "in"},
            {"label": "IN R", "u": 0.70, "v": 0.14, "type": "in"},
        ],
    },
]

HP_TOTAL = sum(m["hp"] for m in MODULES)

# Front-bay patch routes: (src_mod, src_jack, dst_mod, dst_jack, sag, color_index, radius)
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
    (0.15, 0.75, 0.95),  # 0: Cyan
    (1.00, 0.45, 0.08),  # 1: Amber
    (0.85, 0.15, 0.55),  # 2: Magenta
    (0.20, 0.90, 0.45),  # 3: Neon Green
    (0.95, 0.85, 0.15),  # 4: Yellow
    (0.40, 0.35, 1.00),  # 5: Electric Purple
    (0.95, 0.25, 0.20),  # 6: Coral Red
    (0.10, 0.85, 0.80),  # 7: Teal
]
