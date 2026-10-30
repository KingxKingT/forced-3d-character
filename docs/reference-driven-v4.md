# Reference-driven V4 plan

## Evidence-based diagnosis
The prior generator's hair used a scalp cap plus seven similarly shaped front sweeps. The style setting changed the sweep amount or number of locks, but did not express a designed strand layout. The sample configuration also had no `manhwa_layered` option. The output was therefore structurally valid but visually generic.

## Implemented in this branch
- Added a distinct `manhwa_layered` hair style made of separately authored tapered locks for long/short bangs, side framing, crown, and rear silhouette.
- Kept `side_swept` and `short` as separate supported layouts.
- Updated config validation and the dark-suit benchmark config to select `manhwa_layered`.
- Bumped generator version to 2.1.0.

## What is not yet solved
This is a targeted improvement, not a claim of reference matching. Locks are currently hand-authored in generator coordinates, and face/clothing geometry still need close-up iteration. The hairstyle is not yet image-conditioned; no Blender render has been produced by this GitHub edit alone.

## Next visual milestones
1. Run Blender locally and render the six canonical views. Compare the head close-up to the supplied sheet.
2. Adjust scalp/head overlap and every lock in front, side, and back views; avoid making all tips point down or using a single dark material if silhouette becomes unreadable.
3. Improve face plane transitions and eye socket/eyelid fit. Check the side profile, not only the front.
4. Fit the suit panels and sleeves to the torso from all angles.
5. Only after a visual pass, optimize triangle count and export/re-import into Godot.

## Future architecture
Consider a lightweight control-point hair API where each lock has a 3D path, width, thickness, tip profile, root attachment, and optional material variation. This is inspired by published anime-hair research, but the repository should keep a lightweight procedural baseline and must not require a neural model or large checkpoint.
