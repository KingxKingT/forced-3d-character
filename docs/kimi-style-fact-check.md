# Fact check: universal "Kimi-style" low-poly skill

This repository uses the term "Kimi-style" only as shorthand for a disciplined procedural workflow. It is not a verified description of Kimi's private implementation.

## Claims reviewed

| Claim | Assessment | Correction |
|---|---|---|
| BMesh or explicit vertex data improves deterministic modeling | Useful practice | Both are valid tools. Use direct mesh data for simple explicit geometry and BMesh for topology operations. |
| Never use any `bpy.ops` | Too absolute | Avoid context-sensitive primitive-add operators in reusable geometry helpers. Other operators may be necessary for import/export and scene actions; make context explicit and check results. |
| BMesh guarantees clean topology | False | BMesh can still produce degenerate faces, duplicate vertices, holes, bad normals, and self-intersections. Validate the output. |
| Flat shading is always required | Style-specific | Set `polygon.use_smooth = False` for the requested low-poly look. Other art styles need different shading. |
| All models must be 500–1,500 triangles | Not a universal rule | Choose a budget for the whole asset, camera distance, platform, animation, and silhouette. Report actual counts. |
| N-gons must always be removed | Too absolute | Quads often help deformation; triangles are common in real-time export; planar n-gons may be acceptable on static surfaces. Check triangulation and export results. |
| A skill can make any AI as capable as Kimi | Unsupported | A skill supplies instructions and examples; it cannot change the base model's reasoning, visual perception, or code ability. |
| Kimi's 3D quality comes only from BMesh | Unsupported | Kimi's public materials describe model capability and tool use, but do not establish the internal Blender implementation claimed by the pasted text. |

## Technical notes

### Mesh data and BMesh

Blender exposes both the mesh data API and the standalone BMesh module. They serve different needs. Explicit vertices/faces through `Mesh.from_pydata` are suitable for generated meshes; BMesh is useful for operations and topology edits. Neither method automatically guarantees manifold or attractive geometry.

### Operators

Blender's Python API includes operators as well as data access. Blender's own quickstart notes that context changes depending on where an operator runs. This is why primitive-add operators can be fragile in headless or MCP contexts. The right rule is "prefer context-independent data construction for mesh geometry," not "never use an operator."

### Flat shading

For a flat-shaded low-poly asset, set each polygon's `use_smooth` property to false. This is a per-polygon mesh property; it does not need a shading operator.

### Hair spike bug in the supplied example

The supplied extruded-hair snippet assigns the same tip coordinate to every vertex returned by the extrusion. That collapses the entire extruded region into coincident points and can create degenerate geometry. Only the vertices belonging to the intended top cap should be moved/scaled, or use a separate explicit pyramid mesh as shown in `references/bmesh_cheatsheet.md`.

### Kimi claims

As of 30 October 2026, Kimi's public K3.1 Pro announcement discusses 3D creation, parametric modeling, and BenchCAD performance with tools. Kimi's 3D Make help page says the product is powered by Kimi K3.1 Pro. Neither source demonstrates that Kimi's proprietary 3D workflow is based on the exact BMesh rules in the pasted text. The BMesh strategy should therefore be treated as our own engineering recipe, not a reverse-engineered account of Kimi.

## Sources

- [Blender Python API](https://docs.blender.org/api/current/) — API modules include both data access and BMesh.
- [Blender Python API quickstart source](https://github.com/blender/blender/blob/main/doc/python_api/rst/info_quickstart.rst) — context and data-access discussion.
- [Kimi K3.1 Pro announcement](https://www.kimi.ai/blog/kimi-k3-1-pro) — public description of model capabilities and tool-use results.
- [Kimi 3D Make overview](https://www.kimi.com/en/help/3d-make/3d-make-overview) — public description of its 3D creation product.
