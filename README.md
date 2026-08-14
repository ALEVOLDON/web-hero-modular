# Modular Genesis — 3D Eurorack Hero & Interactive Audio Lab

[![Three.js](https://img.shields.io/badge/Three.js-r160-black?style=flat&logo=three.js)](https://threejs.org/)
[![Blender](https://img.shields.io/badge/Blender-5.2_LTS-E87D0D?style=flat&logo=blender)](https://www.blender.org/)
[![Web Audio API](https://img.shields.io/badge/Web_Audio-Realtime_DSP-22d3ee?style=flat)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An interactive, real-time 3D Eurorack Synthesizer hero experience and interactive sound synthesis laboratory for the **[Modular Genesis](https://alevoldon.github.io/Modular-Genesis/)** open educational portal.

Built with **Three.js**, **GSAP**, **Web Audio API**, and a procedural **Blender 5.2 (Draco)** 3D asset generation pipeline.

---

## 🌟 Key Features

### 1. High-Precision 3D Eurorack Skiff
- **True-to-Scale 68HP Eurorack Case:** Solid matte black anodized aluminum skiff with dark walnut side cheeks (`CheekWood`), silver mounting rails, and recessed screws.
- **Synchronized Controls:** Knobs with tactile knurled bodies and white pointer indicators that rotate synchronously in response to audio modulation and user interaction.
- **Natural Catenary Patch Cables:** Smooth rubberized cables with metal plug sleeves, gravitational sag, and animated traveling electrical voltage pulses.
- **Real-Time Dynamic OLED Screens:**
  - `VCO Screen`: Live oscilloscope tracing waveform morphing in real time.
  - `VIS Screen`: 24-band FFT spectrum analyzer and audio visualizer.
  - `CLK Screen`: 8-step chase sequencer matrix.

### 2. Interactive Learning Mode (Learn & Inspect)
- **Explore Mode:** Full tactile 3D mouse/touch parallax showing depth, reflections, and metallic highlights.
- **Learn Mode:** Hovering over any module highlights its perimeter with an emissive glow and displays a detailed HUD Inspector Card with module role, description, and direct links to the official lesson and downloadable patch.
- **Module Zoom (Focus):** Clicking any module smoothly glides the camera into macro view with an intuitive "← Overview" button to return.
- **Cinematic Shot Presets:**
  - `Overview` — Balanced 3/4 perspective shot of the entire rack.
  - `Controls` — Macro focus on oscillators, ladder filter, and envelopes.
  - `Patch Bay` — Dynamic low angle emphasizing patch cord routing.
  - `Macro / Into` — Front-panel macro close-up.

### 3. Real-Time Web Audio Engine
- **Generative Patch Mode:** Built-in dual-oscillator subtractive synthesis engine with resonant filter modulation, LFO drift, and pentatonic step sequencer.
- **Microphone Reactive Mode:** Live audio input analysis via Web Audio AnalyserNode.
- **Mute Mode:** Silent generative visualization.

### 4. Full Mobile Responsiveness & Touch Support
- **Adaptive Camera FOV:** Dynamically recalculates vertical field of view to ensure the entire rack fits comfortably on portrait smartphone screens without horizontal cutoffs.
- **Touch Parallax:** Single-finger swipe to rotate the rack in 3D with spring inertia; tap to inspect modules.
- **Bottom Sheet Drawer:** HUD Inspector smoothly slides up as a bottom sheet drawer on mobile devices.

### 5. Multilingual Localization (EN / RU)
- Instant on-the-fly language switching between English and Russian without page reloads.

---

## 🎛 Rack Architecture & Module Specification

| Module | Name | HP | Role | Description |
|---|---|---|---|---|
| **CLK** | Master Clock & Divider | 10HP | Rhythmic Spine | High-precision tempo pulses, Euclidean divisions, step sequence triggers. |
| **VCO** | Dual Morphing Oscillator | 8HP | Sound Generator | Saw/Triangle/Square/PWM morphing analog core with 1V/Oct tracking. |
| **FLT** | Resonant Filter (VCF) | 8HP | Timbral Sculptor | 24dB/oct ladder filter topology with analog drive and self-oscillation. |
| **ENV** | Dual ADSR Envelope | 8HP | Dynamic Modulator | Exponential 4-stage amplitude and filter contour generator. |
| **LFO** | Multi-Wave LFO | 6HP | Cyclic Evolution | Slow modulation waves (Triangle/Square) for pitch, cutoff, and PWM drift. |
| **RND** | Sample & Hold / Random | 8HP | Generative Chaos | Analog noise, quantized stepped random voltages, and slew portamento. |
| **MIX** | 4-Channel Summing Mixer | 8HP | Audio Summing | Low-noise DC-coupled summing mixer with linear channel faders. |
| **VIS** | Audiovisual Bridge & Scope | 10HP | Signal Analysis | Dual-channel oscilloscope, FFT spectrum analyzer, and CV visual mapper. |

---

## 📂 Project Structure

```
web-hero-modular/
├── web/                      # Production-ready web application root
│   ├── index.html            # Main HTML5 landing layout & HUD templates
│   ├── main.js               # Three.js scene controller, raycasting, camera GSAP
│   ├── audio.js              # Web Audio API synthesizer & FFT analyser
│   ├── modules.js            # Module specifications, educational metadata, URLs
│   ├── i18n.js               # EN / RU localization dictionary & switcher
│   ├── style.css             # Vanilla CSS design system & responsive layout
│   ├── hero.glb              # Draco-compressed 3D Eurorack asset (~800 KB)
│   └── cables.json           # Spline curve definitions for signal pulse particles
├── module_spec.py            # Master layout & cable routing definitions
├── gen_panels.py             # PIL-based high-resolution faceplate texture generator
├── create_hero.py            # Blender script for procedural 3D Eurorack assembly
├── export_glb.py             # Blender GLTF/GLB Draco exporter
├── hero_loop.blend           # Blender 5.2 master scene
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start & Development

### 1. Run Local Development Server
To launch the live web application locally:

```bash
# Using Python built-in server:
python -m http.server 8765 --directory "web"
```

Open **[http://localhost:8765/](http://localhost:8765/)** in your browser.

---

## 🛠 Rebuilding 3D Assets (Blender Pipeline)

If you modify module dimensions, faceplate textures, or cable routes, regenerate the 3D assets:

```bash
# 1. Regenerate faceplate and screen textures
python gen_panels.py

# 2. Rebuild the Blender master scene (.blend)
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python create_hero.py

# 3. Export Draco-compressed GLB asset to web/hero.glb
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python export_glb.py
```

---

## 🌐 Deployment to GitHub Pages

The `web/` directory is structured as a self-contained static web application.

```bash
# Deploy web/ subfolder to gh-pages branch
git subtree push --prefix web origin gh-pages
```

Live Demo: **[https://alevoldon.github.io/web-hero-modular/](https://alevoldon.github.io/web-hero-modular/)**

---

## 📄 License
MIT © [Modular Genesis](https://github.com/ALEVOLDON/Modular-Genesis)
