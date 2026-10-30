# AI 3D Character Creator

A procedural Blender project and agent skill for creating **real, editable low-poly 3D character meshes** from structured character specifications. It is intended for stylized game characters—especially a dark-suited character with black hair, violet eyes, and subtle gold details—not just image prompts.

## What is included

- `SKILL.md`: instructions for an AI agent to plan, generate, inspect, validate, and iterate on character assets.
- `scripts/blender/create_character.py`: procedural Blender mesh/material creation, export, and front/side/back preview rendering.
- `scripts/blender/validate_character.py`: re-imports an export and checks for real geometry, bounds, and materials.
- `scripts/validate_config.py`: validates JSON settings without needing Blender.
- `configs/default_character.json` and `examples/dark_suit_purple_eyes.json`: editable character specifications.
- `tests/` and `.github/workflows/tests.yml`: Python tests and continuous-integration checks.
- `docs/pipeline.md`: workflow notes, settings, and known constraints.

## Important capability boundary

This is a deterministic procedural model builder, **not** a neural text-to-3D model. It creates a customizable low-poly starting character from Blender geometry. An AI agent can translate a reference into a configuration and iterate on renders, but automated geometry still needs visual review.

The character is **not rigged** and has no armature, skin weights, facial rig, or hand-authored production UV workflow. Do not call it animation-ready or production-ready. The Python tests do not prove that Blender exports or renders; those checks need a machine with Blender installed.

## Requirements

- Blender 4.2+ recommended.
- Python 3.10+ for configuration validation and unit tests.
- Optional: a GLB/GLTF viewer or game engine for inspecting exported assets.

Check Blender availability:

```bash
blender --version
```

## Quick start

Run these commands from the repository root:

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/dark-suit \
  --formats glb fbx obj \
  --render-views
```

Expected output:

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

The available exporters depend on your Blender installation. The script exits with an error if a requested export does not complete or produces an empty file.

Validate the generated GLB:

```bash
blender --background --factory-startup --python scripts/blender/validate_character.py -- \
  --file build/dark-suit/character.glb \
  --report build/dark-suit/validation.json
```

This validates import and basic structure; it does not certify artistic quality, topology, UVs, rigging, or animation deformation.

## Configure a character

1. Copy `configs/default_character.json` or edit `examples/dark_suit_purple_eyes.json`.
2. Change supported palette colors, overall scale, hair style, facial feature flags, outfit details, render resolution, and export formats.
3. Generate to a new output directory so earlier results are preserved.
4. Inspect the front, side, and back previews. Pay special attention to hands, silhouette, clothing intersections, and facial placement.
5. If a required style, pose, or feature is not supported by the current generator, extend the code and add tests rather than setting an option the generator ignores.

Supported values are validated before generation. Current style is `low_poly_stylized`, current pose is `t_pose`, supported hair styles are `side_swept` and `short`, and output formats are GLB, GLTF, FBX, and OBJ.

## Run checks without Blender

```bash
python -m compileall -q scripts tests
python scripts/validate_config.py configs/default_character.json
python scripts/validate_config.py examples/dark_suit_purple_eyes.json
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs these Python-side checks on Python 3.10, 3.11, and 3.12. It does not claim to have rendered a Blender model.

## Repository layout

```text
SKILL.md
configs/
examples/
scripts/
  validate_config.py
  blender/create_character.py
  blender/validate_character.py
tests/
docs/
.github/workflows/tests.yml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for test expectations and Blender validation guidance.

## License

MIT. See [LICENSE](LICENSE).
