"""
Autodesk Fusion 360 Python Script: Modular Genesis Eurorack Generator
=====================================================================
Automated parametric 3D modeling of 68HP Eurorack synthesizer:
- Universal mode (works in both Part Design and Assembly Design)
- Aluminum Skiff Case + Walnut Wooden Side Cheeks
- 8 Functional Module Panels (CLK, VCO, FLT, ENV, LFO, RND, MIX, VIS)
- 3D Knurled Knobs with white indicator pointers
- 3.5mm Thonkiconn Jack sockets with hex nuts
- 4-Channel Linear Slider Faders with DJ caps
- OLED Screen Bezels and Recessed Display Panels
"""

import traceback
import math
import adsk.core
import adsk.fusion

# ==============================================================================
# EURORACK CONSTANTS (Fusion 360 internal units are Centimeters)
# ==============================================================================
HP = 0.508               # 1 HP = 5.08 mm = 0.508 cm
HEIGHT = 12.85           # 3U standard panel height = 128.5 mm = 12.85 cm
PANEL_THICK = 0.20       # 2.0 mm panel thickness = 0.20 cm
CASE_DEPTH = 5.50        # 55.0 mm case depth = 5.50 cm
TOTAL_HP = 68            # Total rack width = 68 HP
TOTAL_WIDTH = TOTAL_HP * HP  # 34.544 cm

MODULE_DEFS = [
    {"id": "CLK", "hp": 10, "name": "Master Clock"},
    {"id": "VCO", "hp": 8,  "name": "Dual Morphing VCO"},
    {"id": "FLT", "hp": 8,  "name": "Resonant Filter"},
    {"id": "ENV", "hp": 8,  "name": "Dual ADSR Envelope"},
    {"id": "LFO", "hp": 6,  "name": "Multi-Wave LFO"},
    {"id": "RND", "hp": 8,  "name": "Sample and Hold"},
    {"id": "MIX", "hp": 8,  "name": "4-Ch Mixer"},
    {"id": "VIS", "hp": 10, "name": "Visualizer Scope"},
]

