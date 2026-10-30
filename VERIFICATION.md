# Verification of the Delivered Improved Version

Verified on 2026-10-30 with Blender 4.2.3 LTS. These results belong to the delivered example and current source; they are not promises for other configurations, Blender versions, or hardware.

## Automated tests

- **30 Python-only tests passed**, covering configuration and pure geometry/structural defect fixtures.
- **1 real Blender integration test passed**, covering generation, `.blend` saving, GLB export, strict source validation, semantic metadata, and GLB re-import. The final combined run used `SKIP_BLENDER_RENDER=1` because final example renders were generated and inspected separately.
- The integration command uses `--python-exit-code 1`; expected artifacts are asserted rather than relying only on Blender's process status.

## Example source scene

Strict source validation passed with watertight, single-component-per-object, semantic-part, winding, and 6,000-evaluated-triangle requirements.

| Metric | Result |
|---|---:|
| Mesh objects | 65 |
| Base vertices | 2,002 |
| Base polygons | 1,791 |
| Base triangles | 3,744 |
| Evaluated triangles | 3,976 |
| Boundary/wire/over-shared edges | 0 / 0 / 0 |
| Degenerate faces / zero-length edges / duplicate faces | 0 / 0 / 0 |
| Inconsistent winding edges / loose vertices / coincident vertices | 0 / 0 / 0 |
| Non-planar quads/n-gons | 1,104 warnings; export triangulation inspected |
| Materials | 12 |

Non-planar quads are expected on curved low-poly sweeps and body-fitted panels; they are not suppressed. The GLB round trip and rendered views are part of their review.

## Exported GLB

Blender re-import and the official Khronos glTF Validator passed.

| Metric | Result |
|---|---:|
| Raw re-imported vertices | 7,815 |
| Analysis-only welded vertices | 2,118 |
| Triangles | 3,976 |
| Mesh objects / materials | 65 / 12 |
| Welded boundary edges | 0 |
| Round-trip warnings / fatal errors | 0 / 0 |
| Khronos errors / warnings / infos / hints | 0 / 0 / 0 / 0 |

Flat shading and attribute seams explain the raw vertex increase. Welding is used only for topology analysis and does not alter the delivered GLB. Source and export triangle counts agree after modifier evaluation.

## Actual visual inspection

Front, side, back, three-quarter, head, and right-hand renders were generated and visually inspected. Status: **passed_with_limitations for an editable static stylized low-poly character**. The initial floating-clothing and vertical-fringe defects were corrected and re-rendered. See the example's `visual-review.json` for evidence and remaining limitations.

## Not established by these tests

- No reference image was supplied, so reference similarity was not tested.
- No production rig, skin weights, UV workflow, facial animation, grip, or range-of-motion quality is claimed.
- FBX and OBJ were not validated in the final example run; GLB was the tested export.
- No render-time, memory, or engine-performance measurement was made on the user's 11th-generation i3/8 GB integrated-graphics machine.
- No claim is made for every Blender version or every possible configuration extreme.
