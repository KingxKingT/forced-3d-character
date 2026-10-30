"""Inspect mesh objects in the currently opened Blender scene.

Run:
  blender --background character.blend --python scripts/blender/validate_mesh.py -- \
    --report build/mesh-report.json --max-triangles 6000
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("mesh-validation.json"))
    parser.add_argument("--max-triangles", type=int, default=6000)
    parser.add_argument("--strict-budget", action="store_true",
                        help="Treat a triangle-budget overrun as a failure, not a warning")
    parser.add_argument("--require-watertight", action="store_true",
                        help="Treat boundary and wire edges as failures")
    args = parser.parse_args(argv)
    if args.max_triangles < 1:
        parser.error("--max-triangles must be at least 1")
    return args


def inspect_object(obj) -> dict:
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        vertices = len(bm.verts)
        edges = len(bm.edges)
        faces = len(bm.faces)
        boundary_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 1)
        wire_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 0)
        non_manifold_edges = sum(1 for edge in bm.edges if len(edge.link_faces) > 2)
        loose_vertices = sum(1 for vert in bm.verts if len(vert.link_edges) == 0)
        degenerate_faces = sum(1 for face in bm.faces if not math.isfinite(face.calc_area())
                               or face.calc_area() <= 1e-12)
        non_finite_vertices = sum(
            1 for vert in bm.verts
            if not all(math.isfinite(float(component)) for component in vert.co)
        )
    finally:
        bm.free()

    triangles = len(mesh.loop_triangles)
    ngons = sum(1 for polygon in mesh.polygons if len(polygon.vertices) > 4)
    smooth_faces = sum(1 for polygon in mesh.polygons if polygon.use_smooth)
    material_slots = len(mesh.materials)
    dimensions = [round(float(value), 6) for value in obj.dimensions]

    return {
        "object": obj.name,
        "vertices": vertices,
        "edges": edges,
        "faces": faces,
        "triangles": triangles,
        "boundary_edges": boundary_edges,
        "wire_edges": wire_edges,
        "non_manifold_edges": non_manifold_edges,
        "loose_vertices": loose_vertices,
        "degenerate_faces": degenerate_faces,
        "non_finite_vertices": non_finite_vertices,
        "ngon_faces": ngons,
        "smooth_shaded_faces": smooth_faces,
        "material_slots": material_slots,
        "dimensions": dimensions,
    }


def main() -> int:
    args = parse_args()
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    results = [inspect_object(obj) for obj in mesh_objects]

    totals = {
        key: sum(item[key] for item in results)
        for key in (
            "vertices", "edges", "faces", "triangles", "boundary_edges", "wire_edges",
            "non_manifold_edges", "loose_vertices", "degenerate_faces",
            "non_finite_vertices", "ngon_faces", "smooth_shaded_faces",
        )
    }
    totals["objects"] = len(results)
    failures: list[str] = []
    warnings: list[str] = []

    if not results:
        failures.append("Scene contains no mesh objects")
    if totals["faces"] == 0 or totals["vertices"] == 0:
        failures.append("Scene contains no usable mesh faces")
    if totals["non_finite_vertices"]:
        failures.append("One or more vertices contain non-finite coordinates")
    if totals["degenerate_faces"]:
        failures.append("One or more faces have zero or near-zero area")
    if totals["non_manifold_edges"]:
        failures.append("One or more edges are shared by more than two faces")
    if totals["boundary_edges"]:
        message = f"Scene has {totals['boundary_edges']} boundary edges"
        (failures if args.require_watertight else warnings).append(message)
    if totals["wire_edges"]:
        warnings.append(f"Scene has {totals['wire_edges']} wire edges")
    if totals["loose_vertices"]:
        warnings.append(f"Scene has {totals['loose_vertices']} loose vertices")
    if totals["ngon_faces"]:
        warnings.append(f"Scene has {totals['ngon_faces']} n-gon faces; inspect their planarity and export triangulation")
    if totals["smooth_shaded_faces"]:
        warnings.append(f"Scene has {totals['smooth_shaded_faces']} smooth-shaded faces; flat shading was expected by this skill")
    if totals["triangles"] > args.max_triangles:
        message = f"Triangle budget exceeded: {totals['triangles']} > {args.max_triangles}"
        (failures if args.strict_budget else warnings).append(message)
    if any(item["material_slots"] == 0 for item in results):
        warnings.append("One or more mesh objects have no material slots")

    report = {
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "passed": not failures,
        "totals": totals,
        "objects": results,
        "failures": failures,
        "warnings": warnings,
        "notes": [
            "Structural inspection only: this does not judge resemblance, good anatomy, UV quality, rigging, or deformation.",
            "Boundary edges may be intentional for open surfaces. Use --require-watertight only for a closed solid.",
            "Triangle limits are project-specific; the default is a warning, not a universal quality standard.",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
