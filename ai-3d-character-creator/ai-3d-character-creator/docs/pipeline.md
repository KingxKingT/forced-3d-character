# Pipeline and configuration reference

## Overview

The project uses Blender as the geometry and export engine. A JSON file describes a character, and `scripts/blender/create_character.py` builds meshes, assigns materials, configures lights and orthographic cameras, writes model metadata, and exports the requested formats.

## Configuration fields

- `name`: descriptive character name used in object and report names.
- `scale`: global scale multiplier (0.1–5.0).
- `style`: descriptive style label; the current builder targets `low_poly_stylized`.
- `pose`: currently supports a neutral T-pose-style arrangement.
- `palette`: named six-digit hex colors for skin, hair, suit, shirt, tie, eyes, eye whites, shoes, and gold trim.
- `features`: hair style and optional facial/outfit accents. Unsupported feature strings fall back to safe defaults and are noted in the report.
- `outfit`: enables clothing layers such as lapels, tie, shirt, cuffs, and jacket details.
- `render`: preview resolution, Cycles/Eevee sample setting, and background transparency.
- `exports`: list containing any of `glb`, `gltf`, `fbx`, `obj`.

Run `python scripts/validate_config.py examples/dark_suit_purple_eyes.json` before invoking Blender to catch malformed colors or options.

## Command line

The Blender script arguments must appear after `--`:

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/test-character \
  --formats glb fbx obj \
  --render-views
```

`--formats` overrides the `exports` list in the JSON. `--render-views` creates front, side, and back PNG previews. `--no-render` skips them. `--config` and `--outdir` are required. The script clears the startup scene, so use a dedicated Blender background process rather than an interactive session with unsaved work.

## Output and validation

The generator saves a copy of the JSON, model metadata, exported asset files, and requested renders under the output directory. The Blender validator imports the selected export into a clean scene and records whether geometry, non-zero bounds, and materials were found.

The validation report proves only that certain structural checks passed. It does not prove attractive proportions, correct fingers, good deformation, UV completeness, topology suitability, or legal use of referenced imagery. Review the preview images and open the export in the intended runtime.

## Known limitations

- No neural reconstruction from text or image.
- No armature, skin weights, facial rig, animation clips, or retargeting.
- No promise of production-ready retopology or a hand-authored UV layout.
- OBJ materials are less expressive than modern GLB materials.
- Render appearance can vary across Blender versions and render engines.
- The procedural face and hand details are approximations; inspect all views and improve the mesh if the asset is close-up or animation-critical.
