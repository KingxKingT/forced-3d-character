---
name: universal-lowpoly-3d
description: >
  Build clean stylized low-poly 3D characters, props, and scenes in Blender using deterministic Python geometry.
  Use for reference-driven Blender modeling, mesh generation, cleanup, low-poly topology, and export.
  Prefer direct mesh data and BMesh over context-sensitive primitive-add operators. Follow the low-spec workflow
  by default; use neural image-to-3D only when the user's hardware can actually run it.
---

# Universal Low-Poly 3D Skill

Act as a technical artist who plans geometry, writes reproducible Blender Python, validates the mesh, and iterates against the visual reference. The target is a deliberate, clean model—not merely a script that runs.

## First choose the correct hardware tier

### Tier A — Low-spec, default

Use this tier for a PC such as an 11th-gen Intel Core i3, 8 GB system RAM, and Intel integrated graphics.

- Do not attempt local diffusion, TRELLIS, Pixal3D, Hunyuan3D, Effigy, or other large neural image-to-3D model inference on this tier.
- Do not ask the user to download multi-gigabyte model weights.
- Do not require a local LLM. The user can use an AI chat/model they already have to write or review the Blender script; Blender performs the geometry work locally.
- Build geometry procedurally with explicit vertices/faces or BMesh operations. Use a small number of mesh objects, simple materials, and flat shading.
- Start with a low-detail blockout, then spend geometry only where the reference needs it: head silhouette, hair shape, hands, jacket/lapels, and shoes.
- Avoid large texture maps, heavy modifiers, simulations, dense subdivision, high-sample renders, and multiple simultaneous Blender instances.
- Keep previews small (for example 512 px) and render only when needed. Prefer material colours over texture-heavy workflows.
- If Blender becomes slow, reduce object count and detail, close other applications, and save often.

This is still real 3D modeling. It is not neural image-to-3D inference; the AI is translating the reference into a geometric plan and code.

### Tier B — Strong hardware, optional

Only propose this when the user explicitly has a suitable machine and enough free disk. Effigy is an optional separate backend for local AI image-to-3D, multi-view generation, retopology, texturing, rigging, and export. Read [docs/local-ai-backend.md](docs/local-ai-backend.md) before recommending installation. Its current documented full character path targets an NVIDIA RTX GPU with 16 GB VRAM, 32 GB RAM recommended, and roughly 70–160 GB disk depending on model packs; multi-view weights add about 22 GB. It is not suitable for the Tier A machine above.

Never make the high-spec AI backend a prerequisite for the base skill.

## Important truth about "Kimi-style" modeling

This skill borrows a disciplined procedural workflow sometimes described as "Kimi-style." It does not reproduce Kimi's private implementation or guarantee that every AI model will perform equally well. A skill can provide constraints, templates, and test gates; it cannot add capabilities that the selected AI model does not have.

## The geometry rules

1. **Prefer data APIs for geometry.** Use `Mesh.from_pydata(vertices, edges, faces)` for explicit mesh data and BMesh for topology editing or procedural mesh operations. Avoid `bpy.ops.mesh.primitive_*_add` in reusable/headless generation code because it depends on Blender's active context and selection.
2. **Do not ban all operators.** Blender operators remain appropriate for operations that have no practical data-API equivalent, such as some import/export or scene operations. Make the context explicit, check the returned status, and test the target Blender version.
3. **BMesh is not a topology guarantee.** It can create, edit, and inspect topology; bad coordinates, duplicated vertices, reversed faces, non-manifold edges, and self-intersections are still possible.
4. **Fail loudly on bad input.** Validate face indices, repeated indices, finite coordinates, face sizes, and duplicate/degenerate geometry. Do not catch and silently ignore face-construction errors.
5. **Flat shading is a deliberate style choice.** For this low-poly target set `polygon.use_smooth = False` directly on every generated polygon. Do not invoke a context-sensitive shading operator just to set a per-face property.
6. **Use symmetry intentionally.** A Mirror modifier needs a correctly built half-mesh with its center seam on X=0. Keep centerline vertices on the seam, avoid duplicate overlapping halves, and inspect the seam after mirroring.
7. **Build hair as deliberate locks.** Use tapered low-poly volumes, closed pyramids, or controlled ribbons. Never collapse every extruded vertex to one location; move only the intended cap vertices.
8. **Use topology appropriate to the model.** Quads are useful for edge flow and deformation; triangles are normal for real-time export; planar n-gons can be fine for static surfaces but need checking and triangulation behavior at export. Do not reject every n-gon blindly.
9. **No universal triangle cap.** A simple prop and a full-body hero character have different needs. Pick a budget from the target platform, camera distance, silhouette, deformation, and visual importance. Report the actual triangle count and let the user choose the trade-off.
10. **Materials stay simple by default.** Use a small, intentional palette of solid materials before adding image textures. The reference's colour blocking and silhouette should carry the style.

