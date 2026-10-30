# AI 3D Character Creator

A universal low-poly modeling skill and Blender code toolkit. It is designed to work on modest PCs by default: an AI plans the shape and writes deterministic Blender Python, while Blender builds the actual mesh locally. No local neural image-to-3D model is required.

## Default target: modest hardware

The baseline target is an 11th-gen Intel Core i3, 8 GB RAM, and Intel integrated graphics.

- No local diffusion, TRELLIS, Pixal3D, Hunyuan3D, or large local LLM required.
- Use direct mesh data and BMesh operations for procedural geometry.
- Use a small number of objects, simple solid materials, flat shading, and modest previews.
- Work in stages: silhouette blockout → important forms → topology checks → multi-view inspection → export.

See [docs/low-spec-workflow.md](docs/low-spec-workflow.md).

## What is included

- `SKILL.md`: universal low-poly workflow with hardware tiers and quality gates.
- `references/bmesh_cheatsheet.md`: correct examples for explicit meshes, BMesh, pyramid hair, mirroring, flat shading, and materials.
- `scripts/blender/validate_mesh.py`: structural scene checks for geometry, non-manifold edges, degenerate faces, loose vertices, triangle budgets, shading, and materials.
- `scripts/blender/create_character.py`: an existing procedural character blockout generator.
- `scripts/blender/validate_character.py`: validates that an exported model can be re-imported and contains geometry.
- `scripts/validate_config.py`: JSON config validation.
- `docs/kimi-style-fact-check.md`: fact-check of the proposed "Kimi-style" rules.
- `docs/local-ai-backend.md`: optional Effigy backend for stronger hardware.

## The important distinction

A skill cannot turn every AI into Kimi or guarantee professional results. It can give different AI models a consistent plan, code templates, and validation steps. The model's visual reasoning and coding capabilities still matter.

BMesh is useful, but it does not automatically make topology clean. The workflow combines explicit geometry, validation, and visual iteration. The fact-check explains why banning every `bpy.ops` call, every n-gon, or every model over 1,500 triangles is not technically sound.

## Quick start: procedural low-poly modeling

Open Blender and use its Scripting workspace, or run a saved scene through Blender's background mode.

Check the mesh in the current scene:

```bash
blender --background character.blend --python scripts/blender/validate_mesh.py -- \
  --report build/mesh-report.json --max-triangles 6000
```

Use `--strict-budget` only when the project has an agreed triangle cap. Use `--require-watertight` only for closed solids; open surfaces can intentionally have boundary edges.

The existing configurable blockout generator can still be run as a starting point:

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/dark-suit \
  --formats glb
```

For reliable output quality, inspect the generated result from front, side, and back rather than assuming a successful script means a good model.

## Optional high-spec AI generation

[Effigy](https://github.com/SifuInTheShell/Effigy) is documented as an optional local AI image-to-3D pipeline for stronger hardware. It is not required for the low-spec workflow. Its current guide targets Windows 11, an NVIDIA RTX GPU with 16 GB VRAM for the full character path, 32 GB RAM recommended, and 70–160 GB disk depending on the selected model packs. The four-view model pack is about 22 GB additional.

Do not install Effigy, TRELLIS.2, Pixal3D multi-view, or other large model packs on the baseline i3/8 GB integrated-graphics machine. See [local AI backend notes](docs/local-ai-backend.md) first.

## Run Python checks

```bash
python -m compileall -q scripts tests
python scripts/validate_config.py configs/default_character.json
python scripts/validate_config.py examples/dark_suit_purple_eyes.json
python -m unittest discover -s tests -v
```

CI checks Python syntax and configuration tests. They do not run Blender or validate the live Blender mesh script; that requires Blender installed.

## Repository layout

```text
SKILL.md
references/
  bmesh_cheatsheet.md
configs/
examples/
scripts/
  validate_config.py
  blender/
    create_character.py
    validate_character.py
    validate_mesh.py
docs/
  low-spec-workflow.md
  kimi-style-fact-check.md
  local-ai-backend.md
tests/
.github/workflows/tests.yml
```

## License

This repository's code is MIT. Effigy and any future third-party code, checkpoints, and asset packs remain separate components under their own licences. No third-party model weights are bundled here.
