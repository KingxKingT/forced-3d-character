# Pipeline and Configuration Reference

## 1. Plan

Identify observable references, intended use, coordinate system, proportions, semantic parts, topology intent, triangle budget, materials, cameras, and output formats. Do not claim an image comparison when no image exists. The universal decision process is in [../SKILL.md](../SKILL.md).

## 2. Configure

The JSON schema supports:

- `name`, `scale` (0.1–5.0), `style=low_poly_stylized`, and `pose=t_pose`;
- `palette` six-digit RGB colours;
- `features`: `side_swept` or `short` hair, eye colour, brows, ears, nose, mouth, beard, buttons, and pocket square;
- `outfit`: tailored jacket with shirt, lapels, tie, and cuffs toggles;
- `render`: resolution 128–4096, samples 1–512, transparency;
- `exports`: non-duplicated `glb`, `gltf`, `fbx`, and/or `obj`.

Validate without Blender:

```bash
python scripts/validate_config.py examples/dark_suit_purple_eyes.json
```

## 3. Generate locally

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/character --formats glb --save-blend --render-views
```

`geometry_core.py` creates deterministic vertex/face arrays. `mesh_tools.py` validates arrays before Blender creation and adds flat-shaded materials and semantic metadata. The generator assembles profile-lofted and swept parts, fits clothing panels to the torso, optionally saves `.blend`, exports selected meshes with evaluated modifiers, and renders inspection views.

The script clears the startup scene. Use a dedicated background process. A successful script is not a visual approval.

## 4. Validate source geometry

```bash
blender --background build/character/character.blend --python-exit-code 1 \
  --python scripts/blender/validate_mesh.py -- \
  --report build/character/source-validation.json \
  --max-triangles 6000 --strict-budget \
  --require-watertight --require-single-component \
  --require-character-parts --strict-winding
```

This generator intentionally uses closed, single-component objects. Other projects may allow open boundaries or multiple components. Non-planar fitted panels and sweep quads are warnings by default because their export triangulation needs inspection; they are not automatically invalid.

## 5. Validate export and target use

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/blender/validate_character.py -- \
  --file build/character/character.glb \
  --report build/character/roundtrip-validation.json \
  --require-character-parts
```

Run the Khronos glTF Validator for GLB/glTF delivery and inspect the intended viewer. Repeat re-import for FBX/OBJ when requested. Source and exported counts can differ due to modifiers, triangulation, normals, and attribute splits.

## 6. Review and iterate

Inspect front, side, back, three-quarter, head, and hand images with [visual-review.md](visual-review.md). Fix diagnosed geometry/placement defects and rerun affected checks. Record `not_tested` for missing review, reference comparison, animation, UV, and target-hardware performance checks.

## Current limitations

The generator is procedural, not neural image-to-3D. It creates a static multi-part character without a production armature, skin weights, facial rig, UV workflow, or animation clips. Attractive close-up anatomy and hairstyle still depend on art direction and iteration. No universal render-time or memory promise is made for the baseline computer.
