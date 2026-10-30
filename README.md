# AI 3D Character Creator — Low-Spec Procedural Toolkit

A reusable modelling skill and Blender Python toolkit for building **real editable 3D characters locally**. The default path targets an 11th-generation Intel Core i3, 8 GB RAM, Intel integrated graphics, and no dedicated GPU. An external AI can plan and write code; Blender performs the actual mesh generation. No cloud 3D generator, paid API, local neural model, or large weight download is required.

## What changed in this improved version

The original primitive-based blockout has been refactored rather than discarded. The CLI and JSON configuration remain, while reusable geometry and validation are now independently testable.

- Shaped ring-lofted head, neck, tailored torso, trousers, and palms.
- Solid swept hair locks, continuous sleeves, jointed fingers, opposed thumbs, and shoe lasts.
- Fitted shirt, notched lapel, collar, tie, and pocket solids that follow the torso instead of floating in side view.
- Pure Python loft, sweep, panel, vector, and structural-inspection algorithms.
- Duplicate-face, zero-length-edge, winding, volume, component, planarity, semantic-part, and evaluated-triangle checks.
- Export re-import validation, editable `.blend` output, six inspection views, and an optional real Blender integration test.

The result is a **static editable multi-part low-poly character**. It is not automatically a production sculpt, rigged character, UV-mapped asset, animation-ready deformation mesh, or reference-matched likeness. See [VERIFICATION.md](VERIFICATION.md) for the exact tests and visual review performed on this delivered version.

## Repository layout

```text
AGENTS.md                        persistent project goals and agent instructions
SKILL.md                         universal modelling and quality-gate workflow
references/bmesh_cheatsheet.md   practical construction and defect-fix reference
configs/default_character.json
examples/dark_suit_purple_eyes.json
scripts/
  geometry_core.py              Blender-independent geometry and diagnostics
  hair_cards.py                 five-parameter CHARM-inspired hair-card mesh builder
  validate_config.py
  blender/
    mesh_tools.py               validated bpy/bmesh adapter and materials
    create_character.py         deterministic character generator
    validate_mesh.py            source-scene structural/semantic validation
    validate_character.py       export re-import validation
tests/
  test_config.py
  test_geometry_core.py
  test_blender_integration.py   skipped when Blender is unavailable
docs/
  pipeline.md
  low-spec-workflow.md
  testing.md
  visual-review.md
  architecture.md
  roadmap.md
  licences.md
```

## Requirements

- Python 3.10+ for configuration and pure geometry tests.
- Blender 4.2 LTS or a compatible later version for generation and Blender tests.
- No third-party Python packages are required by the generator.

Blender's Python API can change between versions. Test the exact installed version rather than assuming every operator or socket is identical.

## Generate a character

Run from the repository root. `--python-exit-code 1` is important: without it, Blender may return process status zero after a Python exception.

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/blender/create_character.py -- \
  --config examples/dark_suit_purple_eyes.json \
  --outdir build/dark-suit \
  --formats glb --save-blend --render-views
```

Outputs include `character.glb`, editable `character.blend`, `model_report.json`, the copied configuration, and front/side/back/three-quarter/head/hand previews. Use `--no-render` to suppress previews or omit `--save-blend` if only export files are needed. The generator clears the startup scene, so run it in a dedicated background process rather than an unsaved interactive scene.

The JSON controls name, scale, palette, hair style, facial options, outfit details, render resolution/samples, and exports. Hair styles include `manhwa_layered`, `side_swept`, and `short`; `manhwa_layered` is the current reference-driven benchmark, but its visual match still requires Blender renders and human review.

## Validate the source scene

```bash
blender --background build/dark-suit/character.blend --python-exit-code 1 \
  --python scripts/blender/validate_mesh.py -- \
  --report build/dark-suit/source-validation.json \
  --max-triangles 6000 --strict-budget \
  --require-watertight --require-single-component \
  --require-character-parts --strict-winding
```

The strict flags above match this generator's closed, single-component-per-object static design. They are not universal rules for every mesh. Open clothing, hair cards, and intentional multi-component objects need different flags. Non-planar polygons are reported separately because curved sweeps and body-fitted panels require triangulation review.

## Validate the exported file

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/blender/validate_character.py -- \
  --file build/dark-suit/character.glb \
  --report build/dark-suit/roundtrip-validation.json \
  --require-character-parts
```

For glTF delivery, also run the [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) and inspect the model in the intended viewer. Blender re-import alone cannot validate every glTF accessor, extension, or target-engine behaviour.

## Run tests

Python-only checks:

```bash
python -m compileall -q scripts tests
python scripts/validate_config.py configs/default_character.json
python scripts/validate_config.py examples/dark_suit_purple_eyes.json
python -m unittest discover -s tests -v
```

Real Blender integration test:

```bash
BLENDER_BIN=/path/to/blender python -m unittest discover \
  -s tests -p test_blender_integration.py -v
```

If `blender` is on PATH, `BLENDER_BIN` is optional. `REQUIRE_BLENDER=1` documents that a runtime is required; `SKIP_BLENDER_RENDER=1` shortens the test while retaining generation, strict validation, and GLB round trip. See [docs/testing.md](docs/testing.md) for the meaning and limits of each test class.

## Visual review is still mandatory

Structural success does not establish good anatomy, resemblance, attractive silhouettes, or correct clothing fit. Inspect the rendered views using [docs/visual-review.md](docs/visual-review.md). Record unperformed checks as `not_tested`. If no reference image was supplied, do not claim a reference comparison.

## Low-spec and optional high-spec paths

Use small meshes, solid materials, modest previews, one character at a time, and no simulation-heavy default. See [docs/low-spec-workflow.md](docs/low-spec-workflow.md). Any neural or high-spec backend documented elsewhere is optional and separate; it is not needed by this generator.

## Licence and third-party work

Repository code is MIT. No third-party character bases, model weights, or asset packs are bundled. Optional projects and CC0 asset routes are listed with their separate licence boundaries in [docs/licences.md](docs/licences.md) and [REFERENCES.md](REFERENCES.md).
