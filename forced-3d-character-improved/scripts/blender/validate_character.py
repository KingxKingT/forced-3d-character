"""Re-import an exported character and write a round-trip structural report."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry_core import inspect_mesh, weld_mesh  # noqa: E402
from validate_mesh import REQUIRED_CHARACTER_PARTS  # noqa: E402


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--max-triangles", type=int, default=8000)
    parser.add_argument("--require-character-parts", action="store_true")
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
    if not asset.is_file():
        raise FileNotFoundError(f"Asset not found: {asset}")
    if asset.stat().st_size <= 0:
        raise ValueError(f"Asset file is empty: {asset}")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    import_result = import_asset(asset)
    fatal = []
    warnings = []
    if "FINISHED" not in import_result:
        fatal.append("Blender importer did not finish")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    object_reports = []
    part_manifest = {}
    for obj in meshes:
        mesh = obj.data
        mesh.calc_loop_triangles()
        vertices_raw = [tuple(vertex.co) for vertex in mesh.vertices]
        faces_raw = [tuple(polygon.vertices) for polygon in mesh.polygons]
        metrics = inspect_mesh(vertices_raw, faces_raw)
        metrics["object"] = obj.name
        metrics["material_slots"] = len(mesh.materials)
        metrics["character_part"] = obj.get("character_part", "unclassified")
        # Flat shading and attribute seams legitimately split exported vertices.
        # Weld a copy for topology analysis without changing the imported asset.
        metrics["welded_metrics"] = inspect_mesh(*weld_mesh(vertices_raw, faces_raw))
        object_reports.append(metrics)
        part_manifest.setdefault(metrics["character_part"], []).append(obj.name)
    vertices = sum(item["vertices"] for item in object_reports)
    polygons = sum(item["faces"] for item in object_reports)
    triangles = sum(item["triangles"] for item in object_reports)
    materials = sorted({mat.name for obj in meshes for mat in obj.data.materials if mat})
    world_bounds = [
        obj.matrix_world @ Vector(corner)
        for obj in meshes
        for corner in obj.bound_box
    ]
    dimensions = {"x": 0.0, "y": 0.0, "z": 0.0}
    if world_bounds:
        for index, axis in enumerate(("x", "y", "z")):
            dimensions[axis] = round(max(p[index] for p in world_bounds) - min(p[index] for p in world_bounds), 6)
    if not meshes or vertices == 0 or polygons == 0:
        fatal.append("No mesh geometry was imported")
    if not all(value > 1.0e-4 for value in dimensions.values()):
        fatal.append("Imported mesh has zero or near-zero bounds on at least one axis")
    if not materials:
        fatal.append("No materials were found on imported mesh objects")
    for key, label in (
        ("zero_area_faces", "zero-area faces"),
        ("zero_length_edges", "zero-length edges"),
        ("duplicate_faces", "duplicate faces"),
        ("non_manifold_edges", "edges with more than two faces"),
        ("inconsistent_winding_edges", "inconsistently wound edges"),
    ):
        count = sum(item["welded_metrics"][key] for item in object_reports)
        if count:
            fatal.append(f"Round-trip mesh has {count} {label}")
    boundary_count = sum(item["welded_metrics"]["boundary_edges"] for item in object_reports)
    if boundary_count:
        warnings.append(f"Welded round-trip mesh has {boundary_count} boundary edges; assess whether they are intentional")
    if triangles > args.max_triangles:
        warnings.append(f"Round-trip triangle count {triangles} exceeds advisory budget {args.max_triangles}")
    if args.require_character_parts:
        missing = sorted(REQUIRED_CHARACTER_PARTS - set(part_manifest))
        if missing:
            fatal.append("Exported asset lost required semantic parts: " + ", ".join(missing))
    report = {
        "asset": str(asset),
        "bytes": asset.stat().st_size,
        "blender_version": bpy.app.version_string,
        "passed": not fatal,
        "validation_scope": "export_roundtrip_structure",
        "fatal_errors": fatal,
        "warnings": warnings,
        "counts": {
            "mesh_objects": len(meshes),
            "vertices": vertices,
            "welded_vertices_for_topology_analysis": sum(item["welded_metrics"]["vertices"] for item in object_reports),
            "polygons": polygons,
            "triangles": triangles,
            "materials": len(materials),
        },
        "dimensions": dimensions,
        "material_names": materials,
        "part_manifest": {key: sorted(value) for key, value in sorted(part_manifest.items())},
        "objects": object_reports,
        "visual_review": {"status": "not_tested", "required": True},
        "limitations": [
            "Blender re-import is not certification in every target viewer or engine.",
            "This is not a visual, UV, rigging, skinning, animation, or performance certification.",
            "Welding is analysis-only and can hide intentional vertex splits; raw counts remain reported.",
            "glTF-specific accessor and extension checks require the separate Khronos glTF Validator.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if fatal:
        raise RuntimeError("Asset validation failed: " + "; ".join(fatal))


if __name__ == "__main__":
    main()
