# Optional high-spec local AI backend: Effigy

Effigy is a separate open-source local image-to-3D application. This is an **optional high-spec tier**, not the default and not needed by the low-spec procedural workflow.

Repository: https://github.com/SifuInTheShell/Effigy

## Do not install on the baseline low-spec machine

The baseline target for this repository is an 11th-gen Intel Core i3, 8 GB RAM, and Intel integrated graphics. That machine is not suitable for the full Effigy neural character-generation path.

The current Effigy Windows setup guide documents:
- Windows 11 as the primary target.
- NVIDIA RTX GPU with 16 GB VRAM for the full character path; 12 GB is best-effort for the Fast route.
- 32 GB RAM recommended.
- About 70–160 GB disk depending on selected models.
- The optional Pixal3D multi-view model pack adds about 22 GB.

Do not ask the user to download model packs until their hardware and free disk have been checked.

## When it is appropriate

Use Effigy only when the user explicitly says they have stronger hardware. Its local pipeline includes image-to-3D, cleanup, remeshing, UV unwrap, texture baking, rigging, validation, and export. It exposes tools to local coding agents through MCP.

For a turnaround with front, right, and back views, Effigy documents a multi-view Pixal3D route. It can use the views together rather than relying on a single image. See its current [setup guide](https://github.com/SifuInTheShell/Effigy/blob/main/SETUP.md), [agent MCP guide](https://github.com/SifuInTheShell/Effigy/blob/main/mcp/SKILL.md), and [model licence manifest](https://github.com/SifuInTheShell/Effigy/blob/main/licenses.yaml).

## Free versus open licensing

The Effigy application repository declares MIT. Model checkpoints and some dependencies have separate terms. A free Hugging Face account and licence acceptance may be required for certain checkpoints. Free to download does not mean every component is under an OSI-approved open-source licence. Keep all required credits and licence files with generated assets.

## Integration boundary

This repository does not copy Effigy's code or weights. It links to the upstream application and documents how a local coding agent can connect to its MCP server. An ordinary browser chat cannot directly access a service running on the user's localhost; the local agent must be configured to use the MCP server.

For the baseline i3/8 GB machine, stay with [the low-spec workflow](low-spec-workflow.md): AI-assisted procedural modeling through Blender.
