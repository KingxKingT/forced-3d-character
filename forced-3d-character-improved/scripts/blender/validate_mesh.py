"""Inspect source-scene meshes without confusing topology and visual quality.

Run:
  blender --background character.blend --python scripts/blender/validate_mesh.py -- \
    --report build/mesh-report.json --max-triangles 6000 \
    --require-watertight --require-character-parts
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry_core import inspect_mesh  # noqa: E402

REQUIRED_CHARACTER_PARTS = {"head", "face", "hair", "clothing", "hands", "legs", "shoes"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("mesh-validation.json"))
    parser.add_argument("--max-triangles", type=int, default=6000)
    parser.add_argument("--strict-budget", action="store_true")
    parser.add_argument("--require-watertight", action="store_true")
    parser.add_argument("--require-character-parts", action="store_true")
    parser.add_argument("--require-single-component", action="store_true")
    parser.add_argument("--strict-winding", action="store_true", help="Fail on inward closed components")
    parser.add_argument("--strict-planarity", action="store_true", help="Fail on non-planar quads/n-gons")
    args = parser.parse_args(argv)
    if args.max_triangles < 1:
        parser.error("--max-triangles must be at least 1")
    return args


def inspect_object(obj, depsgraph) -> dict:
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = [tuple(vertex.co) for vertex in mesh.vertices]
    faces = [tuple(polygon.vertices) for polygon in mesh.polygons]
    metrics = inspect_mesh(vertices, faces)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        metrics["wire_edges"] = sum(1 for edge in bm.edges if len(edge.link_faces) == 0)
        metrics["non_finite_vertices"] = sum(
            not all(math.isfinite(float(component)) for component in vert.co) for vert in bm.verts
        )
    finally:
        bm.free()
    metrics["degenerate_faces"] = metrics["zero_area_faces"]
    metrics["ngon_faces"] = sum(len(polygon.vertices) > 4 for polygon in mesh.polygons)
    metrics["smooth_shaded_faces"] = sum(polygon.use_smooth for polygon in mesh.polygons)
    metrics["material_slots"] = len(mesh.materials)
    metrics["dimensions"] = [round(float(value), 6) for value in obj.dimensions]
    metrics["object"] = obj.name
    metrics["character_part"] = obj.get("character_part", "unclassified")
    metrics["modifier_count"] = len(obj.modifiers)
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        evaluated_mesh.calc_loop_triangles()
        metrics["evaluated_triangles"] = len(evaluated_mesh.loop_triangles)
    finally:
        evaluated.to_mesh_clear()
    return metrics


def main() -> int:
    args = parse_args()
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    results = [inspect_object(obj, depsgraph) for obj in mesh_objects]
    sum_keys = (
        "vertices", "edges", "faces", "triangles", "evaluated_triangles",
        "boundary_edges", "wire_edges", "non_manifold_edges", "loose_vertices",
        "degenerate_faces", "non_finite_vertices", "ngon_faces", "smooth_shaded_faces",
        "zero_length_edges", "duplicate_faces", "coincident_vertices",
        "inconsistent_winding_edges", "non_planar_ngons",
    )
    totals = {key: sum(item[key] for item in results) for key in sum_keys}
    totals["objects"] = len(results)
    failures: list[str] = []
    warnings: list[str] = []
    if not results:
        failures.append("Scene contains no mesh objects")
    if totals["faces"] == 0 or totals["vertices"] == 0:
        failures.append("Scene contains no usable mesh faces")
    for key, message in (
        ("non_finite_vertices", "Vertices contain non-finite coordinates"),
        ("degenerate_faces", "Faces have zero or near-zero area"),
        ("zero_length_edges", "Edges have zero or near-zero length"),
        ("duplicate_faces", "Duplicate faces were found"),
        ("non_manifold_edges", "Edges are shared by more than two faces"),
        ("inconsistent_winding_edges", "Adjacent faces have inconsistent winding"),
    ):
        if totals[key]:
            failures.append(f"{message}: {totals[key]}")
    if totals["boundary_edges"]:
        message = f"Scene has {totals['boundary_edges']} boundary edges"
        (failures if args.require_watertight else warnings).append(message)
    if totals["wire_edges"]:
        (failures if args.require_watertight else warnings).append(f"Scene has {totals['wire_edges']} wire edges")
    if totals["loose_vertices"]:
        warnings.append(f"Scene has {totals['loose_vertices']} loose vertices")
    if totals["coincident_vertices"]:
        warnings.append(f"Scene has {totals['coincident_vertices']} extra coincident vertices; check unintended splits")
    multi_component = [item["object"] for item in results if item["connected_components"] > 1]
    if multi_component:
        message = "Objects with multiple disconnected components: " + ", ".join(multi_component)
        (failures if args.require_single_component else warnings).append(message)
    inward = [
        item["object"] for item in results
        if item["edge_manifold_closed"] and item["signed_volume"] < -1.0e-10
    ]
    if inward:
        message = "Closed objects with negative signed volume (probably inward): " + ", ".join(inward)
        (failures if args.strict_winding else warnings).append(message)
    if totals["non_planar_ngons"]:
        message = f"Scene has {totals['non_planar_ngons']} non-planar quads/n-gons; inspect export triangulation"
        (failures if args.strict_planarity else warnings).append(message)
    if totals["ngon_faces"]:
        warnings.append(f"Scene has {totals['ngon_faces']} n-gons; planarity and export triangulation need review")
    if totals["smooth_shaded_faces"]:
        warnings.append(f"Scene has {totals['smooth_shaded_faces']} smooth-shaded faces; flat shading was expected")
    budget_count = totals["evaluated_triangles"]
    if budget_count > args.max_triangles:
        message = f"Evaluated triangle budget exceeded: {budget_count} > {args.max_triangles}"
        (failures if args.strict_budget else warnings).append(message)
    if any(item["material_slots"] == 0 for item in results):
        warnings.append("One or more mesh objects have no material slots")
    part_manifest = {}
    for item in results:
        part_manifest.setdefault(item["character_part"], []).append(item["object"])
    if args.require_character_parts:
        missing = sorted(REQUIRED_CHARACTER_PARTS - set(part_manifest))
        if missing:
            failures.append("Missing required semantic character parts: " + ", ".join(missing))
        if "unclassified" in part_manifest:
            failures.append("Unclassified mesh objects are not allowed with --require-character-parts")
    report = {
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "passed": not failures,
        "validation_scope": "source_scene_structure_and_semantics",
        "totals": totals,
        "part_manifest": {key: sorted(value) for key, value in sorted(part_manifest.items())},
        "objects": results,
        "failures": failures,
        "warnings": warnings,
        "visual_review": {"status": "not_tested", "required": True},
        "notes": [
            "Structural inspection does not judge resemblance, anatomy, silhouette, UVs, rigging, or deformation.",
            "Boundary edges can be intentional; use --require-watertight only when closed solids are required.",
            "Signed volume is meaningful for consistently wound closed components, not arbitrary open surfaces.",
            "Triangle limits are project-specific; evaluated counts include modifiers and can differ after export.",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
