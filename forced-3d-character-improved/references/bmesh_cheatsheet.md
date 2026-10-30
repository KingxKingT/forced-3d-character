# Practical Blender Mesh and BMesh Reference

The repository's reusable implementations live in `scripts/geometry_core.py` (pure Python) and `scripts/blender/mesh_tools.py` (Blender adapter). The examples below are complete patterns, but structural correctness still does not prove good character art.

## 1. Validate arrays before creating a Blender mesh

`Mesh.from_pydata` is appropriate when vertices and faces are already known. Validate indices and coordinates first. `Mesh.validate()` can correct invalid data; a correction means the source arrays need attention, not that the intended geometry survived.

```python
import math
import bpy


def create_mesh_from_pydata(name, vertices, faces, collection=None):
    if len(vertices) < 3 or not faces:
        raise ValueError("A mesh needs at least three vertices and one face")
    for index, vertex in enumerate(vertices):
        if len(vertex) != 3 or not all(math.isfinite(float(c)) for c in vertex):
            raise ValueError(f"Vertex {index} is not a finite XYZ triple")
    for face_index, raw_face in enumerate(faces):
        face = tuple(raw_face)
        if len(face) < 3 or len(set(face)) != len(face):
            raise ValueError(f"Face {face_index} is degenerate or repeats an index")
        if any(type(i) is not int or i < 0 or i >= len(vertices) for i in face):
            raise ValueError(f"Face {face_index} has an invalid vertex index")

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    if mesh.validate(verbose=True, clean_customdata=True):
        bpy.data.meshes.remove(mesh)
        raise ValueError("Blender repaired the mesh; fix the source arrays")
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    (collection or bpy.context.scene.collection).objects.link(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    return obj
```

The production adapter also adds material and semantic-part metadata. Avoid silently catching face-construction exceptions.

## 2. Ring loft with outward winding

For rings ordered counter-clockwise when viewed from +Z, reverse the bottom cap, keep the top cap forward, and use `(lower_i, lower_next, upper_next, upper_i)` for sides.

```python
from geometry_core import horizontal_loft

vertices, faces = horizontal_loft(
    [
        # z, centre_x, centre_y, radius_x, radius_y
        (0.00, 0.0, 0.0, 0.08, 0.06),
        (0.15, 0.0, 0.0, 0.11, 0.08),
        (0.35, 0.0, 0.0, 0.07, 0.05),
    ],
    segments=12,
    exponent=2.0,       # ellipse; above 2 gives a rounded rectangle
)
obj = create_mesh_from_pydata("Neck_Or_Torso_Loft", vertices, faces)
```

Rules and common failures:

- Every ring in one loft must have the same vertex count and corresponding order.
- Use a small positive tip radius, not a zero-radius ring that creates coincident vertices and zero-length edges.
- An n-gon cap is reasonable when planar and static. Inspect export triangulation.
- A rounded-rectangle torso section can read more tailored than a bevelled cube.
- Changing ring centre and radius creates a profile; random per-ring rotation usually creates twisting.

The generic `loft_rings(rings, cap_start=True, cap_end=True)` function accepts explicit 3D rings when the path is not Z-aligned.

## 3. Catmull–Rom swept volume

Use `sweep_mesh` for a solid hair lock, finger, sleeve, or curved shoe last. Width and thickness are radii. The implementation projects the previous thickness axis into each new tangent plane to reduce arbitrary frame flips.

```python
from geometry_core import sweep_mesh

vertices, faces = sweep_mesh(
    control_points=[
        (-0.06, 0.02, 1.80),
        (-0.02, 0.08, 1.77),
        ( 0.03, 0.11, 1.72),
    ],
    widths=[0.018, 0.020, 0.002],
    thicknesses=[0.008, 0.009, 0.0015],
    sides=6,
    samples_per_segment=2,
    thickness_reference=(0.0, 1.0, 0.0),
)
obj = create_mesh_from_pydata("Designed_Hair_Lock", vertices, faces)
```

Check that the path, widths, and thicknesses have equal lengths. More samples smooth the centreline but also create more non-planar quads and triangles. A sweep does not automatically avoid self-intersection at tight bends. Inspect the cap, taper, and side profile.

## 4. Solid XZ panels for lapels, ties, and facial shapes

`extrude_xz_polygon` builds a closed panel facing +Y. It normalizes outline winding and produces outward-facing caps and sides.

```python
from geometry_core import extrude_xz_polygon, mirrored_outline

left = [(-0.07, 1.43), (-0.17, 1.36), (-0.05, 1.11), (-0.07, 1.27)]
vertices, faces = extrude_xz_polygon(left, front_y=0.135, back_y=0.113)
obj = create_mesh_from_pydata("Notched_Lapel_L", vertices, faces)

right_vertices, right_faces = extrude_xz_polygon(
    mirrored_outline(left), front_y=0.135, back_y=0.113
)
```

A constant-Y panel can float away from a tapered torso. The generator's `tailored_front_y(z)` fitting step demonstrates the required correction. Fitting an n-gon to a curved surface can make it non-planar; triangulate deliberately and inspect the result rather than hiding the warning.

`almond_lens(center, width, height, depth)` creates a closed stylized eye solid in the same XZ plane.

## 5. BMesh for topology editing and inspection

BMesh is useful for procedural primitives, connectivity operations, bevels, dissolves, and normal recalculation. It does not guarantee coordinates, silhouette, deformation flow, or manifoldness.

