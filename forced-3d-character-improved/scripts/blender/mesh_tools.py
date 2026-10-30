"""Small Blender adapter for validated geometry_core mesh arrays."""
from __future__ import annotations

import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry_core import validate_mesh_data  # noqa: E402


def create_mesh_object(
    name,
    vertices,
    faces,
    material=None,
    *,
    part="detail",
    collection=None,
):
    validate_mesh_data(vertices, faces, name=name)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    if mesh.validate(verbose=True, clean_customdata=True):
        bpy.data.meshes.remove(mesh)
        raise ValueError(f"{name} was modified by Mesh.validate; source data rejected")
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    (collection or bpy.context.scene.collection).objects.link(obj)
    obj["character_part"] = str(part)
    obj["geometry_source"] = "deterministic_mesh_arrays"
    if material is not None:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    return obj


def create_ico_object(name, center, radii, material, *, subdivisions=2, part="detail"):
    """Low-resolution ellipsoid for small organic details, not whole characters."""
    bm = bmesh.new()
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=int(subdivisions), radius=1.0)
        for vertex in bm.verts:
            vertex.co.x *= radii[0]
            vertex.co.y *= radii[1]
            vertex.co.z *= radii[2]
            vertex.co.x += center[0]
            vertex.co.y += center[1]
            vertex.co.z += center[2]
        bm.normal_update()
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        bm.to_mesh(mesh)
        mesh.update(calc_edges=True)
    finally:
        bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj["character_part"] = str(part)
    obj["geometry_source"] = "bmesh_icosphere"
    if material is not None:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    return obj


def srgb_channel_to_linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def color_from_hex(value):
    text = value.lstrip("#")
    if len(text) != 6:
        raise ValueError(f"Expected six-digit RGB hex colour, got {value!r}")
    rgb = [int(text[index:index + 2], 16) / 255.0 for index in (0, 2, 4)]
    return tuple(srgb_channel_to_linear(channel) for channel in rgb) + (1.0,)


def make_material(name, hex_color, *, roughness=0.72, metallic=0.0, specular=0.28):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    rgba = color_from_hex(hex_color)
    material.diffuse_color = rgba
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in shader.inputs:
        shader.inputs["Specular IOR Level"].default_value = specular
    return material


def add_bevel(obj, width=0.003, segments=1):
    modifier = obj.modifiers.new("Tailored edge highlights", "BEVEL")
    modifier.width = float(width)
    modifier.segments = int(segments)
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = 0.35
    return modifier
