"""
Blender 5.2 Cycles Script: High-End Studio Render of Fusion 360 Eurorack Model
=============================================================================
- Accurate material classification for 549 CAD objects
- Texture-mapped faceplate silkscreens (CLK, VCO, FLT, ENV, LFO, RND, MIX, VIS)
- Glowing active OLED screens (oscilloscope, spectrum analyzer, step sequencer)
- Procedural rich dark walnut wood shader with bump grain
- Brushed black anodized aluminum skiff
- Polished chrome 3.5mm jacks and fader stems
- Three-point cinematic studio lighting
"""

import bpy
import math
import os
from mathutils import Vector, Euler

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(ROOT, "textures")
OUT_DIR = os.path.join(ROOT, "renders")
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Reset scene & setup Cycles GPU
bpy.ops.wm.read_homefile(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440
scene.render.film_transparent = False

try:
    scene.cycles.denoiser = 'OPTIX'
except Exception:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# Configure GPU
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    cprefs = prefs.preferences
    backend = next((b for b in ('OPTIX', 'CUDA') if b in [t[0] for t in cprefs.get_device_types(bpy.context)]), None)
    if backend:
        cprefs.compute_device_type = backend
        cprefs.get_devices()
        for d in cprefs.devices:
            d.use = (d.type == backend)

# 2. Import GLB converted from STEP
glb_path = os.path.join(ROOT, "fusion_separated.glb")
bpy.ops.import_scene.gltf(filepath=glb_path)

# Separate into loose bodies
main_obj = bpy.data.objects[0]
bpy.context.view_layer.objects.active = main_obj
main_obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

all_objs = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) > 0]
print(f"Total CAD solid bodies: {len(all_objs)}")

# 3. Create Shader Materials
def make_principled(name, color, metallic=0.0, roughness=0.4, clearcoat=0.0, emission_color=(0,0,0,1), emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = clearcoat
    elif 'Clearcoat' in bsdf.inputs:
        bsdf.inputs['Clearcoat'].default_value = clearcoat
    if emission_strength > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def make_texture_material(name, tex_path, emission_tex=False):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_node = nodes.new(type='ShaderNodeTexImage')
    if os.path.exists(tex_path):
        tex_node.image = bpy.data.images.load(tex_path)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.5
    bsdf.inputs['Roughness'].default_value = 0.4
    
    mat.node_tree.links.new(tex_coord.outputs['Generated'], tex_node.inputs['Vector'])
    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    
    if emission_tex:
        bsdf.inputs['Emission Strength'].default_value = 3.5
        mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
        
    out = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def make_walnut_wood():
    mat = bpy.data.materials.new(name="CAD_Walnut_Procedural")
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (2.0, 15.0, 2.0)
    
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 12.0
    wave.inputs['Distortion'].default_value = 4.5
    wave.inputs['Detail'].default_value = 3.0
    
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (0.08, 0.04, 0.015, 1.0) # Deep rich walnut brown
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.18, 0.10, 0.045, 1.0) # Warm caramel wood grain
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.002
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.38
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.25
        
    out = nodes.new(type='ShaderNodeOutputMaterial')
    
    mat.node_tree.links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    mat.node_tree.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    mat.node_tree.links.new(wave.outputs['Color'], ramp.inputs['Fac'])
    mat.node_tree.links.new(wave.outputs['Fac'], bump.inputs['Height'])
    mat.node_tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    mat.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mat_walnut = make_walnut_wood()
mat_chassis = make_principled("CAD_Aluminum_Case", (0.025, 0.025, 0.028, 1.0), metallic=0.88, roughness=0.32)
mat_bezel = make_principled("CAD_Screen_Bezel", (0.015, 0.015, 0.018, 1.0), metallic=0.9, roughness=0.25)
mat_knob = make_principled("CAD_Knob_Matte", (0.02, 0.02, 0.022, 1.0), metallic=0.35, roughness=0.45)
mat_pointer = make_principled("CAD_Pointer_White", (1.0, 1.0, 1.0, 1.0), metallic=0.0, roughness=0.1, emission_color=(1,1,1,1), emission_strength=0.8)
mat_chrome = make_principled("CAD_Chrome_Polished", (0.92, 0.92, 0.95, 1.0), metallic=0.98, roughness=0.10)
mat_fader_cap = make_principled("CAD_Fader_Cap", (0.015, 0.015, 0.018, 1.0), metallic=0.25, roughness=0.38)

