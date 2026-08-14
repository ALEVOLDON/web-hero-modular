# Web Hero — Modular Genesis

Live lab landing: Blender eurorack case → Draco GLB → Three.js + GSAP, driven by a generative Web Audio patch.

```
Blender  →  hero.glb  →  Three.js  →  GSAP + Web Audio
```

Not a baked video. Camera shots, cable current, and knob/fader motion are live.

```bat
cd web
start.bat
```

Open http://127.0.0.1:8765

Live: https://alevoldon.github.io/web-hero-modular/

## What you get

| Layer | Behavior |
|---|---|
| Signal | Built-in generative patch (or mic) drives glow, faders, LEDs, bloom, cable sparks |
| Cables | Thick hanging patch cords with metal tips and traveling current |
| Modules | CLK / VCO / VCF / ENV / LFO / S&H / MIX / VIS faceplates |
| Click | Hover a module → lesson + patch from the live Modular Genesis site |
| Camera | Overview / Knobs / Cables / Into — GSAP shots, idle cycle, CTA hover |
| Production | Loader, mobile poster, favicon, Open Graph, Draco GLB, GitHub Pages-ready |

## Files

| Path | Role |
|---|---|
| `web/index.html` | Landing |
| `web/main.js` | Three + GSAP + picking + shots |
| `web/audio.js` | Generative patch + analyser |
| `web/modules.js` | Lesson / patch URLs |
| `web/hero.glb` | Draco-compressed case |
| `web/cables.json` | Cable paths for current |
| `web/cover.jpg` | Mobile poster + OG image |
| `module_spec.py` | Shared eurorack layout |
| `gen_panels.py` | Faceplate textures |
| `create_hero.py` | Rebuild the blend (GPU) |
| `export_glb.py` | Export + Draco |

## Rebuild

```bat
python gen_panels.py
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python create_hero.py
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python export_glb.py
```

Renders stay on the RTX GPU (OptiX). Do not pass `--anim` unless you want the optional 8s preview movie.

## GitHub Pages

`web/` is the site root (relative paths, `.nojekyll`, `404.html`). Publish that folder:

```bat
git subtree push --prefix web origin gh-pages
```

Or copy `web/` onto the `gh-pages` branch. After the first push, enable Pages on that branch.
