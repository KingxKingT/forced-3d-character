"""Generate a stylized low-poly humanoid with Blender's Python API.

Run:
  blender --background --factory-startup --python scripts/blender/create_character.py -- \
    --config examples/dark_suit_purple_eyes.json --outdir build/character \
    --formats glb fbx obj --render-views
"""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--formats", nargs="+", choices=("glb", "gltf", "fbx", "obj"))
    parser.add_argument("--render-views", action="store_true", help="Render front, side, and back PNG previews")
    parser.add_argument("--no-render", action="store_true", help="Do not render preview images")
    return parser.parse_args(argv)


def hex_rgb(value, fallback="#808080"):
    value = value if isinstance(value, str) and HEX.fullmatch(value) else fallback
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def make_material(name, hex_color, metallic=0.0, roughness=0.72):
    rgb = hex_rgb(hex_color)
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def assign_mat(obj, material):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(material)
    return obj


def finish_mesh(obj, name, material, bevel=0.0):
    obj.name = name
    assign_mat(obj, material)
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
    if bevel > 0:
        mod = obj.modifiers.new(name="small_edge_bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = "ANGLE"
    return obj


def add_cube(name, location, dimensions, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, name, material, bevel)


def add_ico(name, location, dimensions, material, subdivisions=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, name, material)


def add_segment(name, start, end, radius_start, radius_end, material, vertices=8):
    start_v, end_v = Vector(start), Vector(end)
    direction = end_v - start_v
    length = direction.length
    if length < 1e-5:
        raise ValueError(f"Segment {name} has zero length")
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius_start, radius2=radius_end,
                                    depth=length, end_fill_type="NGON", location=(start_v + end_v) / 2)
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    return finish_mesh(obj, name, material)


