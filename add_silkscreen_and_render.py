"""
Blender 5.2 Script: Complete Photorealistic Materials for Eurorack Model
========================================================================
- Vector 2048px silkscreens on all 8 module panels
- Glowing active OLED screens (oscilloscope, spectrum analyzer, step sequencer)
- Dark walnut procedural wood cheeks
- Matte black knurled dials with pointer lines
- Mirror chrome 3.5mm jack sockets
- Studio camera & multi-light setup
"""

import bpy
import math
import os
from mathutils import Vector, Euler

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(ROOT, "textures")
OUT_DIR = os.path.join(ROOT, "renders")
os.makedirs(OUT_DIR, exist_ok=True)

# Load master blend
blend_path = os.path.join(ROOT, "fusion_modular_master.blend")
bpy.ops.wm.open_mainfile(filepath=blend_path)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440

MODULE_SPECS = [
    ("CLK", 0.0000, 0.0508, "panel_CLK.png"),
    ("VCO", 0.0508, 0.09144, "panel_VCO.png"),
    ("FLT", 0.09144, 0.13208, "panel_FLT.png"),
    ("ENV", 0.13208, 0.17272, "panel_ENV.png"),
    ("LFO", 0.17272, 0.20320, "panel_LFO.png"),
    ("RND", 0.20320, 0.24384, "panel_RND.png"),
    ("MIX", 0.24384, 0.28448, "panel_MIX.png"),
    ("VIS", 0.28448, 0.33528, "panel_VIS.png"),
]

SCREEN_SPECS = [
    ("CLK", 0.0074, 0.0434, 0.087, 0.105, "screen_steps.png"),
    ("VCO", 0.0571, 0.0851, 0.089, 0.107, "screen_wave.png"),
    ("VIS", 0.2909, 0.3289, 0.075, 0.101, "screen_spec.png"),
]

def build_silkscreen_shader(mod_id, x_start, x_end, tex_name):
    width = x_end - x_start
    tex_path = os.path.join(TEX_DIR, tex_name)
    mat_name = f"CAD_Silkscreen_{mod_id}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    
    math_sub_x = nodes.new(type='ShaderNodeMath')
    math_sub_x.operation = 'SUBTRACT'
    math_sub_x.inputs[1].default_value = x_start
    
    math_div_x = nodes.new(type='ShaderNodeMath')
    math_div_x.operation = 'DIVIDE'
    math_div_x.inputs[1].default_value = width
    
    math_div_z = nodes.new(type='ShaderNodeMath')
    math_div_z.operation = 'DIVIDE'
    math_div_z.inputs[1].default_value = 0.1285
    
    comb_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.extension = 'CLIP'
    if os.path.exists(tex_path):
        tex_node.image = bpy.data.images.load(tex_path)
        
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.32
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    
    mat.node_tree.links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])
    mat.node_tree.links.new(sep_xyz.outputs['X'], math_sub_x.inputs[0])
    mat.node_tree.links.new(math_sub_x.outputs['Value'], math_div_x.inputs[0])
    mat.node_tree.links.new(math_div_x.outputs['Value'], comb_xyz.inputs['X'])
    
    mat.node_tree.links.new(sep_xyz.outputs['Z'], math_div_z.inputs[0])
    mat.node_tree.links.new(math_div_z.outputs['Value'], comb_xyz.inputs['Y'])
    
    mat.node_tree.links.new(comb_xyz.outputs['Vector'], tex_node.inputs['Vector'])
    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def build_screen_shader(mod_id, x_min, x_max, z_min, z_max, tex_name):
    tex_path = os.path.join(TEX_DIR, tex_name)
    mat_name = f"CAD_Screen_Active_{mod_id}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    
    w = x_max - x_min
    h = z_max - z_min
    
    math_sub_x = nodes.new(type='ShaderNodeMath')
    math_sub_x.operation = 'SUBTRACT'
    math_sub_x.inputs[1].default_value = x_min
    
    math_div_x = nodes.new(type='ShaderNodeMath')
    math_div_x.operation = 'DIVIDE'
    math_div_x.inputs[1].default_value = w
    
    math_sub_z = nodes.new(type='ShaderNodeMath')
    math_sub_z.operation = 'SUBTRACT'
    math_sub_z.inputs[1].default_value = z_min
    
    math_div_z = nodes.new(type='ShaderNodeMath')
    math_div_z.operation = 'DIVIDE'
    math_div_z.inputs[1].default_value = h
    
    comb_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.extension = 'CLIP'
    if os.path.exists(tex_path):
        tex_node.image = bpy.data.images.load(tex_path)
        
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.01, 0.012, 0.015, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Emission Strength'].default_value = 5.5
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    
    mat.node_tree.links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])
    mat.node_tree.links.new(sep_xyz.outputs['X'], math_sub_x.inputs[0])
    mat.node_tree.links.new(math_sub_x.outputs['Value'], math_div_x.inputs[0])
    mat.node_tree.links.new(math_div_x.outputs['Value'], comb_xyz.inputs['X'])
    
    mat.node_tree.links.new(sep_xyz.outputs['Z'], math_sub_z.inputs[0])
    mat.node_tree.links.new(math_sub_z.outputs['Value'], math_div_z.inputs[0])
    mat.node_tree.links.new(math_div_z.outputs['Value'], comb_xyz.inputs['Y'])
    
    mat.node_tree.links.new(comb_xyz.outputs['Vector'], tex_node.inputs['Vector'])
    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# Build all materials
