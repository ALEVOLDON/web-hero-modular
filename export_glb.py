"""Export a web-ready GLB. Motion is left to GSAP, not Blender."""
import bpy
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "hero_loop.blend")
OUT = os.path.join(ROOT, "web", "hero.glb")

if bpy.data.filepath.replace("/", "\\").lower() != BLEND.lower():
    bpy.ops.wm.open_mainfile(filepath=BLEND)

hide_prefixes = ("HUD_", "Backdrop", "Orb_", "Floor")
for o in bpy.data.objects:
    if o.name.startswith(hide_prefixes):
        o.hide_set(True)
        o.hide_render = True
        o.hide_viewport = True

# Clear baked object animation — GSAP owns motion
for o in bpy.data.objects:
    if o.animation_data:
        o.animation_data_clear()

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_visible=True,
    export_apply=True,
    export_animations=False,
    export_cameras=False,
    export_extras=False,
    export_yup=True,
)
print("EXPORTED", OUT, "bytes", os.path.getsize(OUT) if os.path.isfile(OUT) else 0)
