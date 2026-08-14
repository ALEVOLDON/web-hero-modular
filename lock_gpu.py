"""Force this .blend + Blender user prefs onto NVIDIA GPU. CPU stays off."""
import bpy

import os

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(ROOT, "hero_loop.blend")


def lock():
    sc = bpy.context.scene
    addon = bpy.context.preferences.addons.get("cycles")
    if not addon:
        raise SystemExit("Cycles addon missing")
    prefs = addon.preferences
    available = [t[0] for t in prefs.get_device_types(bpy.context)]
    backend = next((c for c in ("OPTIX", "CUDA") if c in available), None)
    if not backend:
        raise SystemExit(f"No GPU backend in {available}")
    prefs.compute_device_type = backend
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == backend
        print(f"[{'ON' if d.use else 'off'}] {d.name} ({d.type})")
    sc.cycles.device = "GPU"
    try:
        sc.cycles.denoiser = "OPTIX" if backend == "OPTIX" else "OPENIMAGEDENOISE"
    except Exception:
        pass
    bpy.ops.wm.save_userpref()
    if bpy.data.filepath:
        bpy.ops.wm.save_mainfile()
    print("LOCKED", backend, "device", sc.cycles.device, "file", bpy.data.filepath)


if __name__ == "__main__":
    lock()
