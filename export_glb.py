"""Export clean web-ready GLB from hero_loop.blend."""
import bpy
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "hero_loop.blend")
OUT = os.path.join(ROOT, "web", "hero.glb")

if bpy.data.filepath.replace("/", "\\").lower() != BLEND.lower():
    bpy.ops.wm.open_mainfile(filepath=BLEND)

# Hide non-case objects
hide_prefixes = ("HUD_", "Backdrop", "Orb_", "Floor", "Table")
for o in bpy.data.objects:
    if o.name.startswith(hide_prefixes):
        o.hide_set(True)
        o.hide_render = True
        o.hide_viewport = True

# Clear baked animation
for o in bpy.data.objects:
    if o.animation_data:
        o.animation_data_clear()

# Convert curve cables to real meshes for glTF
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
        print("Converted cables to mesh:", len(cables))
    except Exception as e:
        print("Cable conversion error:", e)

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
    print("EXPORTED DRACO GLB:", OUT, "bytes:", os.path.getsize(OUT) if os.path.isfile(OUT) else 0)
except Exception as err:
    print("Draco export failed, trying standard GLTF:", err)
    bpy.ops.export_scene.gltf(**kwargs)
    print("EXPORTED STANDARD GLB:", OUT, "bytes:", os.path.getsize(OUT) if os.path.isfile(OUT) else 0)
