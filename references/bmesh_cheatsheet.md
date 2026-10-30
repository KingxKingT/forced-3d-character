# Blender Procedural Mesh Cheat Sheet

These examples show three useful approaches: Blender mesh data, BMesh editing, and explicit low-poly geometry. Use the approach that fits the operation; none guarantees good topology by itself.

## 1. Create a mesh from explicit vertices and faces

Use this for predictable custom pieces such as jacket panels, hair locks, collars, shoes, and low-poly props.

```python
import bpy
import math

def create_mesh_from_pydata(name, vertices, faces, collection=None):
    if not vertices or not faces:
        raise ValueError("A mesh needs at least one vertex and one face")

    vertex_count = len(vertices)
    checked_faces = []
    for face_index, face in enumerate(faces):
        face = tuple(face)
        if len(face) < 3:
            raise ValueError(f"Face {face_index} has fewer than 3 vertices")
        if len(set(face)) != len(face):
            raise ValueError(f"Face {face_index} repeats a vertex index")
        if any(not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= vertex_count
               for i in face):
            raise ValueError(f"Face {face_index} contains an invalid vertex index")
        checked_faces.append(face)

    for vertex_index, vertex in enumerate(vertices):
        if len(vertex) != 3 or not all(math.isfinite(float(c)) for c in vertex):
            raise ValueError(f"Vertex {vertex_index} must contain 3 finite coordinates")

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], checked_faces)
    changed = mesh.validate(verbose=True, clean_customdata=True)
    if changed:
        bpy.data.meshes.remove(mesh)
        raise ValueError("Blender had to repair invalid mesh data; fix the source vertices/faces")
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(name, mesh)
    target = collection if collection is not None else bpy.context.scene.collection
    target.objects.link(obj)

    for polygon in mesh.polygons:
        polygon.use_smooth = False
    return obj
```

Do not catch and ignore `mesh.validate` or face-creation errors. Fix the source geometry instead.

## 2. Create and edit topology with BMesh

BMesh is useful for mesh operations and topology edits. It is not a magic "clean mesh" switch.

```python
import bpy
import bmesh

bm = bmesh.new()
try:
    bmesh.ops.create_cube(bm, size=1.0)

    # Example of a deterministic edit to the positive-Z vertices.
    bm.verts.ensure_lookup_table()
    for vertex in bm.verts:
        if vertex.co.z > 0:
            vertex.co.x *= 0.85

    bm.normal_update()

    mesh = bpy.data.meshes.new("Tapered_Block")
    bm.to_mesh(mesh)
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new("Tapered_Block", mesh)
    bpy.context.scene.collection.objects.link(obj)

    for polygon in mesh.polygons:
        polygon.use_smooth = False
finally:
    bm.free()
```

BMesh operations such as `bmesh.ops.create_cube`, `create_cone`, or `create_icosphere` are still procedural primitive construction. The practical distinction is that they operate directly on a BMesh, instead of invoking a context-sensitive `bpy.ops.mesh.primitive_*_add` operator.

## 3. A simple closed low-poly hair spike

This explicit pyramid has four base vertices, one tip, one base quad, and four triangular sides. It avoids the common bug of moving every extruded vertex to the same point.

```python
vertices = [
    (-0.05, -0.05, 0.00),  # 0: base front-left
    ( 0.05, -0.05, 0.00),  # 1: base front-right
    ( 0.05,  0.05, 0.00),  # 2: base back-right
    (-0.05,  0.05, 0.00),  # 3: base back-left
    ( 0.00,  0.00, 0.18),  # 4: tip
]
faces = [
    (0, 3, 2, 1),  # underside
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4),
]
```

For a hairstyle, use several larger, overlapping tapered locks with intentional direction. Avoid dozens of tiny spikes: they add noise and make the silhouette harder to control.

## 4. Mirror modifier — only with a real center seam

```python
mirror = obj.modifiers.new(name="Mirror_X", type="MIRROR")
mirror.use_axis = (True, False, False)
mirror.use_clip = True
mirror.use_mirror_merge = True
```

Build only one side of the mesh. Vertices that lie on the centerline must have `x = 0.0`. Do not build two overlapping full halves and then mirror them. Inspect the seam and apply the modifier only when the workflow requires a single baked mesh.

## 5. Flat shading without an operator

```python
for polygon in obj.data.polygons:
    polygon.use_smooth = False
```

This sets the per-polygon shading property directly. Smooth shading is not universally bad; flat shading is a requirement of this specific low-poly style.

## 6. Simple material with a solid palette colour

```python
def make_flat_material(name, rgba):
    material = bpy.data.materials.new(name)
    material.diffuse_color = rgba
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = rgba
        shader.inputs["Roughness"].default_value = 0.8
    return material
```

Use a small palette first. Add image textures only when the reference genuinely needs them.

## 7. Inspect triangle counts and topology

```python
mesh = obj.data
mesh.calc_loop_triangles()
triangle_count = len(mesh.loop_triangles)
print("vertices:", len(mesh.vertices))
print("faces:", len(mesh.polygons))
print("triangles:", triangle_count)
```

Run the repository's scene validator for non-finite coordinates, zero-area faces, loose vertices, open edges, non-manifold edges, n-gons, material slots, flat shading, and a configurable triangle budget.

## 8. When bpy.ops is acceptable

Avoid primitive-add operators in reusable geometry helpers because they depend on selection/active context. Do not ban every operator. Importers, exporters, some modifiers, and UI operations may be exposed only as operators. When using one:

- make the needed object/selection/active item explicit;
- use a background-safe context where possible;
- check that the operator reports `FINISHED`;
- verify the expected file or geometry exists afterward;
- test against the Blender version actually installed.
