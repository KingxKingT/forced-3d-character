# Pipeline and configuration reference

## Overview

The default workflow is a light, procedural Blender pipeline suitable for modest hardware. An AI translates the reference into a geometric plan and Python code; Blender creates the mesh locally. This does not require local neural inference or a paid 3D API.

For an 11th-gen Intel Core i3, 8 GB RAM, and integrated graphics, use the low-spec settings in [low-spec-workflow.md](low-spec-workflow.md).

A stronger computer can optionally connect to [Effigy](https://github.com/SifuInTheShell/Effigy) for neural image-to-3D and a more advanced retopology, UV, texturing, rigging, and export pipeline. It is a separate application and is not part of the low-spec requirement. See [local-ai-backend.md](local-ai-backend.md).

## Geometry approach

- Use `Mesh.from_pydata` when the vertices and faces are already known.
- Use BMesh for topology operations and procedural mesh construction.
- Avoid primitive-add operators in reusable mesh-building helpers; they depend on selection and active context.
- Do not ban every `bpy.ops` call. Some import/export and scene operations are operators; use them with deliberate context and verify their results.
- Validate geometry before export. BMesh does not automatically guarantee clean topology.
- Set `polygon.use_smooth = False` for the requested flat-shaded aesthetic.
- Use quad flow when deformation/editing needs it, triangles for runtime export, and n-gons only where planar/static geometry and export triangulation are acceptable.
- Do not impose a universal 1,500-triangle cap. Choose a budget for the platform, camera distance, silhouette, and animation needs.

See [references/bmesh_cheatsheet.md](../references/bmesh_cheatsheet.md) and [kimi-style-fact-check.md](kimi-style-fact-check.md).

## Existing procedural blockout configuration

The JSON config used by `scripts/blender/create_character.py` describes:

- `name`: descriptive character name.
- `scale`: global scale multiplier (0.1–5.0).
- `style`: current builder targets `low_poly_stylized`.
- `pose`: current builder supports the configured T-pose-style arrangement.
- `palette`: six-digit hex colours.
- `features`: hair style and optional face/outfit accents.
- `outfit`: jacket details such as lapels, tie, shirt, and cuffs.
- `render`: preview resolution, samples, and background transparency.
- `exports`: GLB, GLTF, FBX, or OBJ.

Run `python scripts/validate_config.py examples/dark_suit_purple_eyes.json` before Blender generation.

## Validate the current Blender scene

```bash
blender --background character.blend --python scripts/blender/validate_mesh.py -- \
  --report build/mesh-report.json --max-triangles 6000
```

This checks structural issues only. The triangle cap is configurable and warns by default. Boundary edges are allowed unless `--require-watertight` is supplied.

## Fallback generator

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/test-character \
  --formats glb
```

The script clears the startup scene. Run it as a dedicated background process, not inside an unsaved interactive scene.

## Known limitations

- The procedural blockout is not neural image-to-3D.
- The existing character blockout has no production armature, skin weights, facial rig, or animation clips.
- Structural validation does not judge reference similarity, anatomy, visual polish, UV quality, or deformation.
- No Blender runtime test is claimed unless run with Blender installed.