# Panel materials
mat_panels = {
    "CLK": make_texture_material("CAD_Panel_CLK", os.path.join(TEX_DIR, "panel_CLK.png")),
    "VCO": make_texture_material("CAD_Panel_VCO", os.path.join(TEX_DIR, "panel_VCO.png")),
    "FLT": make_texture_material("CAD_Panel_FLT", os.path.join(TEX_DIR, "panel_FLT.png")),
    "ENV": make_texture_material("CAD_Panel_ENV", os.path.join(TEX_DIR, "panel_ENV.png")),
    "LFO": make_texture_material("CAD_Panel_LFO", os.path.join(TEX_DIR, "panel_LFO.png")),
    "RND": make_texture_material("CAD_Panel_RND", os.path.join(TEX_DIR, "panel_RND.png")),
    "MIX": make_texture_material("CAD_Panel_MIX", os.path.join(TEX_DIR, "panel_MIX.png")),
    "VIS": make_texture_material("CAD_Panel_VIS", os.path.join(TEX_DIR, "panel_VIS.png")),
}

# Screen materials
mat_screen_clk = make_texture_material("CAD_Screen_CLK", os.path.join(TEX_DIR, "screen_steps.png"), emission_tex=True)
mat_screen_vco = make_texture_material("CAD_Screen_VCO", os.path.join(TEX_DIR, "screen_wave.png"), emission_tex=True)
mat_screen_vis = make_texture_material("CAD_Screen_VIS", os.path.join(TEX_DIR, "screen_spec.png"), emission_tex=True)

# 4. Accurate Solid Body Classification & Material Assignment
MODULE_BOUNDS = [
    ("CLK", -0.01, 0.0508),
    ("VCO", 0.0508, 0.0914),
    ("FLT", 0.0914, 0.1321),
    ("ENV", 0.1321, 0.1727),
    ("LFO", 0.1727, 0.2032),
    ("RND", 0.2032, 0.2438),
    ("MIX", 0.2438, 0.2845),
    ("VIS", 0.2845, 0.3550),
]

for o in all_objs:
    o.data.materials.clear()
    verts = [v.co for v in o.data.vertices]
    bx_min = min(v.x for v in verts)
    bx_max = max(v.x for v in verts)
    by_min = min(v.y for v in verts)
    by_max = max(v.y for v in verts)
    bz_min = min(v.z for v in verts)
    bz_max = max(v.z for v in verts)
    
    dx = bx_max - bx_min
    dy = by_max - by_min
    dz = bz_max - bz_min
    cx = (bx_min + bx_max) * 0.5
    cy = (by_min + by_max) * 0.5
    cz = (bz_min + bz_max) * 0.5
    
    # 1. Walnut Cheeks
    if (cx < -0.002 or cx > 0.347) and dz > 0.12:
        o.data.materials.append(mat_walnut)
    # 2. Main Skiff Chassis
    elif dx > 0.30 and dz > 0.10 and by_min < -0.04:
        o.data.materials.append(mat_chassis)
    # 3. Pointer Inlays (thin white lines on top of knobs/faders)
    elif (dx < 0.0015 or dy < 0.0015 or (dx < 0.006 and dy < 0.002)) and by_max > 0.012:
        o.data.materials.append(mat_pointer)
    # 4. OLED Screens (inner glass planes)
    elif dx > 0.024 and dz > 0.015 and by_max > 0.002 and by_max < 0.008 and cz > 0.07:
        if cx < 0.06:
            o.data.materials.append(mat_screen_clk)
        elif cx < 0.10:
            o.data.materials.append(mat_screen_vco)
        else:
            o.data.materials.append(mat_screen_vis)
    # 5. Screen Bezel Frames
    elif dx > 0.028 and dz > 0.018 and by_max >= 0.003 and cz > 0.07:
        o.data.materials.append(mat_bezel)
    # 6. Jacks (Hex nuts & center holes)
    elif dx < 0.010 and dz < 0.010 and cz < 0.040:
        o.data.materials.append(mat_chrome)
    # 7. Slider Stems
    elif dx < 0.003 and dz < 0.003 and cz > 0.035 and cz < 0.075:
        o.data.materials.append(mat_chrome)
    # 8. Fader Caps
    elif dx < 0.012 and dz > 0.006 and dz < 0.015 and cz > 0.035 and cz < 0.075 and by_max > 0.006:
        o.data.materials.append(mat_fader_cap)
    # 9. Potentiometer Knobs
    elif dx > 0.009 and dx < 0.022 and dz > 0.009 and dz < 0.022 and by_max > 0.010:
        o.data.materials.append(mat_knob)
    # 10. Faceplate Panels
    elif dz > 0.120 and dx > 0.025 and dx < 0.060:
        # Find corresponding module
        assigned = False
        for mod_id, m_start, m_end in MODULE_BOUNDS:
            if cx >= m_start and cx <= m_end:
                o.data.materials.append(mat_panels[mod_id])
                assigned = True
                break
        if not assigned:
            o.data.materials.append(mat_chassis)
    else:
        o.data.materials.append(mat_chassis)