```python
import bpy
import bmesh

bm = bmesh.new()
try:
    bmesh.ops.create_cube(bm, size=1.0)
    for vertex in bm.verts:
        if vertex.co.z > 0.0:
            vertex.co.x *= 0.85
    bm.normal_update()

    boundary = sum(len(edge.link_faces) == 1 for edge in bm.edges)
    wire = sum(len(edge.link_faces) == 0 for edge in bm.edges)
    over_shared = sum(len(edge.link_faces) > 2 for edge in bm.edges)
    loose = sum(len(vertex.link_edges) == 0 for vertex in bm.verts)
    print({"boundary": boundary, "wire": wire, "over_shared": over_shared, "loose": loose})

    mesh = bpy.data.meshes.new("Tapered_Block_mesh")
    bm.to_mesh(mesh)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("Tapered_Block", mesh)
    bpy.context.scene.collection.objects.link(obj)
finally:
    bm.free()
```

`bmesh.ops.create_cube`, `create_cone`, and `create_icosphere` operate directly on a BMesh. They avoid the selection/active-object dependency of `bpy.ops.mesh.primitive_*_add`, but they are still primitive construction. Use them where a primitive is the right shape, not as a substitute for character-specific profiles.

To recalculate face normals after an edit:

```python
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.normal_update()
```

Recalculation cannot infer the desired outside of an arbitrary open patch, repair self-intersection, or choose artistically necessary edge loops.

## 6. Inspect triangles, duplicate faces, winding, and volume

Blender loop triangles reflect mesh triangulation:

```python
mesh = obj.data
mesh.calc_loop_triangles()
print("base triangles:", len(mesh.loop_triangles))
```

Modifiers can change the final count. Inspect the evaluated object as well:

```python
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
evaluated_mesh = evaluated.to_mesh()
try:
    evaluated_mesh.calc_loop_triangles()
    print("evaluated triangles:", len(evaluated_mesh.loop_triangles))
finally:
    evaluated.to_mesh_clear()
```

`geometry_core.inspect_mesh(vertices, faces)` works without Blender and reports duplicate faces, zero-length edges, coincident vertices, inconsistent directed edge use, connected components, non-planar polygons, and signed volume. Signed volume is useful only for consistently wound closed components; it is not a universal quality score for open surfaces.

## 7. Mirror only a true half-mesh

```python
mirror = obj.modifiers.new("Mirror_X", "MIRROR")
mirror.use_axis = (True, False, False)
mirror.use_clip = True
mirror.use_mirror_merge = True
mirror.merge_threshold = 0.0001
```

Center-seam vertices must lie exactly at X=0. Do not create two full overlapping halves and then mirror them. Inspect the seam before and after applying. Mirroring gives geometric symmetry, not automatic symmetry of semantic asymmetries such as a side-swept hairstyle.

## 8. Flat shading and solid materials

Set face properties directly instead of invoking a shading operator:

```python
for polygon in obj.data.polygons:
    polygon.use_smooth = False
```

Flat shading is a style choice, not a universal rule. Smooth shading does not add geometry and cannot repair a poor silhouette.

The included `make_material` converts six-digit sRGB colours to linear values for Blender's Principled BSDF. Start with a small palette and modest specular response. Very dark hair and shoes can become grey or purple under strong studio lights if specular highlights dominate; inspect materials under the actual preview lighting.

## 9. Bevels and n-gons

A small one-segment bevel can create readable edge highlights on a panel:

```python
bevel = obj.modifiers.new("Edge highlights", "BEVEL")
bevel.width = 0.002
bevel.segments = 1
bevel.limit_method = "ANGLE"
```

Bevel width is scene-scale dependent. Large bevels can overlap or erase small details. Keep an editable modifier in the source and export evaluated geometry when required.

Triangles are normal for runtime export. Quads help deliberate editing/deformation. Planar n-gons can be valid static caps. Non-planar n-gons and quads need inspection because Blender and the exporter must choose a triangulation. There is no technically sound universal ban on n-gons or universal 1,500-triangle character cap.

## 10. When `bpy.ops` is appropriate

Avoid primitive-add operators in reusable geometry helpers. Operators remain appropriate for import/export and some scene operations:

```python
result = bpy.ops.export_scene.gltf(
    filepath="/absolute/path/character.glb",
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_extras=True,
)
if "FINISHED" not in result:
    raise RuntimeError("glTF export did not finish")
```

Also verify that the file exists and is non-empty, re-import it, and inspect the target viewer. Run background scripts with `--python-exit-code 1`; otherwise Blender can return process status zero after a Python exception.

## 11. Defect-to-fix map

| Observed defect | Likely cause | Correct response |
|---|---|---|
| Zero-area cap | Collapsed ring or repeated indices | Use positive radii and distinct source vertices. |
| Dark/inverted component | Reversed winding or normals | Fix ring/cap order; recalculate only after source intent is clear. |
| Sudden twisted sweep | Unstable frame or ring correspondence | Use transported frames and consistent section ordering. |
| Floating lapel/tie | Constant-Y panel over tapered body | Fit panel vertices to the body envelope and inspect side view. |
| Mitten/hand fan | Palm block and straight identical fingers | Shape palm, vary lengths, add joints and opposed thumb. |
| Passes BMesh checks but looks wrong | Good connectivity, poor art direction | Change profiles/proportions/placement; do not add random detail. |
| Export count differs | Normal/attribute splits, modifiers, triangulation | Compare evaluated and round-trip counts; inspect target viewer. |
| Valid GLB but unattractive | Format validity is not visual quality | Perform and record multi-view human/AI visual review. |
