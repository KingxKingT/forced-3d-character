# Graphify setup for OpenCode (Windows)

Graphify is a local codebase knowledge-graph tool. It can help an agent recover relationships between scripts, configuration, tests, and design decisions across sessions. It does not replace this repository's `AGENTS.md`, `SKILL.md`, or visual reviews.

## Install locally
Run these commands in PowerShell from the repository root. This installs Graphify on your own machine; a remote GitHub edit cannot install software on your PC.

```powershell
uv tool install graphifyy
graphify install --project --platform opencode
```

If `uv` is not installed, follow the Windows instructions in the official Graphify repository: https://github.com/Graphify-Labs/graphify

Then open/reload this repository in OpenCode and run the Graphify skill command it exposes (normally `/graphify .`) to build the local graph. Do not invent or hand-write `graph.json` or `GRAPH_REPORT.md`; let Graphify generate them from the checked-out source.

## Use and refresh
- Query relationships rather than rereading the entire project: `graphify query "how does hair_style flow from JSON config to generated meshes?"`
- After source changes, use the Graphify update command shown by the installed version/skill to refresh the graph.
- Keep the graph local by default. Do not commit generated graph files unless the project owner specifically wants them versioned.
- Graphify is a convenience. The canonical persistent project intent and constraints are in `AGENTS.md`; implementation workflow is in `SKILL.md`; visual acceptance criteria are in `docs/visual-review.md`.

Official project and current platform options: https://github.com/Graphify-Labs/graphify
