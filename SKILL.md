---
name: universal-lowpoly-3d
description: >
  Plan, build, inspect, validate, and export real editable low-poly characters and props locally in Blender.
  Use for reference-driven modelling, deterministic Blender Python, BMesh, procedural lofts/sweeps, mesh validation,
  multi-view visual iteration, and low-spec character workflows. Blender performs geometry generation locally;
  no cloud 3D generator, paid API, large local model, or dedicated GPU is required by the default path.
---

# Universal Low-Poly 3D Skill

Act as a technical artist, not a script-completion machine. Translate observable requirements into a geometric plan, write deterministic local Blender Python, inspect actual geometry and renders, and report remaining defects honestly. A prompt or this skill cannot make every AI model equally capable: visual reasoning, coding ability, tool access, and the available reference still constrain the result.

## Non-negotiable default constraints

The baseline is an 11th-generation Intel Core i3, 8 GB RAM, Intel integrated graphics, and no dedicated GPU.

- No paid APIs, subscriptions, generation credits, or cloud-based 3D-generation dependency is introduced by this repository.
- No large local AI models, diffusion models, GPU-heavy image-to-3D models, or multi-gigabyte weight downloads are required.
- Use Blender and lightweight Python tools. The actual mesh generation must run locally in Blender.
- An external assistant may reason and write Blender Python through a service the user already has; that assistant is not the geometry engine.
- A stronger local/neural workflow is optional and must never become a prerequisite. Check current hardware and licences before recommending one.
- Do not start large downloads automatically. Do not claim to have run Blender, rendered, or inspected a model unless that actually happened.

## 1. Establish the request and evidence

Record the intended use (static render, game asset, further sculpting, or animation), target style, pose, output formats, triangle/draw-call priorities, and Blender version. Separate these evidence classes:

| Evidence | What to do |
|---|---|
| Supplied image/reference | Describe only visible silhouette, landmarks, layers, colours, and camera views; mark occluded details as assumptions. |
| Text-only request | Convert adjectives into measurable forms and proportions; do not pretend an image was supplied. |
| Multiple views | Confirm identity, pose, scale, and camera consistency before combining information. |
| Missing or unreadable reference | Continue only with an explicit text-based assumption list, or request the reference if resemblance is essential. |

Never claim reference-image comparison when no reference image was available. “Attractive,” “anime,” and “professional” are not geometric specifications; resolve them into head/body ratios, face planes, hair masses, clothing shapes, and silhouette criteria.

## 2. Write a geometric blueprint before code

Use a documented right-handed coordinate system. This project uses **Z-up and character-facing +Y**, with left/right mirrored across X=0. Choose real-world scale and a ground plane. Specify:

1. Overall height, head-to-body ratio, shoulder/waist/hip widths, limb lengths, hand and foot sizes.
2. A semantic part manifest such as `head`, `face`, `hair`, `clothing`, `hands`, `legs`, and `shoes`.
3. Symmetric versus intentionally asymmetric components.
4. Closed solid components versus intentional open surfaces; these have different validation rules.
5. Topology needs. Static multi-part geometry is not automatically suitable for deformation.
6. A project-specific triangle and object budget, with extra density reserved for silhouette-critical areas.
7. Camera views and acceptance criteria before detail work begins.

Do not rewrite a working project merely to appear sophisticated. Preserve stable entry points and configuration contracts, isolate reusable algorithms, and replace the weakest visual components first.

## 3. Select the simplest suitable modelling method

| Method | Best use | Main caution |
|---|---|---|
| Explicit `Mesh.from_pydata` | Deterministic custom panels, rings, low-poly solids | Validate arrays before Blender; it does not invent good edge flow. |
| BMesh | Topology edits, connectivity inspection, procedural primitives | BMesh is a toolset, not a cleanliness guarantee. |
| Ring lofts | Heads, necks, torsos, trousers, palms, shoe sections | Ring correspondence, winding, and profile transitions need design. |
| Swept volumes | Fingers, sleeves, curved shoe lasts | Frame flips, taper collapse, and excessive sampling create defects. |
| Five-parameter hair cards | Stylized locks described by XYZ + width + thickness guides | Hand-authored guides still require reference fitting; a control-point method does not infer a hairstyle by itself. |
| Solid panel extrusion | Collars, lapels, ties, eye shapes | Fit panels to the underlying body; flat floating panels fail side review. |
| Curves/bevels | Interactive strand or piping authoring | Convert and inspect final mesh; radius/twist can change the silhouette. |
| Geometry Nodes | Reusable parametric scattering or profile workflows | Adds another mental/runtime model; optional, not mandatory. |
| Sculpt/retopology | Organic art direction and later deformation preparation | Not a substitute for deliberate landmarks; automatic retopology misses semantic loops. |
| Shared base + morphs | Families of reusable characters | Requires licensed base data and careful fitting; optional asset-backed path. |

Prefer data APIs in reusable geometry helpers. Avoid context-sensitive `bpy.ops.mesh.primitive_*_add`, but do not ban all `bpy.ops`: import/export and scene operations may appropriately use operators when context, return status, and output files are checked.

## 4. Build large forms before detail

Work in this order unless evidence supports another priority:

1. Grounded body silhouette and proportions.
2. Head/jaw/cheek/forehead planes and neck transition.
3. Hair scalp mass and a small number of designed locks.
4. Tailored body-derived clothing shells and major panels.
5. Shoulder/arm transitions, palms, four jointed fingers, and opposed thumb per hand.
6. Trouser breaks and shaped shoe lasts/soles.
7. Facial features and small accessories only after the large forms read correctly.

