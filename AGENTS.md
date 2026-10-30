# Persistent project instructions

## Project goal
Build a reusable, reference-driven Blender modelling skill/toolkit that helps different AI coding agents create visually strong, editable low-poly stylized characters and props from reference images, then export them for Godot. This is not a fixed male-character generator. The dark-suit, black layered hair, violet-eyed manhwa character is a quality benchmark, not the only supported output.

## Non-negotiable priorities
1. Match the reference silhouette and large forms before adding details.
2. For this benchmark, prioritize custom layered hair and a designed face; the previous primitive-heavy result is not the target quality.
3. Inspect front, side, back, three-quarter, and head close-up renders. Passing unit tests does not prove visual quality.
4. Keep the default workflow light enough for an Intel i3, 8 GB RAM, and integrated graphics. Do not require large AI models, paid APIs, cloud 3D services, or GPU-only dependencies.
5. Keep the repository's current CLI/configuration stable unless a change is justified. Never claim Blender renders or visual inspection were performed unless they were.
6. Keep each iteration evidence-based: preserve baseline, change one major visual system, run tests, generate actual previews, compare against the reference, and record remaining defects.
7. Prefer original geometry and documented techniques. Respect third-party licences; do not copy GPL code into this MIT repository without a deliberate licence decision.

## Reference benchmark
- Black layered/asymmetric manhwa hair with individually designed, broad tapered locks; no helmet silhouette or row of near-identical spikes.
- Angular handsome face, narrowed jaw, fitted almond-shaped violet eyes, purposeful brows and subtle nose/mouth.
- Tailored dark suit with clear lapels, white collar, tie, pocket square, fitted sleeves and readable trouser/shoe silhouettes.
- Low-poly means deliberate planes and efficient geometry, not primitive-looking geometry. Do not optimize to an 800-triangle target until visual form is convincing.

## Graphify memory
Graphify is an optional local codebase knowledge graph, not a substitute for these instructions or tests. If installed, use `graphify query` for repository architecture questions and update the graph after meaningful source changes. Do not commit generated graph output unless requested. Setup instructions: `docs/GRAPHIFY_SETUP.md`.
