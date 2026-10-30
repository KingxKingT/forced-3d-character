# Low-Spec Project Architecture

## Design decision

Preserve the existing command-line generator, JSON schema, export conventions, and honest documentation. Improve the weakest geometry and validation behind those contracts. A wholesale rewrite would add risk without automatically improving the character.

## Boundaries

```text
JSON config
   |
   v
validate_config.py --------------- Python-only configuration tests
   |
   v
create_character.py -------------- semantic character assembly, scene, export
   |
   +--> geometry_core.py --------- pure vectors, lofts, paths, sweeps, panels, metrics
   |         |                    no bpy/bmesh; deterministic lists in/out
   |         +--> test_geometry_core.py
   |
   +--> blender/mesh_tools.py ---- validated Mesh.from_pydata, BMesh details,
   |                               materials, bevels, semantic metadata
   |
   +--> character.blend + GLB/FBX/OBJ + model_report.json + previews
              |
              +--> validate_mesh.py -------- source-scene structure/semantics
              +--> validate_character.py --- export re-import/round trip
              +--> visual checklist -------- actual image inspection, separate gate
```

## Why pure geometry matters

`geometry_core.py` accepts and returns ordinary Python arrays. Unit tests can prove ring correspondence, cap winding, sweep sampling, stable frames, duplicate detection, and component metrics in milliseconds without starting Blender. This is stronger than reading source code and asserting that a preferred API name appears. It also lets an AI agent iterate on geometry logic with a fast feedback loop.

The pure layer is not a full geometry kernel. It deliberately implements a small, useful set of operations rather than recreating Blender. BMesh remains appropriate for connectivity editing and selected procedural primitives; Blender remains responsible for objects, modifiers, materials, rendering, import, and export.

## Static component topology

The included character uses intentional closed component meshes that may overlap at joints and clothing layers. This is a legitimate lightweight choice for a static stylized asset: each object remains easy to edit, and the generator does not pretend that intersecting sleeves and torso form a deformation-ready continuous skin. `--require-watertight` and `--require-single-component` apply per object in the integration test.

A future animation path needs different acceptance criteria: continuous or deliberately skinned topology, joint loops, weights, range-of-motion tests, and target-engine validation. Automatic retopology alone cannot infer those requirements.

## Semantic manifest

Every generated mesh receives `character_part`. The default required groups are `head`, `face`, `hair`, `clothing`, `hands`, `legs`, and `shoes`. Source validation checks that parts exist; glTF export includes custom extras so the round-trip test can check metadata preservation where the format supports it. The manifest detects omissions such as “the script ran but no hands were generated”; it does not judge whether the hands look natural.

## Determinism and editability

No random sampling is used by the current generator. Parameters and configuration determine the output. Objects retain useful names and separate materials. Optional `character.blend` output preserves direct editability; export uses evaluated modifiers. Scaling edits mesh coordinates and bevel widths directly rather than relying on repeated context-sensitive transform operators.

## Resource policy

The default scene uses solid materials, flat shading, no image textures, no simulation, and no dense subdivision. The triangle budget is configurable and evaluated modifier counts are reported. Preview resolution and samples belong to the configuration. Actual memory and render time must be measured on the target computer; this architecture does not invent a fixed hardware benchmark.

## Extension points

1. Add new profiles and control points in character assembly without changing the Blender adapter.
2. Add pure geometry algorithms with unit tests before connecting them to `bpy`.
3. Add semantic validators for new part types instead of overloading triangle count as a quality metric.
4. Add an optional licensed base-character adapter behind a separate configuration path; do not make external assets mandatory.
5. Add deformation topology and rigging as a distinct pipeline with its own tests, not as a flag on the current static generator.