Use positive small tip radii instead of collapsed zero-radius rings. Maintain consistent ring sizes within a loft. For horizontal rings ordered counter-clockwise from +Z, use reversed start caps, forward end caps, and side quads `(lower_i, lower_next, upper_next, upper_i)`. Recalculate/inspect normals and test signed volume on closed components.

### Difficult-part rules

- **Head/face:** An ellipsoid with primitive eyes is only a blockout. Shape chin, jaw, cheeks, temples, and forehead deliberately; align facial features to the actual front surface and inspect the profile.
- **Hair:** Build a scalp-following cap plus solid tapered locks with control points, width, thickness, and stable frames. The lightweight `scripts/hair_cards.py` module implements a five-parameter card representation inspired by CHARM. The current presets use hand-authored guides; do not claim neural image-to-hair inference. Avoid random spikes, collapsed extrusions, and dozens of noisy strips.
- **Hands:** A palm cube with straight sticks is incomplete. Use a shaped palm, separated jointed fingers with varied lengths, and an opposed thumb. Check left/right direction and intersections.
- **Clothing:** Derive shells from body sections. Use explicit collar/lapel/tie solids for the lightweight path. Fit every panel in side view. Do not require cloth simulation for a static tailored suit.
- **Animation topology:** Shoulder, elbow, eyelid, mouth, knuckle, and hip deformation require intentional loops and skinning tests. A closed static mesh or automatic quad remesh does not establish them.

## 5. Keep generation deterministic and editable

Separate pure geometry from Blender adapters. Reusable functions should accept and return ordinary vertex/face arrays where practical; keep `bpy` object creation, materials, modifiers, import/export, and rendering at the adapter boundary. Use fixed parameters or a recorded seed. Name objects semantically and attach a `character_part` property.

Validate source arrays before `Mesh.from_pydata`: finite XYZ coordinates, valid indices, at least three distinct indices per face, and no repeated face indices. `Mesh.validate()` may correct data; if it changes the mesh, reject and fix the source rather than silently accepting an unintended repair. Set `polygon.use_smooth = False` directly for this flat-shaded style.

Keep an editable `.blend` when requested. Preserve unapplied working modifiers where useful and export an evaluated copy. Do not join every object merely to reduce the reported count; readability and selective editing matter.

## 6. Apply separate quality gates

### Gate A — Python-only tests

Test configuration parsing and pure geometry without Blender: ring counts, sweep endpoints, stable frames, winding, duplicate faces, zero-length edges, degenerate faces, disconnected components, and malformed inputs. Source-text assertions such as “this function name appears” are not geometry tests.

### Gate B — Blender runtime and structure

Run with `--python-exit-code 1` so script exceptions produce a failing process. Verify actual artifacts. Check non-finite coordinates, invalid/degenerate geometry, duplicate faces, zero-length edges, edge face counts, winding, signed volume where meaningful, connected components, n-gon planarity, materials, semantic parts, and base/evaluated triangle counts.

Boundary edges are not universally errors. Require watertightness only for components intended to be closed. N-gons are not universally bad; inspect planarity and triangulation. Triangle caps are project-specific.

### Gate C — Export round trip

Re-import GLB/glTF/FBX/OBJ and compare geometry, dimensions, materials, semantic metadata where supported, and evaluated triangle counts. For glTF delivery, additionally run the Khronos glTF Validator when available and inspect in the target viewer. File existence is not export validation. Source-scene and exported vertex counts can legitimately differ because of normals, seams, attributes, modifiers, and triangulation.

### Gate D — Actual visual-quality review

Render or inspect front, side, back, and three-quarter views, plus close-ups of the head and hands when important. Record who/what performed the review and which images were inspected. Check silhouette, proportions, profile, alignment, intersections, hair mass, hand anatomy, clothing fit, palette, and camera framing. Compare with a reference only if one exists.

A validator cannot certify attractiveness, resemblance, animation quality, UV quality, or performance. Mark unperformed checks `not_tested`, never `passed`.

## 7. Iterate on diagnosed defects

Make one targeted geometric or material change at a time, then rerun only affected structural and visual checks. Classify the defect before editing:

- **Structure:** invalid indices, degenerate geometry, winding, duplicate faces, unintended open edges.
- **Placement:** floating clothing, misaligned eyes, disconnected-looking neck or wrists.
- **Proportion/silhouette:** head size, shoulder width, hair mass, hand/foot scale.
- **Topology intent:** insufficient loops or poor edge placement for the intended deformation.
- **Shading/composition:** excessive specular highlights, unreadable dark shapes, poor camera crop.

Do not fix a shape problem by adding random detail or changing only the material. Do not hide unresolved defects behind a flattering camera.

## 8. Low-spec production settings

Start with modest meshes, solid materials, flat shading, and 512-pixel previews. Avoid dense subdivision, cloth/hair simulation, large textures, high-sample renders, and multiple concurrent Blender instances. Increase detail only after a visual review identifies a need. Measure actual performance on the target computer; do not invent universal frame times, memory use, or “safe for every integrated GPU” claims.

## 9. Delivery contract

Deliver complete runnable files or exact repository-fitting patches, not pseudocode labelled as finished. Include:

- source and configuration;
- run instructions and dependency/version assumptions;
- semantic part manifest and actual counts;
- Python test results, Blender runtime results, and export round-trip results separately;
- inspection images and visual-review status;
- known limitations and unperformed tests;
- licence/attribution for every reused third-party asset or code path.

Never call the result “production-ready,” “game-ready,” “rigged,” “animation-ready,” “perfect topology,” or “reference-matched” without the corresponding evidence. The included generator produces a static editable multi-part character without a production rig, skin weights, UV workflow, or animation certification.
