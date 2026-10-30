# AI 3D Character Creator

An AI-agent skill and Blender fallback for creating **real, editable 3D characters**. For high-quality image-to-3D work, this project can drive a separate free, local AI pipeline through MCP instead of pretending a few Blender primitives are equivalent to a trained 3D model.

## Recommended engine: Effigy (free, local, open source)

For reference-driven characters like a front/side/back turnaround sheet, use [Effigy](https://github.com/SifuInTheShell/Effigy) as the primary generation backend.

- Effigy is MIT-licensed application code and runs locally/offline. No paid cloud, generation credits, subscription, or API key is required.
- It exposes its workflow to coding agents through an MCP server.
- Its pipeline includes image/turnaround input, 3D generation, mesh repair, triangle or quad remeshing, UV unwrap, PBR texture baking, automatic rig fitting/skinning, validation, and export.
- Its multi-view Pixal3D-MV route is designed for consistent front/side/back/left turnaround views.

This repository **does not copy or bundle Effigy**. It integrates through Effigy's documented MCP interface, preserving its own licence and model notices. Follow [the local AI backend guide](docs/local-ai-backend.md) for installation, hardware checks, and the exact three-view character workflow.

### Free does not mean lightweight

Effigy runs the models on your computer. Its current Windows guide targets Windows 11, an NVIDIA RTX GPU with 16 GB VRAM (12 GB is best-effort for the Fast path), 32 GB RAM recommended, and roughly 70–160 GB of disk depending on selected model packs. The optional four-view Pixal3D model pack is about 22 GB. Do not download the model packs until you have checked that the computer has enough GPU memory, RAM, and disk space.

The Effigy application is MIT-licensed, but each model has its own terms. Some model access requires a free Hugging Face account and acceptance of a royalty-free model licence; that is **not** a paid API, but it is not the same as an OSI open-source model licence. Keep the supplied attribution/licence notices with outputs. See [licensing and hardware notes](docs/local-ai-backend.md#licensing-and-costs).

## What is in this repository

- `SKILL.md`: instructions for an AI agent to choose the strongest available local workflow, inspect results, and avoid false quality claims.
- `scripts/blender/create_character.py`: a deterministic procedural Blender blockout/fallback. It is useful for simple stylized placeholders, **not** a replacement for image-to-3D AI.
- `scripts/blender/validate_character.py`: re-imports an export and checks for real geometry, bounds, and materials.
- `scripts/validate_config.py`: validates JSON settings without needing Blender.
- `configs/default_character.json` and `examples/dark_suit_purple_eyes.json`: editable fallback character specifications.
- `docs/local-ai-backend.md`: free local AI engine setup and multi-view workflow.
- `tests/` and `.github/workflows/tests.yml`: Python tests and continuous-integration checks.

## Fallback: procedural Blender blockout

Use this only when Effigy is unavailable or the machine cannot run its models. It creates a simple editable low-poly starting mesh from parameters; it does **not** infer anatomy or geometry from a reference image.

Requirements: Blender 4.2+ recommended and Python 3.10+ for configuration tests.

```bash
blender --background --factory-startup --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/dark-suit \
  --formats glb fbx obj \
  --render-views
```

Expected output includes `character.glb`, `character.fbx`, `character.obj`, `character_config.json`, `model_report.json`, and front/side/back preview PNGs.

Validate an export:

```bash
blender --background --factory-startup --python scripts/blender/validate_character.py -- \
  --file build/dark-suit/character.glb \
  --report build/dark-suit/validation.json
```

The validator checks structure only. It does not certify artistic quality, topology suitability, rigging, or animation deformation.

## Run checks without Blender

```bash
python -m compileall -q scripts tests
python scripts/validate_config.py configs/default_character.json
python scripts/validate_config.py examples/dark_suit_purple_eyes.json
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs these Python-side checks on Python 3.10, 3.11, and 3.12. It does not claim to have rendered a Blender model or run the optional Effigy backend.

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
  local-ai-backend.md
.github/workflows/tests.yml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Do not vendor third-party source, model weights, or assets without checking their licence and preserving their notices.

## License

This repository's code is MIT. Effigy and each model remain separate components under their own licences; no third-party model weights are bundled here. See [LICENSE](LICENSE) and [the integration notes](docs/local-ai-backend.md).
