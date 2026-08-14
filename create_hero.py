"""
Modular Genesis — Eurorack synthesizer 3D hero scene generator.
Creates a high-precision 8-module Eurorack Skiff case, knobs, jacks, faders,
screens, and natural hanging patch cables with clean coordinate axes.
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
os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "textures"), exist_ok=True)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.view_settings.view_transform = "Filmic"
    sc.view_settings.look = "High Contrast"
    
    world = bpy.data.worlds.new("StudioDark")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.006, 0.009, 0.015, 1)
    bg.inputs["Strength"].default_value = 0.2
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return sc


def mat(name, color, rough=0.35, metal=0.0, emit=None, emit_s=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
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
    return m


def collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def assign(obj, material):
    if not obj.data.materials:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material


def smooth(obj):
    for f in obj.data.polygons:
        f.use_smooth = True


def from_bm(name, bm, col):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def box(name, sx, sy, sz, loc, col, material=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
    o = from_bm(name, bm, col)
    o.location = loc
    if material:
        assign(o, material)
    return o


def cyl(name, r, h, loc, col, material=None, verts=20):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=verts,
        radius1=r,
        radius2=r,
        depth=h,
    )
    o = from_bm(name, bm, col)
    o.location = loc
    if material:
        assign(o, material)
    return o


def bevel(obj, width=0.004, segments=2):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"


def hud_plane(name, sx, sy, loc, rot, material, col):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            loop[uv_layer].uv = (loop.vert.co.x * 0.5 + 0.5, loop.vert.co.y * 0.5 + 0.5)
    for v in bm.verts:
        v.co.x *= (sx * 0.5)
        v.co.y *= (sy * 0.5)
    o = from_bm(name, bm, col)
    o.location = loc
    o.rotation_euler = rot
    assign(o, material)
    return o


def load_tex(path, name):
    if not os.path.isfile(path):
        return None
    img = bpy.data.images.load(path, check_existing=True)
    img.name = name
    img.pack()
    return img


def tex_mat(name, img, emit=0.25, metal=0.45, rough=0.38):
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


def hud_mat(name, img, tint, strength=3.0):
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
    mix.inputs["Fac"].default_value = 0.35
    mix.inputs["Color2"].default_value = (*tint, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(mix.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def uv_local(u, v, mw, mh):
    x = (u - 0.5) * mw * 0.90
    y = (v - 0.5) * mh * 0.88
    return x, y


def cable(name, pts, col, material, radius=0.0035):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = 24
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
    # Forward along +Z (out of face), Down along -Y (towards floor)
    forward = Vector((0.0, 0.0, 1.0))
    down = Vector((0.0, -1.0, 0.0))
    out = sag * 0.45 + span * 0.14
    
    p0 = pa + Vector((0.0, 0.0, 0.022))
    p1 = pa + forward * (out * 0.45) + down * 0.02 + Vector((0.0, 0.0, 0.02))
    p2 = mid + forward * out + down * (sag * 0.40)
    p3 = pb + forward * (out * 0.45) + down * 0.02 + Vector((0.0, 0.0, 0.02))
    p4 = pb + Vector((0.0, 0.0, 0.022))
    return [p0, p1, p2, p3, p4]


def build():
    reset()
    col_case = collection("01_Case")
    col_cables = collection("02_Cables")
    tex_dir = os.path.join(ROOT, "textures")

    # Materials
    M_CASE_METAL = mat("CaseAnodized", (0.025, 0.028, 0.035), 0.28, 0.92)
    M_CHEEK_WOOD = mat("CheekWood", (0.045, 0.028, 0.018), 0.42, 0.08)
    M_RAIL_SILVER = mat("RailSilver", (0.55, 0.58, 0.62), 0.25, 0.95)
    M_PANEL_BASE = mat("PanelBase", (0.02, 0.022, 0.026), 0.40, 0.35)
    M_KNOB_BODY = mat("KnobBody", (0.04, 0.045, 0.05), 0.30, 0.45)
    M_KNOB_PTR = mat("KnobPointer", (0.92, 0.94, 0.96), 0.20, 0.10, emit=(0.9, 0.9, 0.9), emit_s=0.6)
    M_JACK_BEZEL = mat("JackBezel", (0.65, 0.68, 0.72), 0.22, 0.95)
    M_JACK_HOLE = mat("JackHole", (0.005, 0.005, 0.008), 0.8, 0.0)
    M_SCREW = mat("ScrewMetal", (0.35, 0.37, 0.40), 0.25, 0.9)
    M_TIP = mat("CableTip", (0.75, 0.78, 0.82), 0.18, 0.95)

    cables_m = [
        mat(f"CabMat_{i}", c, rough=0.48, metal=0.08, emit=c, emit_s=0.35)
        for i, c in enumerate(CABLE_COLORS)
    ]

    root = bpy.data.objects.new("CaseRoot", None)
    col_case.objects.link(root)
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)

    def adopt(o):
        o.parent = root
        return o

    inner_w = 1.14
    face_h = 0.44
    hp_u = inner_w / HP_TOTAL
    case_depth = 0.48
    case_height = 0.11

    # 1. Main Skiff Enclosure
    case_body = adopt(box("Case_Body", inner_w + 0.02, face_h + 0.03, case_height, (0.0, 0.0, -case_height * 0.5), col_case, M_CASE_METAL))
    bevel(case_body, 0.006, 3)

    # 2. Side Cheeks (Left & Right)
    cheek_thick = 0.024
    for i, x in enumerate((-(inner_w * 0.5 + cheek_thick * 0.5 + 0.008), inner_w * 0.5 + cheek_thick * 0.5 + 0.008)):
        ch = adopt(box(f"Case_Cheek_{i}", cheek_thick, face_h + 0.04, case_height + 0.02, (x, 0.0, -case_height * 0.45), col_case, M_CHEEK_WOOD))
        bevel(ch, 0.005, 3)

    # 3. Top & Bottom Mounting Rails
    top_rail = adopt(box("Case_Rail_Top", inner_w + 0.01, 0.014, 0.012, (0.0, face_h * 0.5 + 0.006, 0.002), col_case, M_RAIL_SILVER))
    bot_rail = adopt(box("Case_Rail_Bot", inner_w + 0.01, 0.014, 0.012, (0.0, -face_h * 0.5 - 0.006, 0.002), col_case, M_RAIL_SILVER))
    bevel(top_rail, 0.002, 2)
    bevel(bot_rail, 0.002, 2)

    screens = {
        "wave": load_tex(os.path.join(tex_dir, "screen_wave.png"), "ScrWave"),
        "steps": load_tex(os.path.join(tex_dir, "screen_steps.png"), "ScrSteps"),
        "spec": load_tex(os.path.join(tex_dir, "screen_spec.png"), "ScrSpec"),
    }

    jack_map = {}
    cursor = -inner_w * 0.5

    for mi, spec in enumerate(MODULES):
        mw = spec["hp"] * hp_u
        mid_x = cursor + mw * 0.5
        cursor += mw

        empty = bpy.data.objects.new(f"Module_{spec['id']}", None)
        col_case.objects.link(empty)
        empty.parent = root
        empty.location = (mid_x, 0.0, 0.0)

        # Module sub-panel
        body = box(f"Module_{spec['id']}_Body", mw - 0.002, face_h, 0.008, (0, 0, -0.004), col_case, M_PANEL_BASE)
        body.parent = empty

        # Silkscreen textured faceplate
        tex = load_tex(os.path.join(tex_dir, f"panel_{spec['id']}.png"), f"Panel_{spec['id']}")
        if tex:
            face_m = tex_mat(f"FaceM_{spec['id']}", tex, emit=0.28, metal=0.55, rough=0.32)
        else:
            face_m = mat(f"FaceM_{spec['id']}", (0.025, 0.028, 0.035), 0.40, 0.4)
        face = hud_plane(f"Module_{spec['id']}_Face", mw - 0.004, face_h - 0.004, (0, 0, 0.001), (0, 0, 0), face_m, col_case)
        face.parent = empty

        accent = spec["accent"]
        accent_mat = mat(f"Accent_{spec['id']}", accent, 0.3, 0.1, emit=accent, emit_s=0.8)

        # Knobs with synchronized pointers
        for ki, (label, u, v) in enumerate(spec.get("knobs", [])):
            x, y = uv_local(u, v, mw, face_h)
            stem = cyl(f"KnobStem_{spec['id']}_{ki}", 0.006, 0.008, (x, y, 0.004), col_case, M_CASE_METAL, verts=14)
            stem.parent = empty

            cap = cyl(f"Knob_{spec['id']}_{ki}", 0.0125, 0.010, (x, y, 0.010), col_case, M_KNOB_BODY, verts=20)
            cap.parent = empty
            smooth(cap)
            init_rot = (mi * 1.5 + ki * 0.8) % math.tau
            cap.rotation_euler.z = init_rot

            pointer = box(f"KnobPtr_{spec['id']}_{ki}", 0.002, 0.009, 0.0025, (0.0, 0.006, 0.005), col_case, M_KNOB_PTR)
            pointer.parent = cap

            ring = cyl(f"KnobRing_{spec['id']}_{ki}", 0.0145, 0.002, (x, y, 0.002), col_case, accent_mat, verts=20)
            ring.parent = empty

        # Jacks
        for ji, (label, u, v) in enumerate(spec.get("jacks", [])):
            x, y = uv_local(u, v, mw, face_h)
            bezel = cyl(f"Jack_{spec['id']}_{ji}", 0.008, 0.006, (x, y, 0.004), col_case, M_JACK_BEZEL, verts=16)
            hole = cyl(f"JackHole_{spec['id']}_{ji}", 0.004, 0.008, (x, y, 0.005), col_case, M_JACK_HOLE, verts=12)
            bezel.parent = empty
            hole.parent = empty
            jack_map[(spec["id"], ji)] = bezel

        # LEDs
        nled = spec.get("leds", 0)
        if nled:
            for li in range(nled):
                u = 0.12 + (0.76 * li / max(1, nled - 1))
                x, y = uv_local(u, 0.84 if spec["id"] == "CLK" else 0.86, mw, face_h)
                led_mat = mat(f"LEDMAT_{spec['id']}_{li}", (0.04, 0.05, 0.06), 0.2, 0.0, emit=accent, emit_s=0.5)
                led = cyl(f"LED_{spec['id']}_{li}", 0.0035, 0.003, (x, y, 0.003), col_case, led_mat, verts=12)
                led.parent = empty

        # Faders
        if spec.get("faders"):
            n = spec["faders"]
            for fi in range(n):
                u = 0.20 + fi * 0.20
                x, y0 = uv_local(u, 0.55, mw, face_h)
                slot = box(f"FaderSlot_{spec['id']}_{fi}", 0.003, 0.12, 0.003, (x, y0, 0.002), col_case, M_JACK_HOLE)
                cap = box(f"FaderCap_{spec['id']}_{fi}", 0.014, 0.009, 0.008, (x, y0 + (fi - 1.5) * 0.018, 0.008), col_case, M_KNOB_BODY)
                slot.parent = empty
                cap.parent = empty

        # OLED Display Screens
        kind = spec.get("screen")
        if kind and screens.get(kind):
            if spec["id"] == "VIS":
                sx, sy, v = 0.075, 0.040, 0.78
            elif spec["id"] == "VCO":
                sx, sy, v = 0.058, 0.024, 0.86
            else:
                sx, sy, v = 0.072, 0.022, 0.80
            sm = hud_mat(f"ScreenM_{spec['id']}", screens[kind], accent, 2.5)
            x, y = uv_local(0.5, v, mw, face_h)
            scr = hud_plane(f"Screen_{spec['id']}", sx, sy, (x, y, 0.003), (0, 0, 0), sm, col_case)
            scr.parent = empty

        # Screws
        for sx, sy in ((-mw * 0.42, face_h * 0.45), (mw * 0.42, face_h * 0.45), (-mw * 0.42, -face_h * 0.45), (mw * 0.42, -face_h * 0.45)):
            scw = cyl(f"Screw_{spec['id']}_{sx:.2f}", 0.003, 0.0025, (sx, sy, 0.003), col_case, M_SCREW, verts=10)
            scw.parent = empty

    bpy.context.view_layer.update()

    # Cables & Routes
    cable_sidecar = []
    for ci, (sa, ja, sb, jb, sag, coli, radius) in enumerate(ROUTES):
        a = jack_map.get((sa, ja))
        b = jack_map.get((sb, jb))
        if not a or not b:
            continue
        pa = a.matrix_world.translation.copy()
        pb = b.matrix_world.translation.copy()
        pts = hanging_pts(pa, pb, sag)
        cm = cables_m[coli % len(cables_m)]
        c = cable(f"Cable_{ci}", pts, col_cables, cm, radius)
        c.parent = root
        
        # Plugs & Sleeves standing out from jacks (+Z)
        for pi, (pt, p_name) in enumerate([(pa, "A"), (pb, "B")]):
            tip = cyl(f"Tip_{ci}_{p_name}", radius * 1.3, 0.014, pt + Vector((0, 0, 0.008)), col_cables, M_TIP, verts=12)
            tip.parent = root
            sleeve = cyl(f"Sleeve_{ci}_{p_name}", radius * 1.5, 0.012, pt + Vector((0, 0, 0.018)), col_cables, cm, verts=12)
            sleeve.parent = root

        for pi, p in enumerate(pts):
            empty = bpy.data.objects.new(f"Path_{ci}_{pi}", None)
            empty.location = p
            empty.parent = root
            col_cables.objects.link(empty)

        cable_sidecar.append({
            "name": f"Cable_{ci}",
            "color": list(CABLE_COLORS[coli % len(CABLE_COLORS)]),
            "points": [list(p) for p in pts],
        })

    sidecar_path = os.path.join(ROOT, "web", "cables.json")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump({"cables": cable_sidecar}, f, indent=2)
    print("Exported cables sidecar to", sidecar_path)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("Saved blend file to", BLEND)


if __name__ == "__main__":
    build()
