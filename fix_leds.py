"""Move LEDs to the front face of the module and export GLB."""
import bpy
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "hero_loop.blend")
OUT = os.path.join(ROOT, "web", "hero.glb")

if bpy.data.filepath.replace("/", "\\").lower() != BLEND.lower():
    bpy.ops.wm.open_mainfile(filepath=BLEND)

for i in range(16):
    o = bpy.data.objects.get(f"LED_{i}")
    if not o:
        print("missing", i)
        continue
    # local to CaseRoot: front of panel is -Y
    o.location = (-0.40 + i * 0.052, -0.205, 0.164)
    o.scale = (1.8, 1.6, 2.4)
    o.hide_set(False)
    o.hide_viewport = False
    o.hide_render = False
    print("moved", o.name, tuple(round(v, 3) for v in o.location))

hide_prefixes = ("HUD_", "Backdrop", "Orb_", "Floor")
for o in bpy.data.objects:
    if o.name.startswith(hide_prefixes):
        o.hide_set(True)
        o.hide_viewport = True
        o.hide_render = True

bpy.ops.wm.save_mainfile()
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_visible=True,
    export_apply=True,
    export_animations=False,
    export_cameras=False,
    export_yup=True,
)
print("EXPORTED", OUT, os.path.getsize(OUT))
