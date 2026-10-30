"""Deterministic, Blender-independent mesh construction and inspection helpers.

Coordinates are right-handed and Z-up. Horizontal rings are counter-clockwise
when viewed from +Z. A character built by the companion generator faces +Y.
No function in this module imports bpy, bmesh, numpy, or a third-party package.
"""
from __future__ import annotations

from math import cos, isfinite, pi, sin, sqrt
from typing import Iterable, Sequence

Vector3 = tuple[float, float, float]
Face = tuple[int, ...]
MeshArrays = tuple[list[Vector3], list[Face]]
EPSILON = 1.0e-9


def add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a: Vector3, scalar: float) -> Vector3:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vector3, b: Vector3) -> Vector3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(a: Vector3) -> float:
    return sqrt(dot(a, a))


def normalize(a: Vector3, fallback: Vector3 = (0.0, 0.0, 1.0)) -> Vector3:
    magnitude = length(a)
    if magnitude <= EPSILON:
        return fallback
    return mul(a, 1.0 / magnitude)


def signed_power(value: float, power: float) -> float:
    if abs(value) <= EPSILON:
        return 0.0
    return (1.0 if value > 0.0 else -1.0) * abs(value) ** power


def _as_face(face: Iterable[int]) -> Face:
    return tuple(int(index) for index in face)


def validate_mesh_data(
    vertices: Sequence[Sequence[float]],
    faces: Sequence[Sequence[int]],
    *,
    name: str = "mesh",
) -> None:
    """Reject malformed source arrays before Blender can silently repair them."""
    errors: list[str] = []
    if len(vertices) < 3:
        errors.append("at least three vertices are required")
    if not faces:
        errors.append("at least one face is required")
    for index, vertex in enumerate(vertices):
        if len(vertex) != 3 or not all(isfinite(float(value)) for value in vertex):
            errors.append(f"vertex {index} is not a finite XYZ triple")
    for face_index, raw_face in enumerate(faces):
        face = _as_face(raw_face)
        if len(face) < 3:
            errors.append(f"face {face_index} has fewer than three vertices")
            continue
        if len(set(face)) != len(face):
            errors.append(f"face {face_index} repeats a vertex index")
        for vertex_index in face:
            if vertex_index < 0 or vertex_index >= len(vertices):
                errors.append(
                    f"face {face_index} references invalid vertex {vertex_index}"
                )
    if errors:
        raise ValueError(f"{name} rejected: " + "; ".join(errors))


def loft_rings(
    rings: Sequence[Sequence[Vector3]],
    *,
    cap_start: bool = True,
    cap_end: bool = True,
) -> MeshArrays:
    """Loft equally sized rings, with outward winding along the ring sequence."""
    if len(rings) < 2:
        raise ValueError("a loft needs at least two rings")
    ring_size = len(rings[0])
    if ring_size < 3 or any(len(ring) != ring_size for ring in rings):
        raise ValueError("loft rings must have the same size of at least three")
    vertices = [tuple(map(float, vertex)) for ring in rings for vertex in ring]
    faces: list[Face] = []
    if cap_start:
        faces.append(tuple(reversed(range(ring_size))))
    for ring_index in range(len(rings) - 1):
        lower = ring_index * ring_size
        upper = (ring_index + 1) * ring_size
        for index in range(ring_size):
            nxt = (index + 1) % ring_size
            faces.append((lower + index, lower + nxt, upper + nxt, upper + index))
    if cap_end:
        last = (len(rings) - 1) * ring_size
        faces.append(tuple(last + index for index in range(ring_size)))
    validate_mesh_data(vertices, faces, name="loft")
    return vertices, faces


