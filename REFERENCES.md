# Primary Implementation and Research References

## Blender APIs and manual

- [Mesh API](https://docs.blender.org/api/current/bpy.types.Mesh.html) — `from_pydata`, loop triangles, validation, and mesh data.
- [BMesh API](https://docs.blender.org/api/current/bmesh.html) — topology editing and inspection.
- [Curve geometry](https://docs.blender.org/manual/en/latest/modeling/curves/properties/geometry.html) — bevelled curve construction.
- [Geometry Nodes: Curve to Mesh](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/curve/operations/curve_to_mesh.html) — profile sweeping.
- [Bevel modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html) — controlled edge geometry.
- [glTF import/export](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html) — selection, evaluated modifiers, normals, shape keys, and coordinate conversion.
- [Blender hardware requirements](https://www.blender.org/download/requirements/) — current published minimum/recommended system guidance.

## Character and asset systems

- [MPFB2](https://github.com/makehumancommunity/mpfb2) and [MakeHuman/MPFB licence](https://static.makehumancommunity.org/about/license.html).
- [MakeHuman 2020 licence clarification](https://static.makehumancommunity.org/oldsite/faq/what_changed_regarding_the_license_in_2020.html).
- [CharMorph](https://github.com/Upliner/CharMorph) and [base-character documentation](https://charmorph-docs.readthedocs.io/en/main/Introduction.html).
- [MB-Lab](https://github.com/animate1978/MB-Lab) — mixed/restrictive reuse boundaries; not copied here.
- [Quaternius Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) — CC0 asset-backed option.
- [KayKit Adventures](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0) — CC0 low-poly character pack.
- [Kenney licence support](https://kenney.nl/support).

## Topology, hair, clothing, and validation research

- [SMPL paper](https://files.is.tue.mpg.de/black/papers/SMPL2015.pdf) — fixed template, identity/pose blend shapes, joint regression, and skinning concepts.
- [MANO](https://mano.is.tue.mpg.de/) — hand-model research; no model data redistributed.
- [Instant Field-Aligned Meshes](https://igl.ethz.ch/projects/instant-meshes/) and [Instant Meshes source](https://github.com/wjakob/instant-meshes).
- [QuadriFlow source](https://github.com/hjwdzh/QuadriFlow) — check actual `LICENSE.txt` and dependency options.
- [CHARM anime hair parameterization](https://arxiv.org/html/2509.21114v1) — control-point/width/thickness representation; neural model not used.
- [Hair Meshes](https://www.cemyuksel.com/research/hairmeshes/hairmeshes.pdf) — generalized-cylinder and wisp concepts.
- [MakeHuman clothing guide](https://static.makehumancommunity.org/assets/creatingassets/makeclothes/clothes.html) — body-derived clothing fitting.
- [Costumy](https://github.com/cdrinmatane/Costumy) — pattern-to-garment research, not a default dependency.
- [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) — format/accessor/resource validation beyond Blender re-import.

These references inform original implementation and optional routes. Their inclusion does not relicense their code, data, papers, or assets. See [docs/licences.md](docs/licences.md).
