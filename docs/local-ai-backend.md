# Free local AI backend: Effigy

This project is deliberately **not** tied to a paid 3D website or a credit-metered API. For higher-quality reference-to-mesh work, it delegates to [Effigy](https://github.com/SifuInTheShell/Effigy), a separate MIT-licensed, local image-to-3D and character pipeline.

Effigy is not copied into this repository. The AI agent connects to its local MCP server; code and model weights remain in the upstream installation with their own licences and notices.

## What you get

Effigy's stages include reference preparation, image-to-3D generation, mesh cleaning, triangle or quad remeshing, UV unwrap, PBR bake, face projection, humanoid rig fitting/skinning, validation, and game-engine export. It accepts pictures and multi-view turnaround sheets. Its MCP server lets a local coding agent call the same steps as the app.

For this project's three-view character reference, the strongest fit is Effigy's **Faithful / Pixal3D multi-view** route. It consumes the views together rather than asking a single-view model to guess the unseen side and back.

Official sources:

- [Effigy repository and MIT licence](https://github.com/SifuInTheShell/Effigy)
- [Effigy setup guide](https://github.com/SifuInTheShell/Effigy/blob/main/SETUP.md)
- [Effigy model/dependency licence manifest](https://github.com/SifuInTheShell/Effigy/blob/main/licenses.yaml)
- [Effigy MCP server](https://github.com/SifuInTheShell/Effigy/blob/main/mcp/effigy_server.py)
- [Effigy agent guide](https://github.com/SifuInTheShell/Effigy/blob/main/mcp/SKILL.md)

## Cost and hardware

**Software and generation:** Effigy's local application does not require a subscription, generation credits, paid cloud service, or API key. Model inference runs on the user's own computer. The model files are large, so the local machine pays the cost in storage, RAM, GPU time, electricity, and hardware.

The current upstream Windows setup guide documents:

| Requirement | Upstream guidance |
|---|---|
| Operating system | Windows 11 first; Windows 10 is not documented as a supported target |
| GPU | NVIDIA RTX with 16 GB VRAM for the full character path; 12 GB is best-effort for the Fast path |
| Driver | NVIDIA driver 575+ |
| System RAM | 32 GB recommended |
| Disk | About 70–160 GB depending on which model packs are selected |
| Character model pack | About 78 GB in the guided setup |
| Optional multi-view Pixal3D pack | About 22 GB additional |

AMD RX 9070/9070 XT support is documented for Effigy's Fast path only; do not assume it supports Faithful multi-view. Effigy does not currently document a macOS generation path. Check the upstream setup guide before installing. These requirements are upstream's current figures and may change.

The 3D model pack is a separate download. The optional Pixal3D multi-view pack is large; ask the user before downloading it. The project must not silently start a multi-gigabyte download.

## Install and connect

1. Read Effigy's [SETUP.md](https://github.com/SifuInTheShell/Effigy/blob/main/SETUP.md) and check the machine against the requirements above.
2. Download the latest Windows release ZIP from [Effigy Releases](https://github.com/SifuInTheShell/Effigy/releases), or clone the repository and use its documented `run.bat` setup.
3. Start Effigy locally and use its guided setup to install only the model packs needed. The multi-view pack is optional and is about 22 GB extra.
4. To connect a coding agent, open Effigy's **Setup → Connect an agent** and copy the generated configuration for that specific client. This avoids stale paths or an invented MCP command. Codex is listed as a supported client.
5. Start a new local agent session and check that the Effigy MCP tools are present: `import_file`, `run_step`, `job_status`, `look`, `describe_steps`, `fit_check`, `validate`, and `export`.

Use the free open-source Blender MCP add-on only if a live Blender viewport connection is needed. It is optional; Effigy's own MCP server drives the main model pipeline. Do not purchase Blender MCP Pro for this project.

A normal ChatGPT browser conversation cannot reach a service running on your PC's localhost. The MCP integration is for a local coding agent that runs on the same PC, such as a configured Codex or Cursor session.

## Exact three-view workflow

Effigy's `prep` step has a `views` operation. It can divide a single turnaround sheet into equal-width columns and create the camera transforms for Pixal3D-MV.

For a horizontal sheet ordered **front | character-right profile | back**:

1. In the local agent, call `import_file(path=<absolute path to the reference sheet>)`. This creates an uploaded/prepared asset version.
2. Inspect `get_asset(asset_id)` to get the prepared version ID.
3. Call `run_step(asset_id, parent=<prepared version>, step="prep", params={"op":"views","views":["front","right","back"]})`.
4. Inspect the returned view version. It must report three views and a small height spread. If the sheet has unequal panel widths or gutters, crop the panels separately and use the `sources` option with one uploaded version per view; do not feed a bad crop to multi-view reconstruction.
5. Run generation from that views version:

   ```json
   {
     "weights": "faithful",
     "multiview": true,
     "pipeline_type": "1024_cascade",
     "steps": 12,
     "texture_size": 2048
   }
   ```

   This selects the multi-view Pixal3D pipeline only when the additional multi-view weights are installed. If they are missing, install them only after confirming the disk requirement; otherwise run a single-view fallback and state that the hidden sides are inferred.
6. Use `look(asset_id, version)` to inspect all sides before mesh cleanup. If fingers, face, hair, or clothing silhouette are wrong, rerun generation or fix the source views before texturing.
7. Continue with `clean` → `remesh` → `uv` → `bake`. Try a quad remesh (for example 15k–25k faces) for editing/deformation; use triangles for simpler game use. Check the output metrics before selecting a result.
8. Optionally project a sharper face from the front image. Inspect it; projection can be wrong if the mesh or camera alignment is wrong.
9. For animation, fit a `mixamo52` skeleton, run `fit_check`, then skin the mesh. Read the skinning QA and inspect deformation. A skeleton existing in a file does not prove the weights are good.
10. Run `validate`, address failures, then export for Godot, Unreal, Unity, or web. Keep `CREDITS.txt` and `LICENSES.json` with the asset.

Effigy queues one heavy GPU job at a time. When a step returns a running job, poll `job_status(job_id)`; do not launch another heavy job concurrently. Use `describe_steps(step)` and Effigy's own guide to confirm parameter names against the installed version.

### T-pose note

The reference sheet currently used by this project is a T-pose turnaround. T-pose views are useful for shape matching, but a rig-fitting model may prefer an A-pose. Do **not** run a one-image re-pose after preparing the multi-view cameras, because moving only the front image invalidates the side/back alignment. Either create a complete, matching A-pose turnaround first, or keep the T-pose geometry and correct/inspect the skeleton markers during rig fitting.

## Licensing and costs

- Effigy's application repository declares **MIT**. Its Blender operations are identified separately as **GPL-3.0-or-later** and run as their own Blender-side process. This project does not copy either codebase.
- Effigy's default model dependencies keep their own licences. Its manifest lists TRELLIS.2 and Pixal3D code/weights as MIT, DINOv3 under Meta's separate royalty-free DINOv3 licence, and other optional models under their individual terms.
- DINOv3 access may require a free Hugging Face account, licence acceptance, and the attribution line **“Built with DINOv3”**. It is not a paid API, but its licence is not the same as an OSI open-source licence.
- Do not enable experimental or region-restricted backends without reviewing their terms. This integration recommends the documented local TRELLIS.2/Pixal3D routes and preserves Effigy's generated `CREDITS.txt` and `LICENSES.json`.
- No model weights are bundled or silently downloaded by this repository. Model access, downloads, and licence acceptance remain under the user's control.

This guide is not legal advice. The model's own licence file and the current upstream manifest take precedence over this summary.