def horizontal_loft(
    sections: Sequence[Sequence[float]],
    *,
    segments: int = 12,
    exponent: float = 2.0,
    phase: float = 0.0,
) -> MeshArrays:
    """Create a Z-aligned loft from ``(z, center_x, center_y, radius_x, radius_y)``.

    ``exponent=2`` is elliptical; values above two produce controlled rounded-
    rectangle sections useful for tailored clothing and stylized jaws.
    """
    if segments < 3:
        raise ValueError("horizontal_loft needs at least three segments")
    if exponent < 1.0:
        raise ValueError("superellipse exponent must be at least one")
    rings: list[list[Vector3]] = []
    power = 2.0 / exponent
    for section in sections:
        if len(section) != 5:
            raise ValueError("each section is (z, center_x, center_y, radius_x, radius_y)")
        z, center_x, center_y, radius_x, radius_y = map(float, section)
        if radius_x <= 0.0 or radius_y <= 0.0:
            raise ValueError("loft radii must be positive; use a small radius, not zero")
        ring = []
        for index in range(segments):
            angle = phase + 2.0 * pi * index / segments
            ring.append(
                (
                    center_x + radius_x * signed_power(cos(angle), power),
                    center_y + radius_y * signed_power(sin(angle), power),
                    z,
                )
            )
        rings.append(ring)
    return loft_rings(rings)


def catmull_rom(
    control_points: Sequence[Sequence[float]], samples_per_segment: int = 4
) -> list[tuple[float, ...]]:
    """Sample an interpolating Catmull-Rom path, including both endpoints."""
    if len(control_points) < 2:
        raise ValueError("a path needs at least two control points")
    if samples_per_segment < 1:
        raise ValueError("samples_per_segment must be positive")
    points = [tuple(map(float, point)) for point in control_points]
    dimensions = len(points[0])
    if any(len(point) != dimensions for point in points):
        raise ValueError("all path points must have the same dimensions")
    sampled: list[tuple[float, ...]] = []
    for segment in range(len(points) - 1):
        p0 = points[max(0, segment - 1)]
        p1 = points[segment]
        p2 = points[segment + 1]
        p3 = points[min(len(points) - 1, segment + 2)]
        for step in range(samples_per_segment):
            t = step / samples_per_segment
            t2 = t * t
            t3 = t2 * t
            sampled.append(
                tuple(
                    0.5
                    * (
                        2.0 * p1[axis]
                        + (-p0[axis] + p2[axis]) * t
                        + (2.0 * p0[axis] - 5.0 * p1[axis] + 4.0 * p2[axis] - p3[axis]) * t2
                        + (-p0[axis] + 3.0 * p1[axis] - 3.0 * p2[axis] + p3[axis]) * t3
                    )
                    for axis in range(dimensions)
                )
            )
    sampled.append(points[-1])
    return sampled


def sweep_mesh(
    control_points: Sequence[Vector3],
    widths: Sequence[float],
    thicknesses: Sequence[float],
    *,
    sides: int = 8,
    samples_per_segment: int = 2,
    thickness_reference: Vector3 = (0.0, 1.0, 0.0),
) -> MeshArrays:
    """Sweep an elliptical low-poly section along a path with stable frames.

    Width and thickness are radii, not diameters. The previous thickness axis
    is projected into each new normal plane to avoid arbitrary frame flips.
    This is suitable for solid hair locks, fingers, sleeves, and shoe lasts.
    """
    if not (len(control_points) == len(widths) == len(thicknesses)):
        raise ValueError("path, widths, and thicknesses must have equal lengths")
    if len(control_points) < 2 or sides < 3:
        raise ValueError("a sweep needs two points and at least three sides")
    sampled_points = catmull_rom(control_points, samples_per_segment)
    sampled_widths = [item[0] for item in catmull_rom([(float(v),) for v in widths], samples_per_segment)]
    sampled_thicknesses = [item[0] for item in catmull_rom([(float(v),) for v in thicknesses], samples_per_segment)]
    if any(value <= 0.0 for value in sampled_widths + sampled_thicknesses):
        raise ValueError("sweep radii must remain positive along the whole path")
    rings: list[list[Vector3]] = []
    previous_axis = normalize(thickness_reference, (0.0, 1.0, 0.0))
    for index, raw_center in enumerate(sampled_points):
        center = (raw_center[0], raw_center[1], raw_center[2])
        before = sampled_points[max(0, index - 1)]
        after = sampled_points[min(len(sampled_points) - 1, index + 1)]
        tangent = normalize(
            (
                after[0] - before[0],
                after[1] - before[1],
                after[2] - before[2],
            )
        )
        projected = sub(previous_axis, mul(tangent, dot(previous_axis, tangent)))
        if length(projected) <= 1.0e-6:
            fallback = (0.0, 0.0, 1.0) if abs(tangent[2]) < 0.9 else (1.0, 0.0, 0.0)
            projected = sub(fallback, mul(tangent, dot(fallback, tangent)))
        thickness_axis = normalize(projected, (0.0, 1.0, 0.0))
        width_axis = normalize(cross(thickness_axis, tangent), (1.0, 0.0, 0.0))
        previous_axis = thickness_axis
        ring = []
        for side in range(sides):
            angle = 2.0 * pi * side / sides
            offset = add(
                mul(width_axis, cos(angle) * sampled_widths[index]),
                mul(thickness_axis, sin(angle) * sampled_thicknesses[index]),
            )
            ring.append(add(center, offset))
        rings.append(ring)
    return loft_rings(rings)


