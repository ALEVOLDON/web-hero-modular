"""
Modular Genesis — looping website hero.
Dark lab, eurorack case, patch cables, HUD panels, sequencer chase.
EEVEE, 8s seamless loop. Run:
  blender --background --python create_hero.py
  blender --background --python create_hero.py -- --anim
"""
import bpy
import bmesh
import json
import math
import os
import sys
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from module_spec import CABLE_COLORS, HP_TOTAL, MODULES, ROUTES
BLEND = os.path.join(ROOT, "hero_loop.blend")
STILL = os.path.join(ROOT, "renders", "still.png")
ANIM_DIR = os.path.join(ROOT, "renders", "frames")
MP4 = os.path.join(ROOT, "renders", "loop.mp4")
WEB_MP4 = os.path.join(ROOT, "web", "loop.mp4")

FPS = 24
DURATION = 8
FRAMES = FPS * DURATION  # 192
WANT_ANIM = "--anim" in sys.argv

os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
os.makedirs(ANIM_DIR, exist_ok=True)


def force_gpu():
    """Render on the NVIDIA GPU only. Never enable the CPU as a Cycles device."""
    cycles_addon = bpy.context.preferences.addons.get("cycles")
    if not cycles_addon:
        print("GPU LOCK: Cycles addon missing")
        return False
    cprefs = cycles_addon.preferences
    try:
        available = [t[0] for t in cprefs.get_device_types(bpy.context)]
    except Exception:
        available = ["OPTIX", "CUDA"]
    backend = None
    for candidate in ("OPTIX", "CUDA"):
        if candidate in available:
            backend = candidate
            break
    if not backend:
        print("GPU LOCK: no NVIDIA backend", available)
        return False
    cprefs.compute_device_type = backend
    try:
        cprefs.get_devices()
    except Exception:
        pass
    for dev in cprefs.devices:
        dev.use = dev.type == backend
        print(f"GPU LOCK: [{'ON' if dev.use else 'off'}] {dev.name} ({dev.type})")
    sc = bpy.context.scene
    sc.cycles.device = "GPU"
    try:
        sc.cycles.denoiser = "OPTIX" if backend == "OPTIX" else "OPENIMAGEDENOISE"
    except Exception:
        pass
    try:
        bpy.ops.wm.save_userpref()
    except Exception as e:
        print("GPU LOCK: userpref", e)
    print(f"GPU LOCK: backend={backend} cycles.device={sc.cycles.device}")
    return True


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    force_gpu()
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.frame_start = 1
    sc.frame_end = FRAMES
    sc.render.fps = FPS
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Filmic"
    sc.view_settings.look = "High Contrast"
    try:
        ee = sc.eevee
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = 64
        if hasattr(ee, "use_raytracing"):
            ee.use_raytracing = True
        if hasattr(ee, "use_volumetric_shadows"):
            ee.use_volumetric_shadows = True
        if hasattr(ee, "volumetric_tile_size"):
            ee.volumetric_tile_size = "2"
        if hasattr(ee, "use_shadows"):
            ee.use_shadows = True
    except Exception as e:
        print("eevee prefs", e)
    world = bpy.data.worlds.new("Night")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.004, 0.006, 0.012, 1)
    bg.inputs["Strength"].default_value = 0.15
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return sc


def mat(name, color, rough=0.4, metal=0.0, emit=None, emit_s=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if emit is not None and emit_s > 0 and alpha >= 1.0 and metal == 0 and rough > 0.8:
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*emit, 1)
        em.inputs["Strength"].default_value = emit_s
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        return m
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Alpha" in b.inputs:
        b.inputs["Alpha"].default_value = alpha
    if emit is not None:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (*emit, 1)
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit_s
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    if alpha < 1.0:
        m.blend_method = "BLEND"
        m.use_backface_culling = False
    return m


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def from_bm(name, bm, col):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    return o


