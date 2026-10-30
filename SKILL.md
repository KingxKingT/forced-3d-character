---
name: ai-3d-character-creator
description: Create, customize, inspect, and export real 3D characters from reference images. Prefer the free local Effigy image-to-3D pipeline through MCP for high-quality meshes; use the included procedural Blender builder only as a fallback or blockout.
---

# AI 3D Character Creator

Use this skill for real editable character meshes, especially reference-driven stylized game characters. The goal is a usable model, not just an image prompt or a rendered concept.

## Choose the right engine first

**Preferred for image-to-3D: Effigy (local, free, MIT application code).** If the Effigy MCP tools are connected, use them for reference-driven generation, cleanup, remeshing, UVs, PBR baking, rigging, validation, and export. Do not use Effigy Cloud, paid APIs, credits, or subscription services. Effigy is a separate project and is not bundled here.

Read [docs/local-ai-backend.md](docs/local-ai-backend.md) for hardware, licence, and setup requirements. Confirm the user's machine can run the selected model before asking it to download large model packs. Never trigger a model download without explaining its size and asking the user first.

**Fallback: included Blender script.** The procedural generator in `scripts/blender/create_character.py` makes a basic editable blockout from boxes, cones, and low-poly spheres. Use it only if Effigy is not installed/available or the task explicitly asks for a quick blockout. Do not present its output as comparable to a trained image-to-3D system.

## Preferred workflow with Effigy MCP

Effigy exposes tools such as `import_file`, `run_step`, `job_status`, `look`, `fit_check`, `validate`, and `export`. Use Effigy's own `describe_steps` for current parameters and its `effigy://guide` resource for full instructions; do not guess a tool argument if the installed version describes it differently.

### For a three-view turnaround sheet

The reference should contain the **same character, same pose, same scale, and same camera distance** in each panel. For a horizontal three-panel sheet ordered front, character-right profile, back:

1. Call `import_file(path=<absolute_path_to_reference_sheet>)`. It imports the picture and creates a prepared/cut-out version.
2. Call `run_step(asset_id, parent=<prepared_version>, step="prep", params={"op":"views","views":["front","right","back"]})`. Effigy splits the sheet into equal-width columns, creates the camera transforms, and checks that the character heights agree. If the panels are not equal-width, use separate cropped images and Effigy's `sources` option instead of allowing a bad split.
3. Call `run_step(asset_id, parent=<views_version>, step="trellis2", params={"weights":"faithful","multiview":true,"pipeline_type":"1024_cascade","steps":12,"texture_size":2048})`. This selects the multi-view Pixal3D route when the optional multi-view model pack is installed. Check the run result and the actual model variant in its metadata.
4. Use `look(asset_id, version)` to inspect the mesh from multiple angles before continuing. Compare the silhouette, head/body proportions, suit shape, hair mass, hands, and back against the reference. If wrong, try another seed or correct the source images; do not hide structural errors with textures.
5. Continue from the chosen model version: `clean` → `remesh` → `uv` → `bake`. For a stylized game character, try a moderate face budget first (for example 15k–25k); choose `quad` when editability/deformation matters, or `tri` for simpler game export. Check the remesh report and do not discard distinctive details.
6. Optionally run Effigy's `project` head/front pass when a sharper face from the reference is needed. Inspect the result; image projection can misalign if the camera or geometry is wrong.
7. For a rig, run `rig_fit` with the `mixamo52` template, then `fit_check`, and only then `rig_skin`. Read its QA output and fix markers when joints sit outside the mesh or deformation checks fail. Use Effigy's own step documentation for the skinning engine choices.
8. Run `validate`, fix all failures, then `export` to the requested profile (`godot`, `unreal`, `unity`, `web`, or `obj`). Keep `CREDITS.txt` and `LICENSES.json` beside the export.

If a call returns `status="running"`, poll `job_status(job_id)` until it is done. Effigy allows one heavy GPU job at a time; do not start concurrent generation/texture jobs. Each step writes a new version, so preserve the good parent and branch from it for experiments.

### Important rule for multi-view references

Do **not** run the single-image `canon` re-pose step after preparing multi-view cameras: changing only the front view breaks the agreement between front/side/back. If an A-pose is essential for rigging, prepare a matching A-pose image for every view first, or generate from the aligned reference and correct the rig markers in Effigy's rig editor. A T-pose turnaround can be used for shape generation, but rig-fit quality must be checked rather than assumed.

## Reference interpretation

Record what is visible and what is inferred. For a stylized dark-suited character, describe the silhouette, shoulder/waist ratio, head shape, facial landmarks, solid hair locks, jacket/lapel geometry, shirt/tie, trousers, shoes, palette, and any gold/violet accents. Preserve the user's reference design rather than inventing unrelated accessories.

For best image-to-3D conditioning, use one isolated character per view, a plain background, soft even 3D-style lighting, visible hands/feet, clear face, and consistent scale between views. Avoid panels with different poses, camera angles, crop sizes, or character heights; multi-view reconstruction fuses them into one shape.

## Workflow with the procedural fallback

1. Interpret style, body type, pose, outfit, palette, hair, eyes, accessories, target engine, and output formats.
2. Copy `configs/default_character.json` and edit values. The sample `examples/dark_suit_purple_eyes.json` is a style reference, not a learned model.
3. Run Blender's `scripts/blender/create_character.py` with the selected config.
4. Inspect front/side/back renders for silhouette, fingers, intersections, and face placement.
5. Run `scripts/blender/validate_character.py` and inspect its report.
6. State clearly that this is a procedural blockout with no trained image-to-3D inference, armature, or skin weights.

## Done means

- The chosen backend actually completed its geometry generation.
- The model was inspected from front, side, and back; do not claim a successful visual match based on file existence alone.
- Every requested export exists and is non-empty.
- Rigging claims are supported by a successful skeleton fit, skinning QA, and deformation checks.
- Model licences, attribution notices, and output provenance are preserved.
- Known limitations are stated honestly. Never claim a Blender render, export, or validation passed unless it completed and its output was inspected.