def polygon_area_xz(outline: Sequence[Sequence[float]]) -> float:
    area = 0.0
    for index, point in enumerate(outline):
        nxt = outline[(index + 1) % len(outline)]
        area += float(point[0]) * float(nxt[1]) - float(nxt[0]) * float(point[1])
    return area * 0.5


def extrude_xz_polygon(
    outline: Sequence[Sequence[float]], front_y: float, back_y: float
) -> MeshArrays:
    """Extrude a simple XZ polygon along Y; useful for lapels and face panels."""
    if len(outline) < 3 or front_y <= back_y:
        raise ValueError("panel needs three outline points and front_y > back_y")
    points = [(float(point[0]), float(point[1])) for point in outline]
    if abs(polygon_area_xz(points)) <= EPSILON:
        raise ValueError("panel outline has zero area")
    if polygon_area_xz(points) < 0.0:
        points.reverse()
    count = len(points)
    vertices = [(x, float(back_y), z) for x, z in points]
    vertices += [(x, float(front_y), z) for x, z in points]
    faces: list[Face] = [tuple(range(count)), tuple(reversed(range(count, count * 2)))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, count + index, count + nxt, nxt))
    validate_mesh_data(vertices, faces, name="XZ panel")
    return vertices, faces


def almond_lens(
    center: Vector3, width: float, height: float, depth: float
) -> MeshArrays:
    """A closed eight-point almond solid in the XZ plane, facing +Y."""
    x, y, z = center
    outline = [
        (x - width, z),
        (x - width * 0.52, z + height * 0.72),
        (x, z + height),
        (x + width * 0.52, z + height * 0.72),
        (x + width, z),
        (x + width * 0.52, z - height * 0.55),
        (x, z - height * 0.72),
        (x - width * 0.52, z - height * 0.55),
    ]
    return extrude_xz_polygon(outline, y + depth * 0.5, y - depth * 0.5)