# 5. Studio Environment & Lighting
world = bpy.data.worlds.new("CAD_Studio_Lighting")
scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wnodes.clear()

wbg = wnodes.new(type='ShaderNodeBackground')
wbg.inputs['Color'].default_value = (0.008, 0.014, 0.020, 1.0) # Deep midnight slate
wbg.inputs['Strength'].default_value = 0.5
wout = wnodes.new(type='ShaderNodeOutputWorld')
world.node_tree.links.new(wbg.outputs['Background'], wout.inputs['Surface'])

# Center point of the synthesizer
target = Vector((0.172, 0.0, 0.064))

# Key Light (Top-Left 45 deg Warm Studio Softbox)
key_data = bpy.data.lights.new(name="Studio_Key", type='AREA')
key_data.energy = 95.0
key_data.color = (1.0, 0.97, 0.92)
key_data.size = 0.9
key_obj = bpy.data.objects.new(name="Studio_Key", object_data=key_data)
key_obj.location = (target.x - 0.30, -0.45, target.z + 0.40)
key_obj.rotation_euler = Euler((math.radians(50), math.radians(10), math.radians(-32)), 'XYZ')
scene.collection.objects.link(key_obj)

# Rim / Edge Accent Light (Crisp Cyan on wood & metallic edges)
rim_data = bpy.data.lights.new(name="Studio_Rim", type='AREA')
rim_data.energy = 130.0
rim_data.color = (0.25, 0.88, 1.0)
rim_data.size = 0.7
rim_obj = bpy.data.objects.new(name="Studio_Rim", object_data=rim_data)
rim_obj.location = (target.x + 0.40, 0.25, target.z + 0.15)
rim_obj.rotation_euler = Euler((math.radians(-30), math.radians(-20), math.radians(115)), 'XYZ')
scene.collection.objects.link(rim_obj)

# Top Softbox Fill
fill_data = bpy.data.lights.new(name="Studio_TopFill", type='AREA')
fill_data.energy = 40.0
fill_data.color = (0.94, 0.96, 1.0)
fill_data.size = 1.4
fill_obj = bpy.data.objects.new(name="Studio_TopFill", object_data=fill_data)
fill_obj.location = (target.x, -0.10, target.z + 0.55)
fill_obj.rotation_euler = Euler((math.radians(15), 0, 0), 'XYZ')
scene.collection.objects.link(fill_obj)

# Ground Shadow Catcher / Table Surface
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(target.x, 0.0, -0.015))
ground = bpy.context.active_object
ground.name = "Studio_Ground"
gmat = make_principled("Ground_Dark", (0.005, 0.008, 0.012, 1.0), metallic=0.2, roughness=0.6)
ground.data.materials.append(gmat)

# 6. Camera Rig & Rendering
cam_data = bpy.data.cameras.new(name="StudioCamera")
cam_data.sensor_width = 36.0
cam_obj = bpy.data.objects.new(name="StudioCamera", object_data=cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Shot 1: Perspective Beauty Hero Shot (3/4 Studio View)
cam_data.lens = 70.0
cam_obj.location = (target.x + 0.10, -0.62, target.z + 0.32)
cam_obj.rotation_euler = Euler((math.radians(64), 0, math.radians(11)), 'XYZ')

out_persp = os.path.join(OUT_DIR, "render_fusion_perspective.png")
scene.render.filepath = out_persp
print(f"Rendering Shot 1: {out_persp} ...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_persp}")

# Shot 2: Front Ortho / Macro Hero Shot
cam_data.lens = 85.0
cam_obj.location = (target.x, -0.75, target.z + 0.02)
cam_obj.rotation_euler = Euler((math.radians(88), 0, 0), 'XYZ')

out_front = os.path.join(OUT_DIR, "render_fusion_front.png")
scene.render.filepath = out_front
print(f"Rendering Shot 2: {out_front} ...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_front}")

# Shot 3: Macro Close-up on CLK, VCO & Filter
cam_data.lens = 110.0
cam_obj.location = (target.x - 0.08, -0.32, target.z + 0.14)
cam_obj.rotation_euler = Euler((math.radians(58), 0, math.radians(-16)), 'XYZ')

out_macro = os.path.join(OUT_DIR, "render_fusion_macro.png")
scene.render.filepath = out_macro
print(f"Rendering Shot 3: {out_macro} ...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_macro}")

# Save master .blend file
blend_out = os.path.join(ROOT, "fusion_modular_master.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"Master Blender file saved: {blend_out}")
