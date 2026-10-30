# Multi-View Visual-Quality Review

Structural validation can pass a badly proportioned character. This checklist is a separate qualitative gate. Use the same camera set across iterations so changes are comparable.

## Required views

- Front: overall symmetry, stance, shoulder line, hand direction, jacket opening, trouser and shoe silhouette.
- Side: head/profile, nose and hair projection, neck transition, clothing fit, chest/waist depth, shoe length.
- Back: scalp coverage, jacket/back silhouette, arm transitions, leg separation, heel/sole shape.
- Three-quarter: depth relationships and intersections that orthographic front/side views can hide.
- Head close-up: jaw/cheek planes, eye alignment, brows, nose, mouth, hairline, lock grouping, ears.
- Hand close-up when hands are important: palm shape, four fingers plus thumb, varied lengths, joint bends, left/right orientation.

## Review questions

| Area | Pass evidence | Common failure |
|---|---|---|
| Silhouette | Character and outfit read at thumbnail size | Primitive stack, noisy micro-detail, weak shoulder/waist relationship |
| Proportion | Head, neck, torso, limbs, hands, and feet follow the blueprint | Long neck, tiny hands, oversized head, detached-looking joints |
| Face | Features sit on the head surface and profile remains deliberate | Floating eyes, flat feature placement, pointed accidental jaw |
| Hair | Scalp mass and locks have a clear direction from every view | Vertical stripes, random spikes, gaps, dark unreadable mass |
| Clothing | Shell and panels follow body depth and remain layered | Floating lapels/tie, giant shirt opening, intersections |
| Hands | Palm/finger proportions and thumb opposition read naturally | Mitten, fan of identical sticks, wrong thumb side |
| Shoes | Foot direction, toe taper, sole, and ground contact read | Box toes, inverted sole, floating foot |
| Materials/light | Dark parts retain separation; palette supports forms | Excess specular turns black hair/shoes grey or purple |
| Reference | Observable landmarks match supplied evidence | Claimed resemblance without an image or with mismatched views |

## Iteration record

For every defect, record view, component, diagnosis, exact change, and re-review result. Example: “Side view showed shirt and lapels floating ahead of the tapered torso; fitted panel Y coordinates to the torso envelope and shortened the shirt opening; front and side renders improved.” This is stronger evidence than “improved clothing.”

## Status vocabulary

- `not_tested`: no actual visual inspection occurred.
- `failed`: inspected, with a blocking visual defect.
- `passed_with_limitations`: inspected and usable for the stated static low-poly purpose, with documented unresolved art-direction limitations.
- `reference_not_tested`: no reference image was available or comparison was not performed.

There is no automatic numerical visual-quality score in this repository. A passing visual review does not establish deformation, UV, rigging, or engine performance quality.