def mirrored_outline(outline: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    """Mirror an XZ outline across X=0 and reverse its winding."""
    return [(-float(x), float(z)) for x, z in reversed(outline)]


def weld_mesh(
    vertices: Sequence[Sequence[float]],
    faces: Sequence[Sequence[int]],
    *,
    tolerance: float = 1.0e-6,
) -> MeshArrays:
    """Return arrays with exactly/near coincident vertices merged for analysis.

    This does not modify a Blender object. Face order is retained so welding
    that collapses a face remains visible to the structural inspector.
    """
    if tolerance <= 0.0:
        raise ValueError("weld tolerance must be positive")
    unique: list[Vector3] = []
    buckets: dict[tuple[int, int, int], int] = {}
    mapping: list[int] = []
    for raw_vertex in vertices:
        vertex = tuple(map(float, raw_vertex))
        key = tuple(int(round(value / tolerance)) for value in vertex)
        if key not in buckets:
            buckets[key] = len(unique)
            unique.append(vertex)
        mapping.append(buckets[key])
    welded_faces = [tuple(mapping[int(index)] for index in face) for face in faces]
    return unique, welded_faces


def newell_normal(vertices: Sequence[Vector3], face: Face) -> Vector3:
    normal = [0.0, 0.0, 0.0]
    for index, vertex_index in enumerate(face):
        current = vertices[vertex_index]
        nxt = vertices[face[(index + 1) % len(face)]]
        normal[0] += (current[1] - nxt[1]) * (current[2] + nxt[2])
        normal[1] += (current[2] - nxt[2]) * (current[0] + nxt[0])
        normal[2] += (current[0] - nxt[0]) * (current[1] + nxt[1])
    return (normal[0], normal[1], normal[2])


def inspect_mesh(
    vertices: Sequence[Sequence[float]],
    faces: Sequence[Sequence[int]],
    *,
    distance_epsilon: float = 1.0e-7,
    area_epsilon: float = 1.0e-12,
    planarity_tolerance: float = 1.0e-5,
) -> dict:
    """Return language-neutral structural metrics; never call this a visual test."""
    points: list[Vector3] = [tuple(map(float, vertex)) for vertex in vertices]
    polygons = [_as_face(face) for face in faces]
    edge_uses: dict[tuple[int, int], list[int]] = {}
    parent = list(range(len(points)))
    rank = [0] * len(points)

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(a: int, b: int) -> None:
        root_a, root_b = find(a), find(b)
        if root_a == root_b:
            return
        if rank[root_a] < rank[root_b]:
            root_a, root_b = root_b, root_a
        parent[root_b] = root_a
        if rank[root_a] == rank[root_b]:
            rank[root_a] += 1

    zero_area_faces = 0
    non_planar_ngons = 0
    signed_volume = 0.0
    for face in polygons:
        normal = newell_normal(points, face)
        if length(normal) * 0.5 <= area_epsilon:
            zero_area_faces += 1
        elif len(face) > 3:
            unit = normalize(normal)
            origin = points[face[0]]
            if max(abs(dot(sub(points[index], origin), unit)) for index in face) > planarity_tolerance:
                non_planar_ngons += 1
        anchor = points[face[0]]
        for index in range(1, len(face) - 1):
            signed_volume += dot(anchor, cross(points[face[index]], points[face[index + 1]])) / 6.0
        for index, a in enumerate(face):
            b = face[(index + 1) % len(face)]
            key = (min(a, b), max(a, b))
            edge_uses.setdefault(key, []).append(1 if a < b else -1)
            union(a, b)

    seen_faces: set[Face] = set()
    duplicate_faces = 0
    for face in polygons:
        key = tuple(sorted(face))
        if key in seen_faces:
            duplicate_faces += 1
        seen_faces.add(key)
    zero_length_edges = sum(
        1 for a, b in edge_uses if length(sub(points[a], points[b])) <= distance_epsilon
    )
    used_vertices = {index for edge in edge_uses for index in edge}
    position_buckets: dict[tuple[int, int, int], int] = {}
    quantum = max(distance_epsilon, EPSILON)
    for point in points:
        key = tuple(int(round(value / quantum)) for value in point)
        position_buckets[key] = position_buckets.get(key, 0) + 1
    coincident_vertices = sum(count - 1 for count in position_buckets.values())
    return {
        "vertices": len(points),
        "faces": len(polygons),
        "triangles": sum(max(0, len(face) - 2) for face in polygons),
        "edges": len(edge_uses),
        "boundary_edges": sum(len(uses) == 1 for uses in edge_uses.values()),
        "wire_edges": 0,
        "non_manifold_edges": sum(len(uses) > 2 for uses in edge_uses.values()),
        "loose_vertices": len(points) - len(used_vertices),
        "zero_area_faces": zero_area_faces,
        "zero_length_edges": zero_length_edges,
        "duplicate_faces": duplicate_faces,
        "coincident_vertices": coincident_vertices,
        "inconsistent_winding_edges": sum(
            len(uses) == 2 and uses[0] == uses[1] for uses in edge_uses.values()
        ),
        "connected_components": len({find(index) for index in range(len(points))}) if points else 0,
        "non_planar_ngons": non_planar_ngons,
        "signed_volume": signed_volume,
        "edge_manifold_closed": bool(edge_uses) and all(len(uses) == 2 for uses in edge_uses.values()),
    }