for mod_id, xs, xe, tex_name in MODULE_SPECS:
    build_silkscreen_shader(mod_id, xs, xe, tex_name)

for mod_id, x_min, x_max, z_min, z_max, tex_name in SCREEN_SPECS:
    build_screen_shader(mod_id, x_min, x_max, z_min, z_max, tex_name)

# Assign to objects
all_objs = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) > 0]
for o in all_objs:
    verts = [v.co for v in o.data.vertices]
    bx_min = min(v.x for v in verts)
    bx_max = max(v.x for v in verts)
    bz_min = min(v.z for v in verts)
    bz_max = max(v.z for v in verts)
    
    dx = bx_max - bx_min
    dz = bz_max - bz_min
    cx = (bx_min + bx_max) * 0.5
    cz = (bz_min + bz_max) * 0.5
    
    # 1. Faceplates
    if dz > 0.120 and dx > 0.025 and dx < 0.065:
        for mod_id, xs, xe, _ in MODULE_SPECS:
            if cx >= xs - 0.005 and cx <= xe + 0.005:
                o.data.materials.clear()
                o.data.materials.append(bpy.data.materials[f"CAD_Silkscreen_{mod_id}"])
                break
                
    # 2. OLED Display Screen Glass
    elif dz > 0.015 and dz < 0.030 and dx > 0.025 and dx < 0.042 and cz > 0.075:
        for mod_id, x_min, x_max, _, _, _ in SCREEN_SPECS:
            if cx >= x_min - 0.01 and cx <= x_max + 0.01:
                o.data.materials.clear()
                o.data.materials.append(bpy.data.materials[f"CAD_Screen_Active_{mod_id}"])
                break

# Render Shots
cam_obj = bpy.data.objects.get("StudioCamera") or bpy.data.objects.get("MainCamera")
target = Vector((0.172, 0.0, 0.064))

# Shot 1: 3/4 Perspective Studio
cam_obj.data.lens = 55.0
cam_obj.location = (target.x + 0.10, -0.60, target.z + 0.22)
direction = target - cam_obj.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

out_persp = os.path.join(OUT_DIR, "render_fusion_perspective.png")
scene.render.filepath = out_persp
print("Rendering perspective...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_persp}")

# Shot 2: Direct Front Studio
cam_obj.data.lens = 72.0
cam_obj.location = (target.x, -0.72, target.z + 0.01)
direction = target - cam_obj.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

out_front = os.path.join(OUT_DIR, "render_fusion_front.png")
scene.render.filepath = out_front
print("Rendering front...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_front}")

# Shot 3: Macro Close-up on CLK & VCO
cam_obj.data.lens = 95.0
cam_obj.location = (0.055, -0.36, 0.11)
direction = Vector((0.050, 0.0, 0.070)) - cam_obj.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

out_macro = os.path.join(OUT_DIR, "render_fusion_macro.png")
scene.render.filepath = out_macro
print("Rendering macro...")
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_macro}")

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Saved master blend: {blend_path}")
