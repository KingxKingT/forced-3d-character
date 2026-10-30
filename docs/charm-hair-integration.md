# CHARM-inspired hair-card integration

## What CHARM contributes

[CHARM](https://github.com/hyz317/CHARM) (SIGGRAPH Asia 2025) represents anime hair as separate cards. A card is a sequence of control points; each point has five geometric values:

- X, Y, Z: centerline position
- width: card width
- thickness: card thickness

The project page describes full hairstyles as roughly 25–130 individual hair pieces. See the [paper](https://arxiv.org/abs/2509.21114) and [project page](https://hyzcluster.github.io/charm/) for the method and examples.

## What this repository implements

`scripts/hair_cards.py` contains an independent, lightweight implementation of the five-value control-point idea. It interpolates the centerline, transports a stable local frame, and creates a tapered closed low-poly lock. The Blender generator calls this module for its `manhwa_layered`, `side_swept`, and `short` presets.

This is a **procedural adaptation inspired by CHARM's representation**, not the CHARM autoregressive neural model. The hairstyle guides in the current sample are hand-authored. The code does not infer locks from an image or point cloud, and the current preset uses fewer pieces than the complete 25–130-card hairstyles described by the research.

No CHARM Python source, checkpoint, training data, or dataset is included in this MIT repository. The implementation in `scripts/hair_cards.py` was written independently.

## Why the full model is not a default dependency

The upstream README specifies Python 3.9 and a PyTorch 2.1.0 / torchvision 0.16.0 CUDA 11.8 setup, plus its other Python requirements. It asks users to download both CHARM model weights and a separate Michelangelo point-cloud-encoder checkpoint, as well as test data. That is not an appropriate default dependency for the project's i3 / 8 GB / integrated-graphics target.

A future optional high-spec adapter may call the upstream model in a separate environment and pass generated 5D control-point guides to this repository. Keep that path isolated and optional.

## Licence boundary

The [CHARM GitHub repository](https://github.com/hyz317/CHARM) is GPL-3.0, and the [published model card](https://huggingface.co/hyz317/CHARM) also identifies GPL-3.0. This project remains MIT. Do not copy CHARM source or redistribute its checkpoints/data inside this repository without a deliberate compatible licensing decision. This document records the method and points to the source; it does not relicense CHARM.

## Current test status

- Eight Python tests cover closed geometry, winding, degenerate faces, endpoints, named-card generation, and invalid inputs.
- A CPU-only test exported the existing character plus 17 cards produced with the upstream CHARM template-to-mesh converter, re-imported the GLB, and rendered front/side/back/three-quarter previews.
- That experiment used hand-authored control-point data. It did **not** run the CHARM neural inference model or prove image-to-hairstyle reconstruction.
- Blender is not installed in the validation environment, so the repository's actual Blender generation/render integration test remains unrun here. Run the documented Blender command locally before accepting the preset visually.

The experimental GLB and previews are test artifacts, not bundled upstream assets or proof of final visual matching.