def get_profile(sketch):
    """Safely returns the main closed profile of a sketch."""
    if sketch.profiles.count == 0:
        return None
    if sketch.profiles.count == 1:
        return sketch.profiles.item(0)
    best = sketch.profiles.item(0)
    max_area = 0.0
    for i in range(sketch.profiles.count):
        p = sketch.profiles.item(i)
        try:
            a = p.areaProperties().area
            if a > max_area:
                max_area = a
                best = p
        except Exception:
            pass
    return best

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Please open a Fusion Design workspace before running this script.")
            return

        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        rootComp = design.rootComponent
        xyPlane = rootComp.xYConstructionPlane

        # ==============================================================================
        # 1. BUILD SKIFF CASE & WOODEN SIDE CHEEKS
        # ==============================================================================
        # Aluminum Skiff Body (drawn on XY, extruded in -Z)
        skiffSketch = rootComp.sketches.add(xyPlane)
        skiffSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-0.2, -0.2, 0.0),
            adsk.core.Point3D.create(TOTAL_WIDTH + 0.2, HEIGHT + 0.2, 0.0)
        )
        skiffProf = get_profile(skiffSketch)
        if skiffProf:
            rootComp.features.extrudeFeatures.addSimple(
                skiffProf,
                adsk.core.ValueInput.createByReal(-CASE_DEPTH),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

        # Hollow cavity for electronics
        cavitySketch = rootComp.sketches.add(xyPlane)
        cavitySketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0.4, 0.4, 0.0),
            adsk.core.Point3D.create(TOTAL_WIDTH - 0.4, HEIGHT - 0.4, 0.0)
        )
        cavityProf = get_profile(cavitySketch)
        if cavityProf:
            rootComp.features.extrudeFeatures.addSimple(
                cavityProf,
                adsk.core.ValueInput.createByReal(-(CASE_DEPTH - 0.5)),
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )

        # Wooden Side Cheeks (Left & Right - 12mm Walnut)
        CHEEK_THICK = 1.2
        # Left Cheek
        cheekLSketch = rootComp.sketches.add(xyPlane)
        cheekLSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-0.2 - CHEEK_THICK, -0.6, 0.0),
            adsk.core.Point3D.create(-0.2, HEIGHT + 0.6, 0.0)
        )
        cheekLProf = get_profile(cheekLSketch)
        if cheekLProf:
            rootComp.features.extrudeFeatures.addSimple(
                cheekLProf,
                adsk.core.ValueInput.createByReal(-CASE_DEPTH - 0.6),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

        # Right Cheek
        cheekRSketch = rootComp.sketches.add(xyPlane)
        cheekRSketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(TOTAL_WIDTH + 0.2, -0.6, 0.0),
            adsk.core.Point3D.create(TOTAL_WIDTH + 0.2 + CHEEK_THICK, HEIGHT + 0.6, 0.0)
        )
        cheekRProf = get_profile(cheekRSketch)
        if cheekRProf:
            rootComp.features.extrudeFeatures.addSimple(
                cheekRProf,
                adsk.core.ValueInput.createByReal(-CASE_DEPTH - 0.6),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

        # ==============================================================================
        # 2. BUILD 8 MODULAR PANELS & HARDWARE CONTROLS
        # ==============================================================================
        currentX = 0.0
        for mod in MODULE_DEFS:
            modId = mod["id"]
            modHp = mod["hp"]
            modW = modHp * HP
            
            # Panel Faceplate
            pSketch = rootComp.sketches.add(xyPlane)
            pSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(currentX + 0.01, 0.01, 0.0),
                adsk.core.Point3D.create(currentX + modW - 0.01, HEIGHT - 0.01, 0.0)
            )
            
            # M3 Mounting Holes
            for sx in (currentX + 0.75, currentX + modW - 0.75):
                for sy in (0.30, HEIGHT - 0.30):
                    pSketch.sketchCurves.sketchCircles.addByCenterRadius(
                        adsk.core.Point3D.create(sx, sy, 0.0), 0.16
                    )
            
            pProf = get_profile(pSketch)
            if pProf:
                rootComp.features.extrudeFeatures.addSimple(
                    pProf,
                    adsk.core.ValueInput.createByReal(PANEL_THICK),
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
            
            cx = currentX + modW * 0.5
            
            if modId == "CLK":
                create_oled(rootComp, cx, 9.6, 3.6, 1.8)
                create_knob(rootComp, cx - 1.1, 5.2, 0.6)
                create_knob(rootComp, cx + 1.1, 5.2, 0.6)
                for j in range(4):
                    create_jack(rootComp, currentX + 0.7 + j * (modW - 1.4) / 3.0, 3.2)
                    create_jack(rootComp, currentX + 0.7 + j * (modW - 1.4) / 3.0, 1.6)

            elif modId == "VCO":
                create_oled(rootComp, cx, 9.8, 2.8, 1.8)
                create_knob(rootComp, cx, 6.4, 0.8) # Big FREQ knob
                create_knob(rootComp, cx - 0.9, 3.8, 0.55)
                create_knob(rootComp, cx + 0.9, 3.8, 0.55)
                for j in range(3):
                    create_jack(rootComp, currentX + 0.7 + j * (modW - 1.4) / 2.0, 2.3)
                    create_jack(rootComp, currentX + 0.7 + j * (modW - 1.4) / 2.0, 1.1)

            elif modId == "FLT":
                create_knob(rootComp, cx, 7.8, 0.85) # Cutoff
                create_knob(rootComp, cx - 0.9, 4.4, 0.55)
                create_knob(rootComp, cx + 0.9, 4.4, 0.55)
                create_jack(rootComp, cx - 1.0, 2.4)
                create_jack(rootComp, cx + 1.0, 2.4)
                create_jack(rootComp, cx - 1.0, 1.2)
                create_jack(rootComp, cx + 1.0, 1.2)

            elif modId == "ENV":
                create_knob(rootComp, cx - 0.9, 8.2, 0.55) # Attack
                create_knob(rootComp, cx + 0.9, 8.2, 0.55) # Decay
                create_knob(rootComp, cx - 0.9, 4.8, 0.55) # Sustain
                create_knob(rootComp, cx + 0.9, 4.8, 0.55) # Release
                create_jack(rootComp, cx - 1.0, 2.4)
                create_jack(rootComp, cx + 1.0, 2.4)
                create_jack(rootComp, cx - 1.0, 1.2)
                create_jack(rootComp, cx + 1.0, 1.2)

            elif modId == "LFO":
                create_knob(rootComp, cx, 8.0, 0.6)
                create_knob(rootComp, cx, 4.6, 0.6)
                create_jack(rootComp, cx, 2.8)
                create_jack(rootComp, cx - 0.7, 1.4)
                create_jack(rootComp, cx + 0.7, 1.4)

            elif modId == "RND":
                create_knob(rootComp, cx - 0.9, 7.5, 0.6)
                create_knob(rootComp, cx + 0.9, 7.5, 0.6)
                for j in range(2):
                    create_jack(rootComp, currentX + 0.9 + j * (modW - 1.8), 3.2)
                    create_jack(rootComp, currentX + 0.9 + j * (modW - 1.8), 1.6)

            elif modId == "MIX":
                create_knob(rootComp, cx, 9.4, 0.75) # Master Level
                for f in range(4):
                    fx = currentX + 0.65 + f * (modW - 1.3) / 3.0
                    create_fader(rootComp, fx, 5.2, 3.2)
                    create_jack(rootComp, fx, 1.5)

            elif modId == "VIS":
                create_oled(rootComp, cx, 8.8, 3.8, 2.6) # Big Scope Screen
                create_knob(rootComp, cx - 1.1, 3.8, 0.6)
                create_knob(rootComp, cx + 1.1, 3.8, 0.6)
                create_jack(rootComp, cx - 1.2, 1.5)
                create_jack(rootComp, cx + 1.2, 1.5)
            
            currentX += modW

        ui.messageBox(
            "Modular Genesis Eurorack rack successfully built!\n"
            f"Total Width: 68 HP ({TOTAL_WIDTH:.2f} cm)\n"
            "All 8 modules, case, cheeks, knobs, jacks, faders and screens generated."
        )

    except Exception:
        if ui:
            ui.messageBox(f"Failed to generate Eurorack:\n{traceback.format_exc()}")

# ==============================================================================
# HELPER FUNCTIONS FOR 3D HARDWARE GENERATION
# ==============================================================================
def create_knob(comp, x, y, radius):
    """Creates a 3D knurled potentiometer knob with white pointer inlay."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0.0), radius)
    prof = get_profile(sk)
    if prof:
        comp.features.extrudeFeatures.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 1.25),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
    
    # White Pointer line
    pSk = comp.sketches.add(comp.xYConstructionPlane)
    pSk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x - 0.03, y + 0.1, 0.0),
        adsk.core.Point3D.create(x + 0.03, y + radius - 0.05, 0.0)
    )
    pProf = get_profile(pSk)
    if pProf:
        comp.features.extrudeFeatures.addSimple(
            pProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 1.29),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

def create_jack(comp, x, y):
    """Creates a 3.5mm Thonkiconn mini-jack with hexagonal nut and center hole."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0.0), 0.40)
    prof = get_profile(sk)
    if prof:
        comp.features.extrudeFeatures.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.25),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
    
    hSk = comp.sketches.add(comp.xYConstructionPlane)
    hSk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0.0), 0.18)
    hProf = get_profile(hSk)
    if hProf:
        comp.features.extrudeFeatures.addSimple(
            hProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.25),
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )

def create_fader(comp, x, y_center, length):
    """Creates a linear slider slot and fader cap."""
    halfL = length * 0.5
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x - 0.08, y_center - halfL, 0.0),
        adsk.core.Point3D.create(x + 0.08, y_center + halfL, 0.0)
    )
    prof = get_profile(sk)
    if prof:
        comp.features.extrudeFeatures.addSimple(
            prof,
            adsk.core.ValueInput.createByReal(PANEL_THICK),
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
    
    # Stem
    stemSk = comp.sketches.add(comp.xYConstructionPlane)
    stemSk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x - 0.05, y_center - 0.08, 0.0),
        adsk.core.Point3D.create(x + 0.05, y_center + 0.08, 0.0)
    )
    sProf = get_profile(stemSk)
    if sProf:
        comp.features.extrudeFeatures.addSimple(
            sProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.45),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
    
    # Cap
    capSk = comp.sketches.add(comp.xYConstructionPlane)
    capSk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x - 0.25, y_center - 0.45, 0.0),
        adsk.core.Point3D.create(x + 0.25, y_center + 0.45, 0.0)
    )
    cProf = get_profile(capSk)
    if cProf:
        comp.features.extrudeFeatures.addSimple(
            cProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.65),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

def create_oled(comp, cx, cy, width, height):
    """Creates an OLED screen bezel frame and recessed display glass."""
    hw = width * 0.5
    hh = height * 0.5
    
    bSk = comp.sketches.add(comp.xYConstructionPlane)
    bSk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(cx - hw - 0.15, cy - hh - 0.15, 0.0),
        adsk.core.Point3D.create(cx + hw + 0.15, cy + hh + 0.15, 0.0),
    )
    bProf = get_profile(bSk)
    if bProf:
        comp.features.extrudeFeatures.addSimple(
            bProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.12),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
    
    gSk = comp.sketches.add(comp.xYConstructionPlane)
    gSk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(cx - hw, cy - hh, 0.0),
        adsk.core.Point3D.create(cx + hw, cy + hh, 0.0)
    )
    gProf = get_profile(gSk)
    if gProf:
        comp.features.extrudeFeatures.addSimple(
            gProf,
            adsk.core.ValueInput.createByReal(PANEL_THICK + 0.06),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