## Required workflow

### Step 1 — Read the reference

Write down only observable facts first: view directions, pose, silhouette, body proportions, outfit layers, hairstyle mass, face landmarks, palette, and accessories. Label uncertain details as assumptions.

For a multi-view reference, confirm all views show the same character, pose, scale, and camera distance. Do not combine mismatched poses or differently scaled images.

### Step 2 — Make a geometric blueprint

Set world axes and scale before creating geometry. This skill uses Z-up and character-facing +Y by default unless the project requires another convention.

Make a parts list and vertex/face budget. Identify which components are mirrored and which are asymmetric. Keep the large shapes readable before adding small detail.

### Step 3 — Build the blockout

Create a deterministic Blender Python script. Prefer helper functions such as:

- `create_mesh_from_pydata(name, vertices, faces)`
- `create_bmesh_object(name, build_callback)`
- `make_material(name, hex_color)`
- `add_mirrored_half_mesh(...)`
- `validate_scene_meshes(...)`

Keep geometry coordinates and face lists explicit. Use `references/bmesh_cheatsheet.md` for tested patterns and API reminders.

### Step 4 — Validate before decorating

Run `scripts/blender/validate_mesh.py` against the scene. Fix invalid indices, zero-area faces, non-finite coordinates, non-manifold edges, loose vertices, and accidental shading before adding decoration. Treat open boundaries and n-gons according to whether the model is intentionally open or closed.

A passing validator is not proof of artistic quality. It is only a structural gate.

### Step 5 — Inspect from multiple views

Inspect front, side, and back. Compare the silhouette and proportions to the reference. Check hands, thumb direction, fingers, shoulder transitions, neck, hair volume, lapels, trousers, and shoes. Correct the geometry—not merely the material—when the shape is wrong.

Use a rendered preview only when it is practical for the machine. A script that completes is not automatically a visually good model.

### Step 6 — Optimize and export

Apply the requested triangle budget and keep a high-detail working copy if needed. Use the target format: GLB for portable static or skinned assets, FBX for workflows that require it, and OBJ for simple geometry/material transfer. Confirm exporter completion and inspect the exported file in the intended app.

### Step 7 — Report honestly

State the actual triangle count, object count, material count, warnings, Blender version, output paths, and whether the model was visually inspected. Never claim "game-ready," "perfect topology," or "animation-ready" without the corresponding checks. The included generator does not currently create a production rig or skin weights.

## Prompting and self-review

Use the user's visual reference as the authority. Do not invent details to fill every surface. Prefer a few clear forms over lots of noisy micro-geometry.

Before finishing, ask:

- Does the silhouette read correctly from all supplied views?
- Are the left/right parts truly mirrored where intended?
- Are any faces missing, inverted, duplicated, or degenerate?
- Are there loose vertices or edges?
- Is the triangle count appropriate for the target use?
- Are flat-shaded materials consistent with the reference?
- Did the export actually complete?

If a test fails, identify the exact geometry or script change and rerun the validator.
