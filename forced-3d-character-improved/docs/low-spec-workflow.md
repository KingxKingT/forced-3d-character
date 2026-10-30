# Low-spec workflow (the default)

This project must remain useful without a gaming GPU or a local image-to-3D model.

## Target machine profile

The baseline target is an 11th-generation Intel Core i3, 8 GB system RAM, and Intel integrated graphics. Treat this as a constrained Blender scripting machine. It is not a suitable target for large local diffusion, TRELLIS, Pixal3D, or other neural 3D model inference.

## What still works

The generation step is procedural code: a capable AI writes a Blender Python script, then Blender constructs actual mesh data using coordinates, faces, BMesh operations, materials, and modifiers. This does not require a local neural model or a 3D API subscription.

The AI model itself may be used through a chat product or through an agent on another machine/service; whether that AI service costs money depends on the user's chosen provider and plan. This repository does not call a paid model API. To automate Blender execution, use a local agent/MCP bridge; an ordinary browser chat cannot directly execute scripts inside Blender on the user's PC.

## Recommended settings

- Start with a blockout and a limited number of objects.
- Use explicit low-poly mesh data; avoid dense subdivision and unnecessary modifiers.
- Use flat-shaded solid colours; defer image textures and complex shader graphs.
- Keep preview renders small (512 px is a sensible starting point) and render only when needed.
- Work on one character/asset at a time; close other memory-heavy applications.
- Save incrementally and keep a clean base version before trying risky modifications.
- Measure the actual triangle count and simplify only where it does not damage the silhouette.
- Keep the mesh editable; use a separate export copy when triangulation or modifier application is required.

There is no universal safe triangle count for every PC or game engine. The skill should report counts and allow the user to choose a target budget. For this machine, prefer a modest stylized character with clearly defined silhouette and clothing layers instead of a dense cinematic sculpt.

## What to avoid on this tier

Do not install or run the Effigy full character model pack, TRELLIS.2, Pixal3D multi-view, Hunyuan3D, large local language models, 4K texture baking, or other GPU-heavy models. Do not start large model downloads automatically. A tiny mesh can still become slow if the scene contains large textures, heavy modifiers, or expensive rendering.

## Optional strong-hardware tier

For a stronger PC, see [local-ai-backend.md](local-ai-backend.md). The Effigy route is an optional local neural image-to-3D pipeline, not a dependency of this low-spec workflow. Check its current hardware, model-download sizes, and per-model licences before installing.
