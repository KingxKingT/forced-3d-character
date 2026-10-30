"""Import a model export in Blender and write a structural validation report."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    return parser.parse_args(argv)


def import_asset(path):
    ext = path.suffix.lower()
    if ext in (".glb", ".gltf"):
        return bpy.ops.import_scene.gltf(filepath=str(path))
    if ext == ".fbx":
        return bpy.ops.import_scene.fbx(filepath=str(path))
    if ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            return bpy.ops.wm.obj_import(filepath=str(path))
        if hasattr(bpy.ops.import_scene, "obj"):
            return bpy.ops.import_scene.obj(filepath=str(path))
    raise ValueError(f"Unsupported file type or unavailable importer: {ext}")


def main():
    args = parse_args()
    asset = args.file.resolve()
    report_path = args.report.resolve()
    checks = []
    fatal = []
    if not asset.is_file():
        raise FileNotFoundError(f"Asset not found: {asset}")
    if asset.stat().st_size <= 0:
        raise ValueError(f"Asset file is empty: {asset}")
    checks.append({"name": "file_exists_and_non_empty", "passed": True})
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    import_result = import_asset(asset)
    if "FINISHED" not in import_result:
        fatal.append("Blender importer did not finish")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    vertices = sum(len(obj.data.vertices) for obj in meshes)
    polygons = sum(len(obj.data.polygons) for obj in meshes)
    materials = sorted({mat.name for obj in meshes for mat in obj.data.materials if mat})
    world_bounds = []
    for obj in meshes:
        for corner in obj.bound_box:
            world_bounds.append(obj.matrix_world @ Vector(corner))
    dimensions = {"x": 0.0, "y": 0.0, "z": 0.0}
    if world_bounds:
        for idx, axis in enumerate(("x", "y", "z")):
            dimensions[axis] = round(max(p[idx] for p in world_bounds) - min(p[idx] for p in world_bounds), 6)
    checks.append({"name": "mesh_geometry_present", "passed": len(meshes) > 0 and vertices > 0 and polygons > 0,
                   "mesh_objects": len(meshes), "vertices": vertices, "polygons": polygons})
    if not meshes or vertices == 0 or polygons == 0:
        fatal.append("No mesh geometry was imported")
    nonzero_bounds = all(v > 1e-4 for v in dimensions.values())
    checks.append({"name": "non_zero_dimensions", "passed": nonzero_bounds, "dimensions": dimensions})
    if not nonzero_bounds:
        fatal.append("Imported mesh has zero or near-zero bounds on at least one axis")
    checks.append({"name": "materials_present", "passed": len(materials) > 0, "material_count": len(materials)})
    if not materials:
        fatal.append("No materials were found on imported mesh objects")
    report = {
        "asset": str(asset),
        "bytes": asset.stat().st_size,
        "blender_version": bpy.app.version_string,
        "passed": len(fatal) == 0,
        "fatal_errors": fatal,
        "checks": checks,
        "limitations": ["Structural import checks only; not a visual, topology, rigging, UV, or animation certification."],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if fatal:
        raise RuntimeError("Asset validation failed: " + "; ".join(fatal))


if __name__ == "__main__":
    main()
