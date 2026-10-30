# Testing and Evidence Levels

“Tests passed” is ambiguous unless the test class is named. This project separates pure algorithms, Blender runtime behaviour, export integrity, and visual quality.

## 1. Python-only tests

```bash
python -m compileall -q scripts tests
python -m unittest discover -s tests -v
```

These tests cover JSON validation and `geometry_core.py`: loft/sweep construction, endpoint sampling, stable frames, malformed inputs, open/closed meshes, duplicate faces, zero-length edges, inconsistent winding, negative volume, disconnected components, and non-planar quads. The Blender integration module appears as `skipped` when no Blender executable is available; a skip is not a runtime pass.

## 2. Real Blender runtime test

```bash
BLENDER_BIN=/path/to/blender python -m unittest discover \
  -s tests -p test_blender_integration.py -v
```

The test uses `--python-exit-code 1`, generates a character, saves `.blend`, exports GLB, runs strict source-scene checks, re-imports the GLB, and renders six views. `SKIP_BLENDER_RENDER=1` skips only the render assertions. `REQUIRE_BLENDER=1` is a declaration for automation that a runtime is required; CI provisioning must still install Blender or supply `BLENDER_BIN`.

Strict source validation includes closed components, one connected component per object, semantic parts, positive orientation, and a 6,000-evaluated-triangle project budget. These are appropriate to this generator, not universal rules for all models.

## 3. Manual/export checks

Run `validate_mesh.py` on the source and `validate_character.py` on every requested export format. Use the Khronos glTF Validator for GLB/glTF delivery and inspect the actual target viewer or engine. FBX and OBJ need their own round trips; a GLB pass says nothing about those files. Counts can change because of modifier evaluation, triangulation, normals, and attribute splits.

## 4. Actual visual-quality test

A visual test requires images or direct scene inspection and a reviewer. Follow [visual-review.md](visual-review.md), record the exact inspected files, and list unresolved issues. No current unit test computes attractiveness, reference similarity, or animation quality. If a reference image is absent, reference comparison is `not_tested`, not `passed`.

## 5. Animation/performance tests are separate

The current suite does not test skin weights, joint deformation, facial animation, UVs, draw calls, engine frame rate, memory on the user's i3/8 GB computer, or every Blender version. Those claims require dedicated evidence. Do not convert a successful static GLB round trip into “game-ready” or “animation-ready.”

## Reporting template

```json
{
  "python_tests": {"status": "not_run", "passed": 0, "failed": 0},
  "blender_runtime": {"status": "not_run", "blender_version": null},
  "export_roundtrip": {"status": "not_run", "formats": []},
  "visual_review": {"status": "not_tested", "reference_comparison": "not_tested"},
  "animation": {"status": "not_tested"},
  "target_hardware_performance": {"status": "not_tested"}
}
```

Replace `not_run` only with actual results and retain failure logs. Never silently remove a failing or skipped test from the report.
