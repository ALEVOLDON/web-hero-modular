"""
Modular Genesis — Eurorack Synthesizer 3D Hero Master Generator.
High-precision 8-module Eurorack Skiff case, knurled knobs, Thonkiconn 3.5mm jacks,
linear faders, OLED screens, domed LEDs, M3 socket screws, and catenary patch cables.
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
    engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else "BLENDER_EEVEE"
    sc.render.engine = engine
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
    bg.inputs["Color"].default_value = (0.008, 0.012, 0.018, 1)
    bg.inputs["Strength"].default_value = 0.3
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


def cyl(name, r, h, loc, col, material=None, verts=24):
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
            # create_grid(size=1.0) creates verts in [-1.0, 1.0], so * 0.5 + 0.5 maps to [0.0, 1.0]
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


def tex_mat(name, img, emit=0.22, metal=0.60, rough=0.32):
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


def hud_mat(name, img, tint, strength=2.8):
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


def uv_to_local(u, v, face_w, face_h):
    x = (u - 0.5) * face_w
    y = (v - 0.5) * face_h
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
    forward = Vector((0.0, 0.0, 1.0))
    down = Vector((0.0, -1.0, 0.0))
    out = sag * 0.40 + span * 0.12
    
    p0 = pa + Vector((0.0, 0.0, 0.022))
    p1 = pa + forward * (out * 0.40) + down * 0.02 + Vector((0.0, 0.0, 0.02))
    p2 = mid + forward * out + down * (sag * 0.42)
    p3 = pb + forward * (out * 0.40) + down * 0.02 + Vector((0.0, 0.0, 0.02))
    p4 = pb + Vector((0.0, 0.0, 0.022))
    return [p0, p1, p2, p3, p4]


def build():
    reset()
    col_case = collection("01_Case")
    col_cables = collection("02_Cables")
    tex_dir = os.path.join(ROOT, "textures")

    # High-quality Eurorack materials
    M_CASE_METAL = mat("CaseAnodized", (0.020, 0.022, 0.028), rough=0.25, metal=0.92)
    M_CHEEK_WOOD = mat("CheekWood", (0.045, 0.026, 0.016), rough=0.38, metal=0.05)
    M_RAIL_SILVER = mat("RailSilver", (0.58, 0.62, 0.68), rough=0.22, metal=0.96)
    M_PANEL_BASE = mat("PanelBase", (0.018, 0.020, 0.024), rough=0.35, metal=0.50)
    
    M_KNOB_BODY = mat("KnobBody", (0.035, 0.038, 0.045), rough=0.28, metal=0.55)
    M_KNOB_SKIRT = mat("KnobSkirt", (0.12, 0.13, 0.15), rough=0.20, metal=0.85)
    M_KNOB_PTR = mat("KnobPointer", (0.95, 0.96, 0.98), rough=0.15, metal=0.10, emit=(1.0, 1.0, 1.0), emit_s=0.9)
    
    M_JACK_BEZEL = mat("JackBezel", (0.65, 0.68, 0.72), rough=0.18, metal=0.95)
    M_JACK_HOLE = mat("JackHole", (0.004, 0.005, 0.007), rough=0.90, metal=0.1)
    M_SCREW = mat("ScrewMetal", (0.38, 0.40, 0.44), rough=0.22, metal=0.92)
    M_TIP = mat("CableTip", (0.78, 0.80, 0.84), rough=0.16, metal=0.95)
    
    M_FADER_CAP = mat("FaderCapMat", (0.04, 0.045, 0.052), rough=0.26, metal=0.60)
    M_FADER_TRACK = mat("FaderTrackMat", (0.005, 0.006, 0.008), rough=0.80, metal=0.20)
    M_FADER_STEM = mat("FaderStemMat", (0.60, 0.62, 0.65), rough=0.20, metal=0.95)
    M_BEZEL_FRAME = mat("BezelFrameMat", (0.025, 0.028, 0.035), rough=0.30, metal=0.80)

    cables_m = [
        mat(f"CabMat_{i}", c, rough=0.45, metal=0.08, emit=c, emit_s=0.40)
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
    case_height = 0.11

    # 1. Main Eurorack Skiff Enclosure
    case_body = adopt(box("Case_Body", inner_w + 0.02, face_h + 0.03, case_height, (0.0, 0.0, -case_height * 0.5), col_case, M_CASE_METAL))
    bevel(case_body, 0.006, 3)

    # 2. American Walnut Side Cheeks
    cheek_thick = 0.024
    for i, x in enumerate((-(inner_w * 0.5 + cheek_thick * 0.5 + 0.008), inner_w * 0.5 + cheek_thick * 0.5 + 0.008)):
        ch = adopt(box(f"Case_Cheek_{i}", cheek_thick, face_h + 0.04, case_height + 0.02, (x, 0.0, -case_height * 0.45), col_case, M_CHEEK_WOOD))
        bevel(ch, 0.005, 3)

    # 3. Extruded Silver Mounting Rails
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

        face_w = mw - 0.004
        face_h_actual = face_h - 0.004
        w_tex = int((spec["hp"] / 8.0) * 640)

        # Module sub-panel backplate
        body = box(f"Module_{spec['id']}_Body", mw - 0.002, face_h, 0.008, (0, 0, -0.004), col_case, M_PANEL_BASE)
        body.parent = empty

        # High-resolution silkscreen textured faceplate
        tex = load_tex(os.path.join(tex_dir, f"panel_{spec['id']}.png"), f"Panel_{spec['id']}")
        if tex:
            face_m = tex_mat(f"FaceM_{spec['id']}", tex, emit=0.22, metal=0.55, rough=0.32)
        else:
            face_m = mat(f"FaceM_{spec['id']}", (0.025, 0.028, 0.035), 0.40, 0.4)
        
        face = hud_plane(f"Module_{spec['id']}_Face", face_w, face_h_actual, (0, 0, 0.001), (0, 0, 0), face_m, col_case)
        face.parent = empty

        accent = spec["accent"]
        accent_mat = mat(f"Accent_{spec['id']}", accent, 0.25, 0.1, emit=accent, emit_s=0.9)

        # 1. Knobs
        for ki, k in enumerate(spec.get("knobs", [])):
            x, y = uv_to_local(k["u"], k["v"], face_w, face_h_actual)
            is_large = (k.get("size") == "large")
            
            r_cap = 0.0155 if is_large else 0.0118
            h_cap = 0.0125 if is_large else 0.0105
            r_skirt = r_cap * 1.15
            
            # Stem bushing
            stem = cyl(f"KnobStem_{spec['id']}_{ki}", r_cap * 0.5, 0.004, (x, y, 0.002), col_case, M_CASE_METAL, verts=16)
            stem.parent = empty

            # Skirt base
            skirt = cyl(f"KnobSkirt_{spec['id']}_{ki}", r_skirt, 0.0018, (x, y, 0.0018), col_case, M_KNOB_SKIRT, verts=28)
            skirt.parent = empty

            # Accent color ring
            ring = cyl(f"KnobRing_{spec['id']}_{ki}", r_skirt * 1.04, 0.0012, (x, y, 0.0012), col_case, accent_mat, verts=28)
            ring.parent = empty

            # Main knurled cap body (origin at its center)
            cap = cyl(f"Knob_{spec['id']}_{ki}", r_cap, h_cap, (x, y, 0.0025 + h_cap * 0.5), col_case, M_KNOB_BODY, verts=32)
            cap.parent = empty
            smooth(cap)
            bevel(cap, 0.001, 2)
            
            # Initial rotation
            init_rot = (mi * 1.4 + ki * 0.9) % math.tau
            cap.rotation_euler.z = init_rot

            # Recessed glowing pointer (parented to cap)
            ptr_len = r_cap * 0.75
            pointer = box(f"KnobPtr_{spec['id']}_{ki}", 0.0018, ptr_len, 0.0025, (0.0, ptr_len * 0.45, h_cap * 0.5 + 0.001), col_case, M_KNOB_PTR)
            pointer.parent = cap

        # 2. Thonkiconn 3.5mm Jacks
        for ji, j in enumerate(spec.get("jacks", [])):
            x, y = uv_to_local(j["u"], j["v"], face_w, face_h_actual)
            is_out = (j.get("type") == "out")
            
            bezel = cyl(f"Jack_{spec['id']}_{ji}", 0.0078, 0.0040, (x, y, 0.0028), col_case, M_JACK_BEZEL, verts=6)
            bezel.parent = empty
            
            if is_out:
                washer = cyl(f"JackWasher_{spec['id']}_{ji}", 0.0092, 0.0012, (x, y, 0.0012), col_case, accent_mat, verts=20)
                washer.parent = empty

            hole = cyl(f"JackHole_{spec['id']}_{ji}", 0.0042, 0.0060, (x, y, 0.0020), col_case, M_JACK_HOLE, verts=16)
            hole.parent = empty
            
            jack_map[(spec["id"], ji)] = bezel

        # 3. LEDs
        for li, led_info in enumerate(spec.get("leds", [])):
            x, y = uv_to_local(led_info["u"], led_info["v"], face_w, face_h_actual)
            
            collar = cyl(f"LEDCollar_{spec['id']}_{li}", 0.0045, 0.0020, (x, y, 0.0018), col_case, M_JACK_BEZEL, verts=16)
            collar.parent = empty

            led_mat = mat(f"LEDMAT_{spec['id']}_{li}", accent, rough=0.15, metal=0.05, emit=accent, emit_s=1.8)
            led = cyl(f"LED_{spec['id']}_{li}", 0.0032, 0.0035, (x, y, 0.0030), col_case, led_mat, verts=16)
            led.parent = empty
            smooth(led)

        # 4. Faders (MIX)
        for fi, f in enumerate(spec.get("faders", [])):
            x, _ = uv_to_local(f["u"], 0.5, face_w, face_h_actual)
            _, y_top = uv_to_local(f["u"], f["v_top"], face_w, face_h_actual)
            _, y_bot = uv_to_local(f["u"], f["v_bot"], face_w, face_h_actual)
            
            y_mid = (y_top + y_bot) * 0.5
            slot_h = (y_top - y_bot)
            
            slot = box(f"FaderSlot_{spec['id']}_{fi}", 0.0035, slot_h, 0.0025, (x, y_mid, 0.0008), col_case, M_FADER_TRACK)
            slot.parent = empty

            cap_y = y_bot + slot_h * (0.35 + fi * 0.15)
            cap_h = 0.0065
            cap_z = 0.00125 + cap_h * 0.5
            
            cap = box(f"FaderCap_{spec['id']}_{fi}", 0.010, 0.016, cap_h, (x, cap_y, cap_z), col_case, M_FADER_CAP)
            cap.parent = empty
            bevel(cap, 0.0012, 2)
            
            stem = box(f"FaderStem_{spec['id']}_{fi}", 0.0016, 0.0030, 0.0045, (0.0, 0.0, -cap_h * 0.5), col_case, M_FADER_STEM)
            stem.parent = cap

            fader_ptr = box(f"FaderPtr_{spec['id']}_{fi}", 0.0085, 0.0015, 0.0008, (0.0, 0.0, cap_h * 0.5 + 0.0002), col_case, M_KNOB_PTR)
            fader_ptr.parent = cap

        # 5. OLED Display Screens (Raised in front of bezel frame)
        s_info = spec.get("screen")
        if s_info:
            kind = s_info["kind"]
            if screens.get(kind):
                sx = s_info["w"] * face_w
                sy = s_info["h"] * face_h_actual
                x, y = uv_to_local(s_info["u"], s_info["v"], face_w, face_h_actual)

                # Outer protective bezel frame
                frame = box(f"ScreenFrame_{spec['id']}", sx + 0.006, sy + 0.006, 0.0018, (x, y, 0.0014), col_case, M_BEZEL_FRAME)
                frame.parent = empty
                bevel(frame, 0.0012, 2)

                # Active OLED screen surface
                sm = hud_mat(f"ScreenM_{spec['id']}", screens[kind], accent, strength=2.8)
                scr = hud_plane(f"Screen_{spec['id']}", sx, sy, (x, y, 0.0028), (0, 0, 0), sm, col_case)
                scr.parent = empty

        # 6. M3 Corner Screws
        u_scw_l = 34.0 / w_tex
        u_scw_r = 1.0 - u_scw_l
        v_scw_t = 1.0 - (48.0 / 2048.0)
        v_scw_b = 48.0 / 2048.0
        
        for scw_u, scw_v in ((u_scw_l, v_scw_t), (u_scw_r, v_scw_t), (u_scw_l, v_scw_b), (u_scw_r, v_scw_b)):
            sx, sy = uv_to_local(scw_u, scw_v, face_w, face_h_actual)
            scw = cyl(f"Screw_{spec['id']}_{sx:.3f}_{sy:.3f}", 0.0038, 0.0022, (sx, sy, 0.0018), col_case, M_SCREW, verts=12)
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
        
        for pi, (pt, p_name) in enumerate([(pa, "A"), (pb, "B")]):
            tip = cyl(f"Tip_{ci}_{p_name}", radius * 1.3, 0.014, pt + Vector((0, 0, 0.008)), col_cables, M_TIP, verts=16)
            tip.parent = root
            sleeve = cyl(f"Sleeve_{ci}_{p_name}", radius * 1.55, 0.012, pt + Vector((0, 0, 0.018)), col_cables, cm, verts=16)
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
