---
name: ai-3d-character-creator
description: Create, customize, export, and validate stylized low-poly 3D characters with Blender. Use when an agent needs a real editable mesh and deliverable assets (GLB/GLTF, FBX, OBJ), not just a prompt or a rendered concept image.
---

# AI 3D Character Creator

Use this skill to create an editable, stylized character in Blender, especially game-ready low-poly humans with clear silhouettes, intentional facial features, readable clothing layers, and optional front/side/back preview renders.

## Important capability boundary

The included generator is a deterministic procedural Blender model builder. It creates a useful low-poly starting character from a JSON configuration; it is not a neural text-to-3D model and does not infer a perfect mesh from a reference image on its own. When reference-image understanding tools are available, first derive a short visual specification from the reference, then encode the measurable choices in the JSON configuration and, when needed, extend the Blender script.

## Workflow

1. **Interpret the request.** Record style, body type, pose, outfit, palette, hair, eyes, accessories, target engine, and file formats. Keep a distinction between visible reference facts and assumptions.
2. **Create a configuration.** Copy `configs/default_character.json`; edit values rather than hard-coding new character-specific choices into the script. The sample `examples/dark_suit_purple_eyes.json` targets a polished low-poly man in a dark suit with black hair and violet eyes.
3. **Generate in Blender.** Run the script using Blender's bundled Python:

   ```bash
   blender --background --factory-startup --python scripts/blender/create_character.py -- \
     --config examples/dark_suit_purple_eyes.json --outdir build/dark-suit --formats glb fbx obj --render-views
   ```

4. **Inspect the result.** Open `build/dark-suit/character.glb` in Blender or the target game engine. Review `preview_front.png`, `preview_side.png`, and `preview_back.png`. Check silhouette, hand/finger readability, clothing intersections, facial symmetry, and scale. Procedural models need visual review; automated checks do not certify art quality.
5. **Validate the export.** Run Blender's `--background --python scripts/blender/validate_character.py -- --file build/dark-suit/character.glb --report build/dark-suit/validation.json`. Validate output existence and inspect the report before calling the task finished.
6. **Iterate deliberately.** Change a small set of configuration values per iteration. Use image renders to compare proportions and colors. If a required feature cannot be expressed in the config, modify the generator with reusable functions rather than one-off geometry that breaks future variants.
7. **Deliver files and instructions.** Include requested model exports, preview views, the exact config used, and any limitations. Never claim a Blender render, export, or validation passed unless the command completed and its output was inspected.

## Modeling guidelines

- Use a consistent human scale: feet near Z=0; head above torso; shoulders wider than waist; arms symmetric around X=0; face toward +Y.
- Build separate readable layers for jacket, shirt, collar, tie, lapels, trousers, shoes, hair, eyes, brows, ears, and hands. Avoid hiding all anatomy under a single box-like mesh.
- Prefer controlled low-poly forms with flat or weighted shading. Use beveled boxes and low-subdivision ico spheres for a stylized aesthetic, avoiding random faceting that harms the silhouette.
- Hands are a high-risk area. Keep palms oriented with the thumb on the anatomically appropriate side, fingers separately defined and slightly tapered, and maintain believable spacing. Use a standard T-pose unless the request specifies otherwise.
- Use named materials and objects, descriptive collection names, sensible origins, and consistent units. Apply transforms before export where appropriate.
- For game use, provide GLB as the simplest portable default. FBX may be useful for common engines; OBJ is geometry/material oriented and does not preserve every modern material feature.
- Do not advertise the output as animation-ready or production topology unless armature, weights, deformation tests, UVs, and topology have actually been implemented and tested.

## Configuration

The configuration supports a character name, overall scale, color palette, facial options, hair style, outfit, and export/render options. See `configs/default_character.json` and `docs/pipeline.md`.

## Done means

- The Blender process exited successfully.
- Every requested export exists and is non-empty.
- The validation report exists and contains no fatal checks.
- Preview renders were visually inspected when rendering was requested.
- Known limitations are stated honestly (for example, no armature or hand-authored UV layout).
