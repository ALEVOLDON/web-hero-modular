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

# Curves become real tubes in glTF
cables = [o for o in bpy.data.objects if o.name.startswith("Cable_") and o.type == "CURVE"]
if cables:
    bpy.ops.object.select_all(action="DESELECT")
    for o in cables:
        o.hide_set(False)
        o.hide_viewport = False
        o.select_set(True)
    bpy.context.view_layer.objects.active = cables[0]
    try:
        bpy.ops.object.convert(target="MESH")
        print("converted cables", len(cables))
    except Exception as e:
        print("cable convert", e)

kwargs = dict(
    filepath=OUT,
    export_format="GLB",
    use_visible=True,
    export_apply=True,
    export_animations=False,
    export_cameras=False,
    export_extras=True,
    export_yup=True,
)
try:
    bpy.ops.export_scene.gltf(
        **kwargs,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
    )
    print("EXPORTED DRACO", OUT, "bytes", os.path.getsize(OUT) if os.path.isfile(OUT) else 0)
except TypeError:
    bpy.ops.export_scene.gltf(**kwargs)
    print("EXPORTED", OUT, "bytes", os.path.getsize(OUT) if os.path.isfile(OUT) else 0)