def box(name, sx, sy, sz, loc, col, material, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    o = from_bm(name, bm, col)
    o.location = loc
    o.rotation_euler = rot
    assign(o, material)
    return o


def cyl(name, r, depth, loc, col, material, verts=20, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=verts,
        radius1=r, radius2=r, depth=depth,
    )
    o = from_bm(name, bm, col)
    o.location = loc
    o.rotation_euler = rot
    assign(o, material)
    return o


def assign(o, m):
    if o.data.materials:
        o.data.materials[0] = m
    else:
        o.data.materials.append(m)


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def bevel(o, w=0.002, s=2):
    md = o.modifiers.new("Bevel", "BEVEL")
    md.width = w
    md.segments = s
    md.limit_method = "ANGLE"
    md.angle_limit = math.radians(30)
    return md


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def paint_waveform(name, w=512, h=256, color=(0.2, 0.75, 1.0)):
    img = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    px = [0.0] * (w * h * 4)
    for x in range(w):
        t = x / (w - 1)
        y = 0.5 + 0.28 * math.sin(t * math.tau * 4.2) + 0.12 * math.sin(t * math.tau * 11.0)
        y += 0.04 * math.sin(t * math.tau * 23)
        cy = int(y * (h - 1))
        for yy in range(h):
            i = (yy * w + x) * 4
            dist = abs(yy - cy) / h
            a = max(0.0, 1.0 - dist * 18)
            glow = max(0.0, 1.0 - dist * 6) * 0.25
            px[i:i + 4] = (color[0] * (a + glow), color[1] * (a + glow), color[2] * (a + glow), min(1.0, a + glow))
        # baseline
        mid = h // 2
        i = (mid * w + x) * 4
        px[i] = min(1.0, px[i] + 0.08)
        px[i + 3] = min(1.0, px[i + 3] + 0.3)
    img.pixels = px
    img.pack()
    return img


def paint_spectrum(name, w=512, h=256):
    img = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    px = [0.0] * (w * h * 4)
    bars = 28
    bw = w // bars
    for b in range(bars):
        hgt = 0.18 + 0.72 * abs(math.sin(b * 0.7 + 0.4)) * (0.5 + 0.5 * math.sin(b * 0.21))
        bh = int(hgt * h)
        cr = 1.0
        cg = 0.45 + 0.4 * (b / bars)
        cb = 0.12
        for x in range(b * bw + 3, min(w, (b + 1) * bw - 2)):
            for y in range(bh):
                i = (y * w + x) * 4
                fade = y / max(1, bh)
                px[i:i + 4] = (cr, cg * (0.5 + 0.5 * fade), cb, 0.55 + 0.45 * fade)
    img.pixels = px
    img.pack()
    return img


def paint_graph(name, w=512, h=320):
    img = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    px = [0.02, 0.03, 0.05, 0.55] * (w * h)
    nodes = [(80, 80), (80, 230), (220, 150), (360, 80), (360, 230), (450, 150)]
    # lines
    pairs = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 5), (4, 5)]

    def setp(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            i = (y * w + x) * 4
            px[i:i + 4] = c

    for a, b in pairs:
        x0, y0 = nodes[a]
        x1, y1 = nodes[b]
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(steps + 1):
            t = s / max(1, steps)
            x = int(x0 + (x1 - x0) * t)
            y = int(y0 + (y1 - y0) * t)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    setp(x + dx, y + dy, (1.0, 0.55, 0.12, 0.85))
    for i, (x, y) in enumerate(nodes):
        col = (0.2, 0.85, 1.0, 1.0) if i in (2, 5) else (1.0, 0.5, 0.1, 1.0)
        for yy in range(y - 14, y + 15):
            for xx in range(x - 22, x + 23):
                setp(xx, yy, (0.04, 0.05, 0.08, 0.9))
        for yy in range(y - 12, y + 13):
            setp(x - 22, yy, col)
            setp(x + 22, yy, col)
        for xx in range(x - 22, x + 23):
            setp(xx, y - 14, col)
            setp(xx, y + 14, col)
    img.pixels = px
    img.pack()
    return img


def hud_plane(name, sx, sy, loc, rot, material, col):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            loop[uv_layer].uv = (loop.vert.co.x + 0.5, loop.vert.co.y + 0.5)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
    o = from_bm(name, bm, col)
    o.location = loc
    o.rotation_euler = rot
    assign(o, material)
    return o


def paint_circuit(name, w=1024, h=640):
    img = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, alpha=True)
    px = [0.01, 0.015, 0.03, 1.0] * (w * h)

    def setp(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            i = (y * w + x) * 4
            px[i:i + 4] = c

    col = (0.12, 0.45, 0.75, 0.55)
    for x in range(0, w, 48):
        for y in range(h):
            setp(x, y, col)
    for y in range(0, h, 48):
        for x in range(w):
            setp(x, y, col)
    # a few traces
    for k in range(8):
        x0, y0 = 80 + k * 110, 60 + (k * 47) % 400
        for t in range(180):
            setp(x0 + t, y0, (0.2, 0.7, 1.0, 0.7))
            setp(x0 + t, y0 + 1, (0.2, 0.7, 1.0, 0.35))
            if t > 90:
                setp(x0 + 90, y0 + (t - 90), (0.2, 0.7, 1.0, 0.7))
    img.pixels = px
    img.pack()
    return img


def hud_mat(name, img, tint, strength=6.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Smart"
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "ADD"
    mix.inputs["Fac"].default_value = 0.25
    mix.inputs["Color2"].default_value = (*tint, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(mix.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def cable(name, pts, col, material, radius=0.004):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = 20
    spl = cu.splines.new("BEZIER")
    spl.bezier_points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        bp = spl.bezier_points[i]
        bp.co = p
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    col.objects.link(o)
    assign(o, material)
    return o


def hanging_pts(pa, pb, sag):
    span = (pb - pa).length
    mid = (pa + pb) * 0.5
    out = sag * 0.95 + span * 0.22
    forward = Vector((0.0, -1.0, 0.0))
    down = Vector((0.0, 0.0, -1.0))
    p1 = pa + forward * (out * 0.28) + down * 0.015
    p2 = mid + forward * out + down * (sag * 0.62)
    p3 = pb + forward * (out * 0.28) + down * 0.015
    return [Vector(pa), p1, p2, p3, Vector(pb)]


def load_tex(path, name):
    if not os.path.isfile(path):
        print("missing tex", path)
        return None
    img = bpy.data.images.load(path, check_existing=True)
    img.name = name
    img.pack()
    return img


def tex_mat(name, img, emit=0.28, metal=0.38, rough=0.44):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Smart"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emit
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def uv_local(u, v, mw, mh):
    x = (u - 0.5) * mw * 0.90
    y = (v - 0.5) * mh * 0.88
    return x, y


def _iter_fcurves(id_data):
    ad = getattr(id_data, "animation_data", None)
    if not ad or not ad.action:
        return
    action = ad.action
    if hasattr(action, "fcurves"):
        for fc in action.fcurves:
            yield fc
        return
    # Blender 5.x layered actions
    try:
        for layer in action.layers:
            for strip in layer.strips:
                bag = getattr(strip, "channelbag", None)
                if bag is None and hasattr(strip, "channelbags"):
                    bags = strip.channelbags
                    bag = bags[0] if bags else None
                if bag is None:
                    continue
                for fc in bag.fcurves:
                    yield fc
    except Exception:
        return


def _soften_fcurves(id_data, constant=False):
    for fc in _iter_fcurves(id_data):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT" if constant else "BEZIER"


def key_sine(obj, data_path, index, mid, amp, frames=FRAMES, step=8):
    obj.rotation_mode = "XYZ"
    for f in list(range(1, frames + 1, step)) + [frames + 1]:
        t = (f - 1) / frames * math.tau
        val = mid + amp * math.sin(t)
        if index is None:
            # location/scale whole? not used
            continue
        if data_path == "location":
            loc = list(obj.location)
            loc[index] = val
            obj.location = loc
            obj.keyframe_insert("location", index=index, frame=f)
        elif data_path == "rotation_euler":
            rot = list(obj.rotation_euler)
            rot[index] = val
            obj.rotation_euler = rot
            obj.keyframe_insert("rotation_euler", index=index, frame=f)
        elif data_path == "scale":
            sc = list(obj.scale)
            sc[index] = val
            obj.scale = sc
            obj.keyframe_insert("scale", index=index, frame=f)
    _soften_fcurves(obj)


def key_energy(light, values, frames=FRAMES):
    for f, e in values:
        light.data.energy = e
        light.data.keyframe_insert("energy", frame=f)
    _soften_fcurves(light, constant=True)


def build():
    sc = reset()
    col_set = collection("01_Set")
    col_case = collection("02_Case")
    col_cables = collection("03_Cables")
    col_hud = collection("04_HUD")
    col_fx = collection("05_FX")
    col_cam = collection("06_Camera")
    tex_dir = os.path.join(ROOT, "textures")

    M_METAL = mat("MetalCase", (0.03, 0.033, 0.04), 0.32, 0.85)
    M_PANEL = mat("Panel", (0.018, 0.02, 0.024), 0.45, 0.2)
    M_TABLE = mat("Table", (0.012, 0.013, 0.016), 0.18, 0.7)
    M_KNOB_OR = mat("KnobOr", (0.85, 0.38, 0.06), 0.28, 0.15)
    M_KNOB_CY = mat("KnobCy", (0.12, 0.55, 0.85), 0.28, 0.1)
    M_KNOB_MG = mat("KnobMg", (0.75, 0.18, 0.55), 0.28, 0.1)
    M_KNOB_WH = mat("KnobWh", (0.82, 0.84, 0.88), 0.3, 0.05)
    M_JACK = mat("Jack", (0.08, 0.08, 0.09), 0.35, 0.6)
    M_SCREW = mat("Screw", (0.18, 0.19, 0.2), 0.28, 0.85)
    M_TIP = mat("Tip", (0.55, 0.56, 0.58), 0.22, 0.9)
    knobs_m = [M_KNOB_OR, M_KNOB_CY, M_KNOB_MG, M_KNOB_WH]
    cables_m = [
        mat(f"Cab{i}", c, 0.38, 0.05, emit=c, emit_s=0.55)
        for i, c in enumerate(CABLE_COLORS)
    ]

    table = box("Table", 1.85, 1.05, 0.05, (0.22, 0.02, -0.025), col_set, M_TABLE)
    bevel(table, 0.006, 3)
    box("Floor", 10.0, 10.0, 0.03, (0.0, 0.0, -0.07), col_set, mat("Floor", (0.006, 0.008, 0.012), 0.75, 0.0))

    circ = paint_circuit("CircuitBG")
    m_circ = hud_mat("CircuitM", circ, (0.15, 0.55, 0.9), 1.1)
    hud_plane("Backdrop", 6.5, 3.6, (0.3, 2.4, 1.15), (math.radians(90), 0, 0), m_circ, col_set)

    root = bpy.data.objects.new("CaseRoot", None)
    col_case.objects.link(root)
    root.location = (0.28, 0.05, 0.0)
    root.rotation_euler = (math.radians(6), 0, math.radians(18))

    def adopt(o):
        o.parent = root
        return o

    case_w, case_d, case_h = 1.22, 0.52, 0.13
    case = adopt(box("Case", case_w, case_d, case_h, (0.0, 0.0, 0.09), col_case, M_METAL))
    bevel(case, 0.008, 3)
    inner_w = 1.12
    face_h = 0.44
    hp_u = inner_w / HP_TOTAL
    for i, x in enumerate((-case_w * 0.5, case_w * 0.5)):
        ch = adopt(box(f"Cheek_{i}", 0.038, 0.54, 0.18, (x, 0.0, 0.09), col_case, M_METAL))
        bevel(ch, 0.005, 2)

    screens = {
        "wave": load_tex(os.path.join(tex_dir, "screen_wave.png"), "ScrWave"),
        "steps": load_tex(os.path.join(tex_dir, "screen_steps.png"), "ScrSteps"),
        "spec": load_tex(os.path.join(tex_dir, "screen_spec.png"), "ScrSpec"),
    }

    jack_map = {}
    leds = []
    cursor = -inner_w * 0.5

    for mi, spec in enumerate(MODULES):
        mw = spec["hp"] * hp_u
        mid_x = cursor + mw * 0.5
        cursor += mw
        empty = bpy.data.objects.new(f"Module_{spec['id']}", None)
        col_case.objects.link(empty)
        empty.parent = root
        empty.location = (mid_x, 0.0, 0.156)

        body = box(f"Module_{spec['id']}_Body", mw - 0.004, face_h, 0.01, (0, 0, -0.004), col_case, M_PANEL)
        body.parent = empty
        tex = load_tex(os.path.join(tex_dir, f"panel_{spec['id']}.png"), f"Panel_{spec['id']}")
        if tex:
            face_m = tex_mat(f"FaceM_{spec['id']}", tex, emit=0.32)
        else:
            face_m = mat(f"FaceM_{spec['id']}", (0.02, 0.022, 0.028), 0.45, 0.25)
        face = hud_plane(f"Module_{spec['id']}_Face", mw - 0.008, face_h - 0.01, (0, 0, 0.003), (0, 0, 0), face_m, col_case)
        face.parent = empty

        accent = spec["accent"]
        km = knobs_m[mi % 4]
        for ki, (label, u, v) in enumerate(spec.get("knobs", [])):
            x, y = uv_local(u, v, mw, face_h)
            stem = cyl(f"KnobStem_{spec['id']}_{ki}", 0.0055, 0.01, (x, y, 0.004), col_case, M_JACK, verts=10)
            cap = cyl(f"Knob_{spec['id']}_{ki}", 0.0115, 0.009, (x, y, 0.012), col_case, km, verts=18)
            stem.parent = empty
            cap.parent = empty
            smooth(cap)
            cap.rotation_euler.z = (mi * 1.7 + ki * 0.8) % math.tau
            pointer = box(f"KnobPtr_{spec['id']}_{ki}", 0.002, 0.009, 0.002, (x, y + 0.006, 0.017), col_case, M_KNOB_WH)
            pointer.parent = empty

        for ji, (label, u, v) in enumerate(spec.get("jacks", [])):
            x, y = uv_local(u, v, mw, face_h)
            ring = cyl(f"Jack_{spec['id']}_{ji}", 0.0072, 0.006, (x, y, 0.005), col_case, M_JACK, verts=12)
            hole = cyl(f"JackHole_{spec['id']}_{ji}", 0.0036, 0.007, (x, y, 0.005), col_case, mat("Hole", (0.01, 0.01, 0.012), 0.6, 0.0), verts=10)
            ring.parent = empty
            hole.parent = empty
            jack_map[(spec["id"], ji)] = ring

        nled = spec.get("leds", 0)
        if nled:
            for li in range(nled):
                u = 0.12 + (0.76 * li / max(1, nled - 1))
                x, y = uv_local(u, 0.84 if spec["id"] == "CLK" else 0.86, mw, face_h)
                led = box(
                    f"LED_{spec['id']}_{li}", 0.01, 0.006, 0.0025, (x, y, 0.006), col_case,
                    mat(f"LEDMAT_{spec['id']}_{li}", (0.02, 0.08, 0.06), 0.3, 0.0, emit=accent, emit_s=0.25),
                )
                led.parent = empty
                leds.append(led)

        if spec.get("faders"):
            n = spec["faders"]
            for fi in range(n):
                u = 0.20 + fi * 0.20
                x, y0 = uv_local(u, 0.55, mw, face_h)
                rail = box(f"FaderRail_{spec['id']}_{fi}", 0.006, 0.12, 0.003, (x, y0, 0.004), col_case, M_JACK)
                cap = box(f"FaderCap_{spec['id']}_{fi}", 0.016, 0.012, 0.007, (x, y0 + (fi - 1.5) * 0.016, 0.01), col_case, knobs_m[fi % 4])
                rail.parent = empty
                cap.parent = empty

        kind = spec.get("screen")
        if kind and screens.get(kind):
            if spec["id"] == "VIS":
                sx, sy, v = 0.072, 0.038, 0.78
            elif spec["id"] == "VCO":
                sx, sy, v = 0.055, 0.022, 0.86
            else:
                sx, sy, v = 0.07, 0.02, 0.80
            sm = hud_mat(f"ScreenM_{spec['id']}", screens[kind], accent, 2.4)
            x, y = uv_local(0.5, v, mw, face_h)
            scr = hud_plane(f"Screen_{spec['id']}", sx, sy, (x, y, 0.006), (0, 0, 0), sm, col_case)
            scr.parent = empty

        for sx, sy in ((-mw * 0.42, face_h * 0.42), (mw * 0.42, face_h * 0.42), (-mw * 0.42, -face_h * 0.42), (mw * 0.42, -face_h * 0.42)):
            scw = cyl(f"Screw_{spec['id']}_{sx:.2f}", 0.0032, 0.003, (sx, sy, 0.006), col_case, M_SCREW, verts=8)
            scw.parent = empty

        rail = box(f"Rail_{spec['id']}", 0.003, face_h + 0.004, 0.012, (mw * 0.5, 0, -0.002), col_case, M_METAL)
        rail.parent = empty

    bpy.context.view_layer.update()
    cable_sidecar = []
    for ci, (sa, ja, sb, jb, sag, coli, radius) in enumerate(ROUTES):
        a = jack_map.get((sa, ja))
        b = jack_map.get((sb, jb))
        if not a or not b:
            print("route miss", sa, ja, sb, jb)
            continue
        pa = a.matrix_world.translation.copy()
        pb = b.matrix_world.translation.copy()
        pa.z += 0.01
        pb.z += 0.01
        pts = hanging_pts(pa, pb, sag)
        cm = cables_m[coli % len(cables_m)]
        c = cable(f"Cable_{ci}", pts, col_cables, cm, radius)
        # metal tips
        tip_a = cyl(f"Tip_{ci}_A", radius * 1.45, 0.018, pa, col_cables, M_TIP, verts=10)
        tip_b = cyl(f"Tip_{ci}_B", radius * 1.45, 0.018, pb, col_cables, M_TIP, verts=10)
        tip_a.rotation_euler = (math.radians(90), 0, 0)
        tip_b.rotation_euler = (math.radians(90), 0, 0)
        sleeve_a = cyl(f"Sleeve_{ci}_A", radius * 1.7, 0.012, pa + Vector((0, -0.01, 0)), col_cables, cm, verts=10)
        sleeve_b = cyl(f"Sleeve_{ci}_B", radius * 1.7, 0.012, pb + Vector((0, -0.01, 0)), col_cables, cm, verts=10)
        for pi, p in enumerate(pts):
            empty = bpy.data.objects.new(f"Path_{ci}_{pi}", None)
            empty.location = p
            empty.empty_display_size = 0.008
            col_cables.objects.link(empty)
        cable_sidecar.append({
            "name": f"Cable_{ci}",
            "color": list(CABLE_COLORS[coli % len(CABLE_COLORS)]),
            "points": [list(p) for p in pts],
        })

    sidecar_path = os.path.join(ROOT, "web", "cables.json")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump({"cables": cable_sidecar}, f, indent=2)
    print("cables", sidecar_path, len(cable_sidecar))

    wf = paint_waveform("HUD_Wave")
    sp = paint_spectrum("HUD_Spec")
    gr = paint_graph("HUD_Graph")
    m_wf = hud_mat("HUD_WaveM", wf, (0.25, 0.75, 1.0), 2.2)
    m_sp = hud_mat("HUD_SpecM", sp, (1.0, 0.55, 0.15), 2.0)
    m_gr = hud_mat("HUD_GraphM", gr, (1.0, 0.5, 0.12), 1.8)

    def hud(name, sx, sy, loc, screen_mat):
        o = hud_plane(name, sx, sy, loc, (0, 0, 0), screen_mat, col_hud)
        look = Vector((1.55, -1.55, 0.85)) - Vector(loc)
        o.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
        key_sine(o, "location", 2, loc[2], 0.016)
        return o

    # small cards around the case — left of frame stays empty for site title
    hud("HUD_Wave", 0.22, 0.12, (-0.12, -0.34, 0.52), m_wf)
    hud("HUD_Graph", 0.24, 0.14, (1.08, 0.22, 0.64), m_gr)
    hud("HUD_Spec", 0.17, 0.10, (1.18, -0.08, 0.40), m_sp)

    for i, (p, colr, r) in enumerate((
        ((1.05, 0.35, 0.55), (0.2, 0.8, 1.0), 0.028),
        ((0.75, 0.42, 0.68), (1.0, 0.5, 0.12), 0.022),
        ((-0.05, 0.30, 0.50), (0.55, 0.25, 1.0), 0.02),
    )):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r)
        o = from_bm(f"Orb_{i}", bm, col_fx)
        o.location = p
        assign(o, mat(f"OrbM_{i}", colr, 0.15, 0.0, emit=colr, emit_s=6.0))
        smooth(o)
        key_sine(o, "location", 2, p[2], 0.03 + 0.008 * i)

    # lights
    def add_light(name, typ, loc, energy, color, size=0.4):
        l = bpy.data.lights.new(name, typ)
        l.energy = energy
        l.color = color
        if typ == "AREA":
            l.size = size
        o = bpy.data.objects.new(name, l)
        col_fx.objects.link(o)
        o.location = loc
        return o

    key = add_light("Key", "AREA", (0.4, -1.3, 0.95), 140, (0.8, 0.88, 1.0), 1.0)
    key.rotation_euler = (math.radians(58), 0, math.radians(12))
    rim = add_light("Rim", "AREA", (-0.9, 0.7, 0.85), 90, (0.25, 0.75, 1.0), 0.7)
    rim.rotation_euler = (math.radians(65), 0, math.radians(-35))
    warm = add_light("Warm", "AREA", (1.15, -0.35, 0.65), 70, (1.0, 0.5, 0.15), 0.45)
    warm.rotation_euler = (math.radians(48), 0, math.radians(-60))
    fill = add_light("Fill", "AREA", (0.1, -1.8, 0.45), 22, (0.55, 0.65, 1.0), 2.2)
    fill.rotation_euler = (math.radians(72), 0, 0)

    # sequencer chase on LED materials
    step = FRAMES // 16  # 12
    for i, led in enumerate(leds):
        m = led.data.materials[0]
        nt = m.node_tree
        em = next((n for n in nt.nodes if n.type == "EMISSION" or n.type == "BSDF_PRINCIPLED"), None)
        sock = None
        node = None
        for n in nt.nodes:
            if n.type == "BSDF_PRINCIPLED" and "Emission Strength" in n.inputs:
                node, sock = n, n.inputs["Emission Strength"]
                break
            if n.type == "EMISSION":
                node, sock = n, n.inputs["Strength"]
                break
        if not node:
            continue
        for f in range(1, FRAMES + 2):
            step_i = ((f - 1) // step) % 16
            on = step_i == i
            sock.default_value = 8.0 if on else 0.15
            sock.keyframe_insert("default_value", frame=f)
        _soften_fcurves(m.node_tree, constant=True)

    # camera rig
    pivot = bpy.data.objects.new("CamPivot", None)
    col_cam.objects.link(pivot)
    pivot.location = (0.30, 0.05, 0.16)
    cam_data = bpy.data.cameras.new("HeroCam")
    cam_data.lens = 32
    cam_data.sensor_width = 36
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = case
    cam_data.dof.aperture_fstop = 2.4
    cam = bpy.data.objects.new("HeroCam", cam_data)
    col_cam.objects.link(cam)
    cam.parent = pivot
    cam.location = (1.25, -1.48, 0.78)
    cam.rotation_euler = (math.radians(66), 0, math.radians(28))
    cam_data.lens = 30
    sc.camera = cam
    key_sine(pivot, "rotation_euler", 2, 0.0, math.radians(5))
    key_sine(cam, "location", 1, -1.48, 0.035)

    # compositor glare (Blender 5.x: scene.node_tree removed)
    try:
        if hasattr(sc, "compositing_node_group"):
            ng = bpy.data.node_groups.new("HeroComp", "CompositorNodeTree")
            sc.compositing_node_group = ng
            nt = ng
        else:
            sc.use_nodes = True
            nt = sc.node_tree
        rlayers = nt.nodes.new("CompositorNodeRLayers")
        glare = nt.nodes.new("CompositorNodeGlare")
        try:
            glare.glare_type = "FOG_GLOW"
        except Exception:
            try:
                glare.glare_type = "BLOOM"
            except Exception:
                pass
        if hasattr(glare, "mix"):
            glare.mix = 0.15
        if hasattr(glare, "threshold"):
            glare.threshold = 0.6
        composite = nt.nodes.new("CompositorNodeComposite")
        nt.links.new(rlayers.outputs["Image"], glare.inputs["Image"])
        nt.links.new(glare.outputs["Image"], composite.inputs["Image"])
        print("compositor ok")
    except Exception as e:
        print("compositor skipped", e)

    sc.render.filepath = STILL
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SAVED", BLEND)
    print("objects", len(bpy.data.objects))
    return sc


def render_still(sc):
    force_gpu()
    sc.cycles.device = "GPU"
    sc.render.filepath = STILL
    sc.render.image_settings.file_format = "PNG"
    sc.render.resolution_percentage = 70
    sc.frame_set(24)
    print("RENDER STILL")
    bpy.ops.render.render(write_still=True)
    print("STILL", STILL, os.path.exists(STILL))


def render_anim(sc):
    force_gpu()
    sc.cycles.device = "GPU"
    sc.render.resolution_percentage = 70
    sc.render.filepath = os.path.join(ANIM_DIR, "f_")
    sc.render.image_settings.file_format = "PNG"
    print("RENDER ANIM", FRAMES, "frames")
    bpy.ops.render.render(animation=True)
    print("FRAMES DONE")


def stitch_ffmpeg():
    import shutil
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        # blender often ships without; try common path
        print("ffmpeg not on PATH, skip mp4 stitch")
        return False
    cmd = (
        f'"{ffmpeg}" -y -framerate {FPS} -i "{os.path.join(ANIM_DIR, "f_%04d.png")}" '
        f'-c:v libx264 -pix_fmt yuv420p -crf 18 "{MP4}"'
    )
    print(cmd)
    os.system(cmd)
    if os.path.exists(MP4):
        import shutil as sh
        sh.copy2(MP4, WEB_MP4)
        print("MP4", MP4)
        return True
    return False


if __name__ == "__main__":
    sc = build()
    render_still(sc)
    bpy.ops.wm.save_mainfile()
    if WANT_ANIM:
        render_anim(sc)
        stitch_ffmpeg()
        bpy.ops.wm.save_mainfile()
    print("DONE")