def add_prism(name, points_xz, y_front, y_back, material):
    """Create a shallow prism from a polygon in X/Z, with its front toward +Y."""
    count = len(points_xz)
    verts = [(x, y_front, z) for x, z in points_xz] + [(x, y_back, z) for x, z in points_xz]
    faces = [tuple(range(count)), tuple(range(count, count * 2))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish_mesh(obj, name, material)


def add_hair(material, style="side_swept"):
    # Main hair cap plus separate low-poly locks to create a deliberate silhouette.
    add_ico("Hair_Cap", (0, -0.005, 1.835), (0.255, 0.208, 0.115), material, 2)
    if style == "short":
        add_ico("Hair_Crown", (0, 0.015, 1.86), (0.235, 0.19, 0.07), material, 1)
        return
    add_ico("Hair_Lock_Left", (-0.075, 0.095, 1.865), (0.15, 0.095, 0.065), material, 1)
    add_ico("Hair_Lock_Center", (0.025, 0.112, 1.88), (0.17, 0.085, 0.060), material, 1)
    add_ico("Hair_Lock_Right", (0.105, 0.065, 1.855), (0.105, 0.095, 0.055), material, 1)
    # A slim sideburn on each side, kept symmetrical.
    for sign, side in ((-1, "L"), (1, "R")):
        add_cube(f"Hair_Sideburn_{side}", (sign * 0.119, 0.055, 1.745), (0.035, 0.09, 0.105), material, 0.012)


def build_character(cfg):
    palette = cfg.get("palette", {})
    features = cfg.get("features", {})
    outfit = cfg.get("outfit", {})
    mats = {
        "skin": make_material("MAT_Skin", palette.get("skin", "#C98F73"), roughness=0.82),
        "hair": make_material("MAT_Hair", palette.get("hair", "#111116"), roughness=0.6),
        "suit": make_material("MAT_Suit", palette.get("suit", "#171622"), roughness=0.86),
        "shirt": make_material("MAT_Shirt", palette.get("shirt", "#E9E5EE"), roughness=0.88),
        "tie": make_material("MAT_Tie", palette.get("tie", "#6B42A0"), roughness=0.7),
        "eyes": make_material("MAT_Eyes", features.get("eye_color", palette.get("eyes", "#8A57E8")), metallic=0.12, roughness=0.28),
        "eyewhite": make_material("MAT_EyeWhite", palette.get("eyewhite", "#F6F2F7"), roughness=0.35),
        "shoe": make_material("MAT_Shoes", palette.get("shoe", "#100F15"), roughness=0.65),
        "gold": make_material("MAT_Gold_Details", palette.get("gold", "#C5A253"), metallic=0.62, roughness=0.34),
        "mouth": make_material("MAT_Mouth", "#7C3E4C", roughness=0.8),
    }

    # Shoes, trouser legs, and tailored jacket. Character faces +Y.
    for sign, side in ((-1, "L"), (1, "R")):
        add_cube(f"Shoe_{side}", (sign * 0.105, 0.045, 0.085), (0.17, 0.285, 0.12), mats["shoe"], 0.035)
        add_cube(f"Sole_{side}", (sign * 0.105, 0.052, 0.037), (0.175, 0.29, 0.035), mats["gold"], 0.008)
        # Lower leg and thigh are separate tapered forms for a readable trouser break.
        add_segment(f"Trouser_Shin_{side}", (sign * 0.105, 0.015, 0.14), (sign * 0.11, 0.0, 0.61), 0.073, 0.093, mats["suit"], 8)
        add_segment(f"Trouser_Thigh_{side}", (sign * 0.11, 0.0, 0.58), (sign * 0.105, 0.0, 0.98), 0.095, 0.13, mats["suit"], 8)
        # Subtle cuff break above each shoe.
        add_cube(f"Trouser_Cuff_{side}", (sign * 0.105, 0.0, 0.16), (0.148, 0.17, 0.055), mats["suit"], 0.012)

    add_cube("Pelvis_Jacket", (0, 0, 1.00), (0.39, 0.225, 0.28), mats["suit"], 0.045)
    add_cube("Jacket_Torso", (0, 0, 1.29), (0.48, 0.245, 0.48), mats["suit"], 0.055)
    # Shirt inset and pointed collar.
    if outfit.get("shirt", True):
        add_cube("Shirt_Front", (0, 0.127, 1.29), (0.145, 0.027, 0.39), mats["shirt"], 0.012)
        add_prism("Collar_Left", [(-0.09, 1.47), (-0.018, 1.435), (-0.045, 1.36), (-0.12, 1.43)], 0.154, 0.135, mats["shirt"])
        add_prism("Collar_Right", [(0.09, 1.47), (0.018, 1.435), (0.045, 1.36), (0.12, 1.43)], 0.154, 0.135, mats["shirt"])
    # Lapels have slightly different silhouettes so the front reads as a jacket rather than a box.
    if outfit.get("lapels", True):
        add_prism("Lapel_Left", [(-0.22, 1.49), (-0.115, 1.47), (-0.015, 1.25), (-0.10, 1.34)], 0.143, 0.119, mats["suit"])
        add_prism("Lapel_Right", [(0.22, 1.49), (0.115, 1.47), (0.015, 1.25), (0.10, 1.34)], 0.143, 0.119, mats["suit"])
    if outfit.get("tie", True):
        add_prism("Tie_Knot", [(-0.035, 1.445), (0.035, 1.445), (0.028, 1.395), (-0.028, 1.395)], 0.164, 0.148, mats["tie"])
        add_prism("Tie_Body", [(-0.027, 1.40), (0.027, 1.40), (0.055, 1.18), (0, 1.145), (-0.055, 1.18)], 0.162, 0.145, mats["tie"])
    # Pocket square and buttons on front surface.
    if features.get("pocket_square", True):
        add_prism("Pocket_Square", [(0.125, 1.40), (0.195, 1.40), (0.19, 1.35), (0.135, 1.355)], 0.151, 0.139, mats["shirt"])
    if features.get("gold_buttons", True):
        for z in (1.25, 1.16, 1.07):
            add_ico(f"Jacket_Button_{z:.2f}", (0.055, 0.151, z), (0.024, 0.013, 0.024), mats["gold"], 1)

    # Neck and stylized head.
    add_cube("Neck", (0, 0.005, 1.55), (0.105, 0.12, 0.17), mats["skin"], 0.018)
    add_ico("Head", (0, 0.005, 1.705), (0.245, 0.205, 0.30), mats["skin"], 2)
    if features.get("ears", True):
        for sign, side in ((-1, "L"), (1, "R")):
            add_ico(f"Ear_{side}", (sign * 0.128, 0.008, 1.70), (0.048, 0.065, 0.085), mats["skin"], 1)
    # Eye whites and irises are placed on the +Y-facing surface.
    for sign, side in ((-1, "L"), (1, "R")):
        add_ico(f"Eye_White_{side}", (sign * 0.055, 0.100, 1.727), (0.047, 0.026, 0.030), mats["eyewhite"], 2)
        add_ico(f"Iris_{side}", (sign * 0.055, 0.121, 1.726), (0.024, 0.012, 0.025), mats["eyes"], 2)
        add_ico(f"Pupil_{side}", (sign * 0.055, 0.131, 1.726), (0.010, 0.007, 0.015), mats["hair"], 1)
        if features.get("eyebrows", True):
            brow = add_cube(f"Eyebrow_{side}", (sign * 0.055, 0.111, 1.768), (0.072, 0.022, 0.018), mats["hair"], 0.006)
            brow.rotation_euler[1] = sign * math.radians(-6)
    if features.get("nose", True):
        add_ico("Nose", (0, 0.115, 1.687), (0.036, 0.045, 0.061), mats["skin"], 1)
    if features.get("mouth", True):
        add_cube("Mouth", (0, 0.105, 1.638), (0.060, 0.012, 0.009), mats["mouth"], 0.004)
    add_hair(mats["hair"], features.get("hair_style", "side_swept"))
    if features.get("beard", False):
        add_ico("Beard_Chin", (0, 0.083, 1.60), (0.16, 0.08, 0.075), mats["hair"], 1)

    # Arms are built as slightly tapered connected sleeve sections in a T-pose.
    for sign, side in ((-1, "L"), (1, "R")):
        shoulder = (sign * 0.235, 0, 1.435)
        elbow = (sign * 0.515, 0, 1.425)
        wrist = (sign * 0.805, 0.006, 1.410)
        add_ico(f"Shoulder_{side}", shoulder, (0.22, 0.24, 0.22), mats["suit"], 1)
        add_segment(f"Sleeve_Upper_{side}", shoulder, elbow, 0.105, 0.086, mats["suit"], 8)
        add_segment(f"Sleeve_Forearm_{side}", elbow, wrist, 0.086, 0.066, mats["suit"], 8)
        if outfit.get("cuffs", True):
            cuff_end = (sign * 0.823, 0.006, 1.41)
            add_segment(f"Cuff_{side}", (sign * 0.792, 0.006, 1.411), cuff_end, 0.069, 0.064, mats["shirt"], 8)
        # Palm is broad enough to read; individual fingers remain separated.
        palm_center = (sign * 0.865, 0.012, 1.406)
        add_cube(f"Palm_{side}", palm_center, (0.115, 0.055, 0.092), mats["skin"], 0.018)
        finger_zs = (1.445, 1.422, 1.399, 1.376)
        lengths = (0.085, 0.105, 0.095, 0.072)
        for i, (fz, length) in enumerate(zip(finger_zs, lengths), start=1):
            start = (sign * 0.907, 0.014, fz)
            end = (sign * (0.907 + length), 0.014, fz - 0.003)
            add_segment(f"Finger_{side}_{i}", start, end, 0.011, 0.008, mats["skin"], 6)
        # Thumb angles down and forward from the palm; mirror its lateral direction.
        thumb_start = (sign * 0.865, 0.040, 1.38)
        thumb_end = (sign * 0.90, 0.065, 1.335)
        add_segment(f"Thumb_{side}", thumb_start, thumb_end, 0.018, 0.012, mats["skin"], 6)

    # Apply overall character scale to geometry only; camera placement adapts later.
    scale = float(cfg.get("scale", 1.0))
    if abs(scale - 1.0) > 1e-6:
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH":
                obj.location *= scale
                obj.dimensions *= scale
                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.select_all(action="DESELECT")

    return mats


def setup_scene(cfg):
    scene = bpy.context.scene
    render_cfg = cfg.get("render", {})
    resolution = int(render_cfg.get("resolution", 900))
    samples = int(render_cfg.get("samples", 24))
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = bool(render_cfg.get("transparent", False))
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    scene.render.image_settings.color_mode = "RGBA" if scene.render.film_transparent else "RGB"
    scene.view_settings.view_transform = "Standard"
    look_ids = [item.identifier for item in scene.view_settings.bl_rna.properties["look"].enum_items]
    preferred_look = "Medium High Contrast"
    scene.view_settings.look = preferred_look if preferred_look in look_ids else (look_ids[0] if look_ids else "Medium High Contrast")
    scene.world.color = (0.045, 0.04, 0.06)

    def area_light(name, location, energy, size, color):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        direction = Vector((0, 0, 0.95)) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    area_light("Key_Light", (3.2, 4.0, 4.2), 420, 4.0, (1.0, 0.82, 0.72))
    area_light("Fill_Light", (-3.5, 2.7, 2.8), 280, 3.5, (0.65, 0.72, 1.0))
    area_light("Rim_Light", (0.2, -3.0, 3.4), 520, 2.5, (0.56, 0.4, 1.0))
    scene.render.image_settings.color_depth = "8"
    scene.camera = None


def aim_camera(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_camera(name, location, target, scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = 2.45 * scale
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    aim_camera(camera, target)
    return camera


def object_dimensions(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {axis: round(maxs[i] - mins[i], 5) for i, axis in enumerate(("x", "y", "z"))}


def export_asset(fmt, outdir):
    fmt = fmt.lower()
    selected_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in selected_meshes:
        obj.select_set(True)
    if selected_meshes:
        bpy.context.view_layer.objects.active = selected_meshes[0]
    if fmt in ("glb", "gltf"):
        ext = "glb" if fmt == "glb" else "gltf"
        path = outdir / f"character.{ext}"
        result = bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB" if fmt == "glb" else "GLTF_SEPARATE",
                                           use_selection=True, export_apply=True)
    elif fmt == "fbx":
        path = outdir / "character.fbx"
        result = bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_scale_options="FBX_SCALE_ALL",
                                          bake_space_transform=False, add_leaf_bones=False)
    elif fmt == "obj":
        path = outdir / "character.obj"
        if hasattr(bpy.ops.wm, "obj_export"):
            result = bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, apply_modifiers=True,
                                           export_materials=True, forward_axis="NEGATIVE_Z", up_axis="Y")
        elif hasattr(bpy.ops.export_scene, "obj"):
            result = bpy.ops.export_scene.obj(filepath=str(path), use_selection=True, use_materials=True,
                                              axis_forward="-Z", axis_up="Y")
        else:
            raise RuntimeError("OBJ exporter is unavailable in this Blender installation")
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    if "FINISHED" not in result or not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Export failed for {fmt}: {path}")
    return path


def render_views(outdir, scale):
    scene = bpy.context.scene
    target = (0, 0, 0.95 * scale)
    views = {
        "front": (0, 4.8 * scale, 0.99 * scale),
        "side": (4.8 * scale, 0, 0.99 * scale),
        "back": (0, -4.8 * scale, 0.99 * scale),
    }
    for view, location in views.items():
        camera = create_camera(f"Camera_{view.title()}", location, target, scale)
        scene.camera = camera
        scene.render.filepath = str(outdir / f"preview_{view}.png")
        bpy.ops.render.render(write_still=True)
        if not (outdir / f"preview_{view}.png").exists():
            raise RuntimeError(f"Render did not produce preview_{view}.png")
        bpy.data.objects.remove(camera, do_unlink=True)


def main():
    args = parse_args()
    config_path = args.config.resolve()
    outdir = args.outdir.resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    # Validate via the sibling helper where possible; fail fast before touching scene.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from validate_config import validate_config
        errors = validate_config(cfg)
        if errors:
            raise ValueError("Invalid configuration:\n- " + "\n- ".join(errors))
    except ImportError:
        pass
    formats = args.formats or cfg.get("exports", ["glb"])
    if not formats:
        raise ValueError("At least one export format must be requested")
    outdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights, bpy.data.materials):
        # Keep no stale objects/materials from startup scene.
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    build_character(cfg)
    setup_scene(cfg)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    report = {
        "name": cfg.get("name", "Character"),
        "generator": "ai-3d-character-creator",
        "blender_version": bpy.app.version_string,
        "mesh_object_count": len(meshes),
        "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
        "polygon_count": sum(len(obj.data.polygons) for obj in meshes),
        "dimensions": object_dimensions(meshes),
        "materials": sorted({mat.name for obj in meshes for mat in obj.data.materials if mat}),
        "requested_formats": list(formats),
        "exports": [],
        "preview_renders": [],
        "notes": ["Procedural low-poly starter; no armature or skin weights.", "Visual inspection is still required."],
    }
    for fmt in formats:
        path = export_asset(fmt, outdir)
        report["exports"].append({"format": fmt, "path": path.name, "bytes": path.stat().st_size})
    do_render = args.render_views and not args.no_render
    if do_render:
        render_views(outdir, float(cfg.get("scale", 1.0)))
        report["preview_renders"] = [f"preview_{view}.png" for view in ("front", "side", "back")]
    (outdir / "character_config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    (outdir / "model_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
