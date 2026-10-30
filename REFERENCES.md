# Implementation references

## Local AI generation and character pipeline

- [Effigy](https://github.com/SifuInTheShell/Effigy) — separate MIT-licensed local image-to-3D app with an MCP server for local coding agents.
- [Effigy setup guide](https://github.com/SifuInTheShell/Effigy/blob/main/SETUP.md) — hardware, model packs, and local MCP setup.
- [Effigy model and dependency licence manifest](https://github.com/SifuInTheShell/Effigy/blob/main/licenses.yaml) — separate terms for code, checkpoints, and clip packs.
- [Effigy multi-view preparation](https://github.com/SifuInTheShell/Effigy/blob/main/steps/prep.py) and [multi-view generation](https://github.com/SifuInTheShell/Effigy/blob/main/steps/trellis2.py) — turnaround camera generation and Pixal3D-MV selection.
- [Effigy MCP server](https://github.com/SifuInTheShell/Effigy/blob/main/mcp/effigy_server.py) — tools for import, steps, visual inspection, rig checks, validation, and export.
- [Meta DINOv3 licence](https://ai.meta.com/resources/models-and-libraries/dinov3-downloads/) — royalty-free model terms and required attribution where used.

## Blender and interchange formats

The fallback generator targets Blender's Python API. Consult the documentation for the exact Blender version installed locally, since operator parameters can change between versions.

- [Blender Python API 4.5 — `bpy.ops.wm.obj_export`](https://docs.blender.org/api/4.5/bpy.ops.wm.html)
- [Blender Python API — glTF 2.0 exporter](https://docs.blender.org/api/3.0/bpy.ops.export_scene.html)
- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)

The references above describe relevant interfaces and format behavior; they do not imply the full project was executed against every Blender version or that the optional Effigy backend has been run in this environment.
