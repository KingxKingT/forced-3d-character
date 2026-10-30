# Roadmap Ordered by Visual Improvement and Implementation Difficulty

The order is deliberate. Better eye shaders or a neural backend cannot compensate for weak proportions, hair, hands, and clothing fit. “Completed” refers only to this repository's implemented static-character path, not to production animation readiness.

| Priority | Work | Visual payoff | Difficulty | Status / acceptance evidence |
|---:|---|---|---|---|
| 1 | Replace box torso/limbs with profile lofts | Very high | Low–medium | Completed; shaped jacket, trousers, sleeves, neck. |
| 2 | Replace ellipsoid head with jaw/cheek/forehead sections | Very high | Medium | Completed at stylized blockout-plus level; inspect close-up. |
| 3 | Build scalp cap and designed swept locks | Very high | Medium | Initial five-parameter `manhwa_layered` card builder implemented; actual Blender visual review still required. |
| 4 | Fit shirt/lapels/tie to the body envelope | High | Medium | Completed after side-render defect review. |
| 5 | Shape palms and add jointed varied fingers/opposed thumbs | High | Medium | Completed static hands; no grip/deformation claim. |
| 6 | Replace shoe cubes with lasts and separate soles | Medium–high | Low–medium | Completed; inspect front and side silhouette. |
| 7 | Add semantic and structural defect tests | Indirect but high | Medium | Completed; Python fixtures and Blender strict validation. |
| 8 | Save source and validate export round trip | Workflow high | Low–medium | Completed for GLB; other formats need per-version testing. |
| 9 | Add parameterized character families on shared topology | High reuse | Medium–high | Next scalable procedural step; keep part indices stable and test extremes. |
| 10 | Improve facial plane transitions and optional selective smooth groups | High for close-ups | Medium | Only after silhouette review; avoid hiding poor profiles with shading. |
| 11 | Add more outfits via body-derived shells/panels | High reuse | Medium–high | Share fitting functions; validate side/back for every outfit. |
| 12 | Add optional CC0 base-character adapter | Potentially very high | Medium | Separate asset-backed path; record provenance and never make it mandatory. |
| 13 | Design continuous deformation topology and skin weights | Essential for animation | High | Separate milestone; joint-loop and range-of-motion tests required. |
| 14 | Add UVs, baking, textures, LODs, and engine profiling | Platform dependent | High | Only after target platform and visual requirements are known. |
| 15 | Evaluate local neural/high-spec tools | Uncertain | High resource cost | Optional experiment only; never a baseline dependency. |

## Next practical iteration

The highest-value next change is not “more polygons everywhere.” Define a small set of body/head proportion presets that share component topology, then render extremes to find intersections and broken clothing fit. After that, improve hair lock grouping and face planes using the close-up checklist. If animation is required, stop extending the static component model and plan the deformation topology explicitly.

## Suggested review cadence

For each row, preserve the previous version, change one visual system, run relevant pure/Blender checks, render the same cameras, and record unresolved issues. Do not mark a row complete from code inspection alone. A feature that passes structure but fails the side-view silhouette remains visually incomplete.


## CHARM-inspired hair-card follow-up

A lightweight independent five-parameter hair-card builder now exists in `scripts/hair_cards.py`, and the Blender generator uses it for all three current hair presets. It is not the CHARM autoregressive model and does not perform image-to-hair inference. The next step is to render the integrated Blender output, compare the same reference angles, and art-direct the guide positions/widths before considering an optional high-spec CHARM model adapter. See [docs/charm-hair-integration.md](charm-hair-integration.md).
