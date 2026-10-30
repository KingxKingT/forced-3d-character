# AI 3D Character Creator

A practical starter project for AI agents that need to create **real, editable stylized 3D characters** in Blender—not only write image prompts. It includes a procedural Blender generator, reusable JSON character specs, export support, front/side/back previews, validation scripts, tests, and a skill guide for agent workflows.

## What it does

- Builds a stylized low-poly human from named meshes and materials.
- Supports configurable proportions, palette, suit, hair, eyes, facial features, and accessories.
- Exports GLB/GLTF, FBX, and/or OBJ from Blender.
- Can render front, side, and back orthographic previews.
- Writes a JSON report with mesh/object/material counts, dimensions, and export checks.
- Includes a reference-style example: dark tailored suit, black hair, violet eyes, and restrained gold details.

> **Honest limitation:** this is a procedural asset generator, not a neural text-to-3D model. It makes a customizable starting character from Blender geometry; a person or vision-capable agent should inspect the renders and iterate. The initial character is not rigged and should not be called animation-ready.

## Requirements

- Blender 4.2+ recommended (the script uses Blender's Python API; no `pip install bpy` needed).
- Python 3.10+ for the configuration tests and helper utilities.
- Optional: a game engine or 3D viewer that can open GLB/GLTF.

Verify Blender is available:

```bash
blender --version
```

## Quick start

From the repository root:

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/dark-suit \
  --formats glb fbx obj \
  --render-views
```

Expected outputs include:

```text
build/dark-suit/
├── character.glb
├── character.fbx
├── character.obj
├── character.mtl
├── character_config.json
├── model_report.json
├── preview_front.png
├── preview_side.png
└── preview_back.png
```

Export availability can depend on the installed Blender build. The script fails clearly if a requested exporter is unavailable or an export is not created.

Validate the GLB in Blender:

```bash
blender --background --factory-startup --python scripts/blender/validate_character.py -- \
  --file build/dark-suit/character.glb \
  --report build/dark-suit/validation.json
```

The validator imports the model into a clean scene and checks that import succeeded, mesh geometry exists, dimensions are non-zero, and the model contains materials. A passing report is not a substitute for visual review.

## Customize a character

1. Copy `configs/default_character.json` or edit `examples/dark_suit_purple_eyes.json`.
2. Change the palette, scale, hair, suit style, tie, eyes, and accessory options.
3. Run the generator again to a new output directory so prior results are preserved.
4. Review all preview views; fix obvious issues and rerun.

See [`SKILL.md`](SKILL.md) for the agent workflow and [`docs/pipeline.md`](docs/pipeline.md) for parameters, export details, and known limits.

## Run tests

The tests do not require Blender and check configuration validity and repository structure:

```bash
python -m unittest discover -s tests -v
```

To test actual generation and exports, run the Blender quick start on a machine with Blender installed. The CI workflow runs Python-side tests; it does not claim to validate a real Blender render.

## Repository layout

```text
SKILL.md                              Agent instructions
configs/default_character.json        Baseline character config
examples/dark_suit_purple_eyes.json   Reference-inspired configuration
scripts/blender/create_character.py   Blender procedural generator
scripts/blender/validate_character.py Import and asset validation
scripts/validate_config.py             Config validator (standard Python)
tests/                                Unit tests
.github/workflows/tests.yml           CI checks
docs/pipeline.md                      Workflow and limitations
```

## License

MIT. See [`LICENSE`](LICENSE).
