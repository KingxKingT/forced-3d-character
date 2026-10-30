"""Generate an editable stylized low-poly human locally in Blender.

Run:
  blender --background --factory-startup --python scripts/blender/create_character.py -- \
    --config examples/dark_suit_purple_eyes.json --outdir build/character \
    --formats glb fbx obj --render-views

The generator intentionally produces a static, multi-part character. It does
not claim animation-ready topology, UVs, a rig, or automatic visual approval.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry_core import (  # noqa: E402
    almond_lens,
    extrude_xz_polygon,
    horizontal_loft,
    loft_rings,
    mirrored_outline,
    sweep_mesh,
)
from mesh_tools import (  # noqa: E402
    add_bevel,
    create_ico_object,
    create_mesh_object,
    make_material,
)

GENERATOR_VERSION = "2.1.0"


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--formats", nargs="+", choices=("glb", "gltf", "fbx", "obj"))
    parser.add_argument("--render-views", action="store_true", help="Render inspection PNG previews")
    parser.add_argument("--no-render", action="store_true", help="Do not render preview images")
    parser.add_argument("--save-blend", action="store_true", help="Also save the editable source scene")
    return parser.parse_args(argv)


def add_mesh(name, arrays, material, part, bevel=0.0):
    obj = create_mesh_object(name, *arrays, material=material, part=part)
    if bevel > 0.0:
        add_bevel(obj, bevel, 1)
    return obj


def tailored_front_y(z):
    """Front envelope of the torso loft, extended slightly for the collar."""
    profile = [
        (0.865, 0.091), (0.940, 0.087), (1.080, 0.099),
        (1.240, 0.111), (1.350, 0.104), (1.405, 0.083), (1.445, 0.058),
    ]
    if z <= profile[0][0]:
        return profile[0][1]
    if z >= profile[-1][0]:
        return profile[-1][1]
    for (z0, y0), (z1, y1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            factor = (z - z0) / (z1 - z0)
            return y0 + (y1 - y0) * factor
    return profile[-1][1]


def add_panel(name, outline, front_y, back_y, material, part="clothing", bevel=0.0):
    vertices, faces = extrude_xz_polygon(outline, front_y, back_y)
    if part == "clothing":
        # Preserve each panel's designed offset/thickness while following the
        # tapered torso. This avoids flat clothing floating in side views.
        vertices = [
            (x, tailored_front_y(z) + y - 0.111, z)
            for x, y, z in vertices
        ]
    return add_mesh(name, (vertices, faces), material, part, bevel)


def add_sweep(name, points, widths, thicknesses, material, part, **kwargs):
    return add_mesh(
        name,
        sweep_mesh(points, widths, thicknesses, **kwargs),
        material,
        part,
    )


def lighten(hex_color, amount=0.08):
    text = hex_color.lstrip("#")
    channels = [int(text[index:index + 2], 16) for index in (0, 2, 4)]
    mixed = [round(channel + (255 - channel) * amount) for channel in channels]
    return "#" + "".join(f"{channel:02X}" for channel in mixed)


def make_hair_cap(material):
    """A scalp-following cap with a high front hairline and lower back edge."""
    segments = 16
    bottom = []
    for index in range(segments):
        angle = 2.0 * math.pi * index / segments
        sine = math.sin(angle)
        bottom.append(
            (
                0.121 * math.cos(angle),
                0.103 * sine,
                1.625 + 0.075 * sine,
            )
        )
    rings = [bottom]
    for z, radius_x, radius_y in (
        (1.735, 0.123, 0.105),
        (1.795, 0.091, 0.078),
        (1.825, 0.026, 0.023),
    ):
        rings.append(
            [
                (
                    radius_x * math.cos(2.0 * math.pi * index / segments),
                    radius_y * math.sin(2.0 * math.pi * index / segments),
                    z,
                )
                for index in range(segments)
            ]
        )
    vertices, faces = loft_rings(rings, cap_start=False, cap_end=True)
    center_index = len(vertices)
    vertices.append((0.0, 0.0, 1.625))
    for index in range(segments):
        faces.append((center_index, (index + 1) % segments, index))
    return add_mesh("Hair_Scalp_Cap", (vertices, faces), material, "hair")


def build_hair(material, style):
    """Build deliberate, asymmetric solid hair clumps rather than repeated spikes.

    Coordinates use +Y as the character's front. Each clump is a separate,
    tapered low-poly sweep so its silhouette can be art-directed independently.
    The manhwa_layered style is intentionally distinct from side_swept and short.
    """
    make_hair_cap(material)

    if style == "short":
        locks = [
            # Small, restrained fringe.
            ("Fringe_Center_L", [(-0.040, 0.040, 1.806), (-0.055, 0.086, 1.770), (-0.065, 0.108, 1.735)], [0.019, 0.020, 0.002], [0.009, 0.009, 0.0015]),
            ("Fringe_Center_R", [(0.010, 0.040, 1.811), (0.020, 0.087, 1.775), (0.034, 0.108, 1.748)], [0.020, 0.019, 0.002], [0.009, 0.008, 0.0015]),
            ("Fringe_Outer_R", [(0.061, 0.020, 1.795), (0.081, 0.073, 1.756), (0.091, 0.090, 1.724)], [0.018, 0.017, 0.002], [0.008, 0.007, 0.0015]),
        ]
    elif style == "side_swept":
        locks = [
            ("Fringe_Sweep_L", [(-0.102, 0.018, 1.802), (-0.067, 0.075, 1.777), (-0.015, 0.108, 1.742)], [0.027, 0.030, 0.002], [0.011, 0.012, 0.0015]),
            ("Fringe_Sweep_Center", [(-0.057, 0.024, 1.811), (-0.016, 0.083, 1.773), (0.033, 0.111, 1.731)], [0.025, 0.027, 0.002], [0.010, 0.010, 0.0015]),
            ("Fringe_Sweep_R", [(0.002, 0.020, 1.813), (0.045, 0.078, 1.778), (0.075, 0.103, 1.750)], [0.023, 0.024, 0.002], [0.010, 0.010, 0.0015]),
            ("Fringe_Tip_R", [(0.067, 0.012, 1.796), (0.091, 0.065, 1.761), (0.102, 0.090, 1.733)], [0.018, 0.018, 0.002], [0.008, 0.008, 0.0015]),
        ]
    else:  # manhwa_layered (the default reference-driven style)
        locks = [
            # Long, separated bangs: deliberately varied direction and length.
            ("Bang_Center_Long", [(-0.032, 0.026, 1.817), (-0.017, 0.080, 1.775), (-0.006, 0.111, 1.716)], [0.026, 0.030, 0.0018], [0.011, 0.012, 0.0014]),
            ("Bang_Left_Long", [(-0.084, 0.018, 1.802), (-0.078, 0.076, 1.761), (-0.099, 0.105, 1.700)], [0.027, 0.029, 0.0018], [0.011, 0.011, 0.0014]),
            ("Bang_Left_Split", [(-0.054, 0.030, 1.819), (-0.046, 0.088, 1.784), (-0.057, 0.116, 1.744)], [0.021, 0.023, 0.0018], [0.009, 0.010, 0.0014]),
            ("Bang_Mid_Right", [(0.010, 0.030, 1.817), (0.030, 0.087, 1.776), (0.047, 0.112, 1.725)], [0.025, 0.027, 0.0018], [0.010, 0.011, 0.0014]),
            ("Bang_Right_Long", [(0.061, 0.018, 1.803), (0.083, 0.071, 1.763), (0.102, 0.100, 1.709)], [0.026, 0.028, 0.0018], [0.010, 0.011, 0.0014]),
            ("Bang_Right_Split", [(0.040, 0.025, 1.818), (0.054, 0.083, 1.789), (0.067, 0.111, 1.753)], [0.020, 0.022, 0.0018], [0.009, 0.009, 0.0014]),
            # Side locks frame the cheeks and deliberately differ left/right.
            ("Temple_L_Long", [(-0.087, 0.025, 1.778), (-0.115, 0.049, 1.710), (-0.111, 0.058, 1.642)], [0.025, 0.022, 0.002], [0.011, 0.009, 0.0015]),
            ("Temple_R_Short", [(0.091, 0.022, 1.778), (0.119, 0.048, 1.713), (0.114, 0.056, 1.666)], [0.023, 0.020, 0.002], [0.010, 0.009, 0.0015]),
            # Crown locks break the cap silhouette without random spikes.
            ("Crown_Sweep_L", [(-0.074, -0.005, 1.790), (-0.055, -0.022, 1.826), (-0.015, -0.028, 1.839)], [0.023, 0.020, 0.002], [0.009, 0.008, 0.0015]),
            ("Crown_Sweep_R", [(0.012, -0.008, 1.813), (0.051, -0.018, 1.835), (0.082, -0.004, 1.807)], [0.023, 0.020, 0.002], [0.009, 0.008, 0.0015]),
            # Back locks overlap the scalp and create a readable rear silhouette.
            ("Back_L_Layer", [(-0.060, -0.071, 1.778), (-0.091, -0.092, 1.708), (-0.074, -0.089, 1.638)], [0.028, 0.026, 0.002], [0.010, 0.009, 0.0015]),
            ("Back_R_Layer", [(0.050, -0.073, 1.779), (0.087, -0.093, 1.714), (0.072, -0.088, 1.651)], [0.028, 0.024, 0.002], [0.010, 0.009, 0.0015]),
        ]

    for name, points, widths, thicknesses in locks:
        add_sweep(
            f"Hair_{name}",
            points,
            widths,
            thicknesses,
            material,
            "hair",
            sides=5,
            samples_per_segment=2,
        )


def build_head(mats, features):
    add_mesh(
        "Neck_Loft",
        horizontal_loft(
            [
                (1.405, 0.0, -0.005, 0.061, 0.054),
                (1.475, 0.0, 0.000, 0.054, 0.052),
                (1.545, 0.0, 0.008, 0.060, 0.057),
            ],
            segments=12,
            exponent=2.2,
        ),
        mats["skin"],
        "head",
    )
    add_mesh(
        "Head_Anatomical_Loft",
        horizontal_loft(
            [
                (1.505, 0.0, 0.018, 0.052, 0.052),
                (1.530, 0.0, 0.009, 0.087, 0.075),
                (1.575, 0.0, 0.002, 0.111, 0.091),
                (1.630, 0.0, 0.000, 0.120, 0.099),
                (1.685, 0.0, -0.002, 0.115, 0.096),
                (1.740, 0.0, -0.004, 0.103, 0.086),
                (1.785, 0.0, -0.006, 0.071, 0.062),
            ],
            segments=16,
            exponent=2.25,
            phase=math.pi / 16.0,
        ),
        mats["skin"],
        "head",
    )
    if features.get("ears", True):
        for sign, side in ((-1, "L"), (1, "R")):
            create_ico_object(
                f"Ear_{side}",
                (sign * 0.119, 0.001, 1.632),
                (0.018, 0.016, 0.034),
                mats["skin"],
                subdivisions=2,
                part="face",
            )
    for sign, side in ((-1, "L"), (1, "R")):
        eye_x = sign * 0.047
        add_mesh(
            f"Eye_White_{side}",
            almond_lens((eye_x, 0.098, 1.646), 0.030, 0.010, 0.006),
            mats["eyewhite"],
            "face",
        )
        add_mesh(
            f"Iris_{side}",
            almond_lens((eye_x + sign * 0.002, 0.102, 1.646), 0.009, 0.0085, 0.003),
            mats["eyes"],
            "face",
        )
        add_mesh(
            f"Pupil_{side}",
            almond_lens((eye_x + sign * 0.002, 0.104, 1.646), 0.0035, 0.006, 0.002),
            mats["hair"],
            "face",
        )
        add_sweep(
            f"Upper_Eyelid_{side}",
            [
                (eye_x - 0.030, 0.101, 1.647),
                (eye_x, 0.104, 1.657),
                (eye_x + 0.030, 0.101, 1.647),
            ],
            [0.0018, 0.0024, 0.0015],
            [0.0015, 0.0018, 0.0012],
            mats["hair"],
            "face",
            sides=5,
            samples_per_segment=2,
        )
        if features.get("eyebrows", True):
            add_sweep(
                f"Eyebrow_{side}",
                [
                    (eye_x - 0.031, 0.096, 1.679),
                    (eye_x, 0.100, 1.686),
                    (eye_x + 0.032, 0.094, 1.681),
                ],
                [0.0025, 0.0040, 0.0018],
                [0.0020, 0.0025, 0.0015],
                mats["hair"],
                "face",
                sides=5,
                samples_per_segment=2,
            )
    if features.get("nose", True):
        add_mesh(
            "Nose_Bridge_And_Tip",
            horizontal_loft(
                [
                    (1.599, 0.0, 0.103, 0.020, 0.010),
                    (1.615, 0.0, 0.116, 0.015, 0.020),
                    (1.664, 0.0, 0.098, 0.009, 0.007),
                ],
                segments=6,
                exponent=1.8,
                phase=math.pi / 6.0,
            ),
            mats["skin"],
            "face",
        )
    if features.get("mouth", True):
        add_sweep(
            "Mouth_Line",
            [(-0.025, 0.093, 1.568), (0.0, 0.099, 1.565), (0.025, 0.093, 1.568)],
            [0.0012, 0.0018, 0.0012],
            [0.0010, 0.0014, 0.0010],
            mats["mouth"],
            "face",
            sides=5,
            samples_per_segment=2,
        )
    if features.get("beard", False):
        for index in range(5):
            x = -0.050 + index * 0.025
            add_sweep(
                f"Beard_Lock_{index + 1}",
                [(x, 0.075, 1.555), (x * 0.75, 0.086, 1.525), (x * 0.45, 0.070, 1.500)],
                [0.013, 0.012, 0.002],
                [0.005, 0.005, 0.0015],
                mats["hair"],
                "hair",
                sides=5,
                samples_per_segment=1,
            )
    build_hair(mats["hair"], features.get("hair_style", "side_swept"))


def build_clothing(mats, features, outfit):
    add_mesh(
        "Pelvis_Trouser_Loft",
        horizontal_loft(
            [
                (0.800, 0.0, 0.0, 0.145, 0.083),
                (0.865, 0.0, 0.0, 0.166, 0.091),
                (0.955, 0.0, 0.0, 0.158, 0.089),
            ],
            segments=12,
            exponent=2.8,
        ),
        mats["suit"],
        "clothing",
    )
    add_mesh(
        "Jacket_Tailored_Torso",
        horizontal_loft(
            [
                (0.865, 0.0, 0.0, 0.157, 0.091),
                (0.940, 0.0, 0.0, 0.151, 0.087),
                (1.080, 0.0, 0.0, 0.170, 0.099),
                (1.240, 0.0, 0.0, 0.207, 0.111),
                (1.350, 0.0, -0.003, 0.229, 0.104),
                (1.405, 0.0, -0.006, 0.191, 0.083),
            ],
            segments=16,
            exponent=3.1,
            phase=math.pi / 16.0,
        ),
        mats["suit"],
        "clothing",
    )
    if outfit.get("shirt", True):
        shirt = [(-0.064, 1.423), (0.064, 1.423), (0.079, 1.285), (0.040, 1.170), (0.0, 1.120), (-0.040, 1.170), (-0.079, 1.285)]
        add_panel("Shirt_Shaped_Front", shirt, 0.119, 0.105, mats["shirt"])
        collar_left = [(-0.071, 1.438), (-0.008, 1.416), (-0.037, 1.356), (-0.091, 1.407)]
        add_panel("Collar_L", collar_left, 0.139, 0.121, mats["shirt"], bevel=0.001)
        add_panel("Collar_R", mirrored_outline(collar_left), 0.139, 0.121, mats["shirt"], bevel=0.001)
    if outfit.get("lapels", True):
        lapel_left = [
            (-0.077, 1.431),
            (-0.177, 1.366),
            (-0.139, 1.322),
            (-0.157, 1.298),
            (-0.047, 1.112),
            (-0.071, 1.270),
        ]
        add_panel("Lapel_Notched_L", lapel_left, 0.135, 0.113, mats["lapel"], bevel=0.0015)
        add_panel("Lapel_Notched_R", mirrored_outline(lapel_left), 0.135, 0.113, mats["lapel"], bevel=0.0015)
    if outfit.get("tie", True):
        add_panel(
            "Tie_Knot",
            [(-0.025, 1.414), (0.0, 1.430), (0.025, 1.414), (0.018, 1.377), (-0.018, 1.377)],
            0.130,
            0.119,
            mats["tie"],
            bevel=0.001,
        )
        add_panel(
            "Tie_Blade",
            [(-0.017, 1.382), (0.017, 1.382), (0.025, 1.176), (0.0, 1.146), (-0.025, 1.176)],
            0.128,
            0.117,
            mats["tie"],
            bevel=0.001,
        )
        add_panel(
            "Tie_Clip_Subtle_Gold",
            [(-0.023, 1.239), (0.023, 1.239), (0.023, 1.233), (-0.023, 1.233)],
            0.134,
            0.129,
            mats["gold"],
        )
    if features.get("pocket_square", True):
        add_panel(
            "Pocket_Square",
            [(0.119, 1.315), (0.174, 1.315), (0.164, 1.343), (0.145, 1.330), (0.130, 1.346)],
            0.124,
            0.112,
            mats["shirt"],
        )
    if features.get("gold_buttons", True):
        for index, z in enumerate((1.075, 0.995), start=1):
            create_ico_object(
                f"Jacket_Button_{index}",
                (0.025, tailored_front_y(z) + 0.012, z),
                (0.008, 0.004, 0.008),
                mats["gold"],
                subdivisions=1,
                part="clothing",
            )
    for sign, side in ((-1, "L"), (1, "R")):
        add_panel(
            f"Jacket_Pocket_Welt_{side}",
            [
                (sign * 0.090 - 0.034, 1.035),
                (sign * 0.090 + 0.034, 1.035),
                (sign * 0.090 + 0.032, 1.022),
                (sign * 0.090 - 0.032, 1.022),
            ],
            0.102,
            0.092,
            mats["lapel"],
        )


def build_legs_and_shoes(mats):
    for sign, side in ((-1, "L"), (1, "R")):
        add_mesh(
            f"Trouser_Leg_{side}",
            horizontal_loft(
                [
                    (0.105, sign * 0.106, 0.012, 0.064, 0.067),
                    (0.180, sign * 0.106, 0.005, 0.071, 0.072),
                    (0.440, sign * 0.103, 0.000, 0.075, 0.076),
                    (0.570, sign * 0.099, 0.000, 0.071, 0.074),
                    (0.790, sign * 0.091, 0.000, 0.090, 0.091),
                    (0.905, sign * 0.084, 0.000, 0.098, 0.094),
                ],
                segments=10,
                exponent=2.35,
            ),
            mats["suit"],
            "legs",
        )
        points = [
            (sign * 0.106, -0.090, 0.062),
            (sign * 0.106, 0.005, 0.055),
            (sign * 0.106, 0.135, 0.044),
            (sign * 0.106, 0.205, 0.039),
        ]
        add_sweep(
            f"Shoe_Last_{side}",
            points,
            [0.044, 0.058, 0.062, 0.023],
            [0.041, 0.039, 0.029, 0.014],
            mats["shoe"],
            "shoes",
            sides=8,
            samples_per_segment=2,
            thickness_reference=(0.0, 0.0, 1.0),
        )
        add_sweep(
            f"Shoe_Sole_{side}",
            [(x, y, 0.025) for x, y, _ in points],
            [0.046, 0.061, 0.064, 0.024],
            [0.012, 0.012, 0.010, 0.008],
            mats["sole"],
            "shoes",
            sides=8,
            samples_per_segment=2,
            thickness_reference=(0.0, 0.0, 1.0),
        )


def build_hand(sign, side, mats):
    add_sweep(
        f"Palm_Loft_{side}",
        [
            (sign * 0.723, 0.005, 1.315),
            (sign * 0.750, 0.006, 1.315),
            (sign * 0.782, 0.004, 1.314),
            (sign * 0.801, 0.001, 1.313),
        ],
        [0.032, 0.043, 0.044, 0.033],
        [0.018, 0.022, 0.021, 0.016],
        mats["skin"],
        "hands",
        sides=8,
        samples_per_segment=1,
    )
    finger_offsets = (-0.030, -0.010, 0.011, 0.031)
    lengths = (0.054, 0.074, 0.079, 0.063)
    for index, (offset, finger_length) in enumerate(zip(finger_offsets, lengths), start=1):
        z = 1.313 + offset
        add_sweep(
            f"Finger_{side}_{index}_Three_Joints",
            [
                (sign * 0.789, 0.002, z),
                (sign * (0.789 + finger_length * 0.38), -0.001, z + offset * 0.08),
                (sign * (0.789 + finger_length * 0.73), -0.009, z + offset * 0.12),
                (sign * (0.789 + finger_length), -0.021, z + offset * 0.15),
            ],
            [0.0090, 0.0082, 0.0072, 0.0048],
            [0.0085, 0.0080, 0.0068, 0.0045],
            mats["skin"],
            "hands",
            sides=6,
            samples_per_segment=1,
        )
    add_sweep(
        f"Thumb_{side}_Opposed",
        [
            (sign * 0.746, 0.002, 1.344),
            (sign * 0.770, -0.006, 1.365),
            (sign * 0.798, -0.016, 1.374),
            (sign * 0.817, -0.026, 1.367),
        ],
        [0.013, 0.011, 0.009, 0.005],
        [0.012, 0.010, 0.008, 0.0045],
        mats["skin"],
        "hands",
        sides=6,
        samples_per_segment=1,
    )


def build_arms_and_hands(mats, outfit):
    for sign, side in ((-1, "L"), (1, "R")):
        add_sweep(
            f"Sleeve_Continuous_{side}",
            [
                (sign * 0.195, -0.002, 1.366),
                (sign * 0.310, 0.000, 1.367),
                (sign * 0.490, 0.002, 1.344),
                (sign * 0.620, 0.004, 1.326),
                (sign * 0.724, 0.005, 1.315),
            ],
            [0.091, 0.088, 0.069, 0.061, 0.046],
            [0.086, 0.082, 0.067, 0.058, 0.044],
            mats["suit"],
            "clothing",
            sides=10,
            samples_per_segment=1,
        )
        if outfit.get("cuffs", True):
            add_sweep(
                f"Shirt_Cuff_{side}",
                [(sign * 0.704, 0.005, 1.318), (sign * 0.735, 0.005, 1.313)],
                [0.047, 0.044],
                [0.045, 0.042],
                mats["shirt"],
                "clothing",
                sides=10,
                samples_per_segment=1,
            )
        build_hand(sign, side, mats)


def build_character(cfg):
    palette = cfg.get("palette", {})
    features = cfg.get("features", {})
    outfit = cfg.get("outfit", {})
    suit_color = palette.get("suit", "#171622")
    mats = {
        "skin": make_material("MAT_Skin", palette.get("skin", "#C98F73"), roughness=0.78),
        "hair": make_material("MAT_Hair", palette.get("hair", "#111116"), roughness=0.72, specular=0.16),
        "suit": make_material("MAT_Suit", suit_color, roughness=0.84),
        "lapel": make_material("MAT_Suit_Lapel", lighten(suit_color, 0.075), roughness=0.76),
        "shirt": make_material("MAT_Shirt", palette.get("shirt", "#E9E5EE"), roughness=0.86),
        "tie": make_material("MAT_Tie", palette.get("tie", "#6B42A0"), roughness=0.67),
        "eyes": make_material("MAT_Eyes", features.get("eye_color", palette.get("eyes", "#8A57E8")), metallic=0.05, roughness=0.30),
        "eyewhite": make_material("MAT_EyeWhite", palette.get("eyewhite", "#F6F2F7"), roughness=0.42),
        "shoe": make_material("MAT_Shoes", palette.get("shoe", "#100F15"), roughness=0.76, specular=0.14),
        "sole": make_material("MAT_Shoe_Soles", "#08080B", roughness=0.90),
        "gold": make_material("MAT_Gold_Details", palette.get("gold", "#C5A253"), metallic=0.58, roughness=0.36),
        "mouth": make_material("MAT_Mouth", "#713C49", roughness=0.82),
    }
    build_legs_and_shoes(mats)
    build_clothing(mats, features, outfit)
    build_head(mats, features)
    build_arms_and_hands(mats, outfit)
    root = bpy.data.objects.new("CHARACTER_ROOT_STATIC", None)
    bpy.context.scene.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.10
    root["generator_version"] = GENERATOR_VERSION
    root["coordinate_system"] = "Z up; character faces +Y"
    root["rig_status"] = "none_static_multipart"
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            obj.parent = root
    scale = float(cfg.get("scale", 1.0))
    if abs(scale - 1.0) > 1.0e-6:
        for obj in list(bpy.context.scene.objects):
            if obj.type != "MESH":
                continue
            for vertex in obj.data.vertices:
                vertex.co *= scale
            obj.location *= scale
            for modifier in obj.modifiers:
                if modifier.type == "BEVEL":
                    modifier.width *= scale
    return mats


def setup_scene(cfg):
    scene = bpy.context.scene
    render_cfg = cfg.get("render", {})
    resolution = int(render_cfg.get("resolution", 900))
    samples = int(render_cfg.get("samples", 24))
    scale = float(cfg.get("scale", 1.0))
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = bool(render_cfg.get("transparent", False))
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    scene.render.image_settings.color_mode = "RGBA" if scene.render.film_transparent else "RGB"
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "Medium High Contrast"
    except (TypeError, ValueError):
        try:
            scene.view_settings.look = "None"
        except (TypeError, ValueError):
            pass
    scene.world.color = (0.055, 0.050, 0.070)

    def area_light(name, location, energy, size, color):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy * scale * scale
        data.shape = "DISK"
        data.size = size * scale
        data.color = color
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = Vector(location) * scale
        direction = Vector((0, 0, 0.95 * scale)) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    area_light("Key_Light", (3.2, 4.0, 4.2), 500, 3.2, (1.0, 0.86, 0.78))
    area_light("Fill_Light", (-3.5, 2.7, 2.8), 340, 3.0, (0.72, 0.78, 1.0))
    area_light("Rim_Light", (0.2, -3.0, 3.4), 600, 2.4, (0.64, 0.48, 1.0))
    scene.render.image_settings.color_depth = "8"
    scene.camera = None


def aim_camera(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    aim_camera(camera, target)
    return camera


def object_dimensions(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        return {"x": 0.0, "y": 0.0, "z": 0.0}
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {axis: round(maxs[i] - mins[i], 5) for i, axis in enumerate(("x", "y", "z"))}


def export_asset(fmt, outdir):
    fmt = fmt.lower()
    selected_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in selected_meshes:
        obj.select_set(True)
    if selected_meshes:
        bpy.context.view_layer.objects.active = selected_meshes[0]
    if fmt in ("glb", "gltf"):
        ext = "glb" if fmt == "glb" else "gltf"
        path = outdir / f"character.{ext}"
        result = bpy.ops.export_scene.gltf(
            filepath=str(path),
            export_format="GLB" if fmt == "glb" else "GLTF_SEPARATE",
            use_selection=True,
            export_apply=True,
            export_extras=True,
        )
    elif fmt == "fbx":
        path = outdir / "character.fbx"
        result = bpy.ops.export_scene.fbx(
            filepath=str(path),
            use_selection=True,
            apply_scale_options="FBX_SCALE_ALL",
            bake_space_transform=False,
            add_leaf_bones=False,
        )
    elif fmt == "obj":
        path = outdir / "character.obj"
        if hasattr(bpy.ops.wm, "obj_export"):
            result = bpy.ops.wm.obj_export(
                filepath=str(path),
                export_selected_objects=True,
                apply_modifiers=True,
                export_materials=True,
                forward_axis="NEGATIVE_Z",
                up_axis="Y",
            )
        elif hasattr(bpy.ops.export_scene, "obj"):
            result = bpy.ops.export_scene.obj(
                filepath=str(path), use_selection=True, use_materials=True, axis_forward="-Z", axis_up="Y"
            )
        else:
            raise RuntimeError("OBJ exporter is unavailable in this Blender installation")
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    if "FINISHED" not in result or not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Export failed for {fmt}: {path}")
    return path


def render_views(outdir, scale):
    scene = bpy.context.scene
    views = {
        "front": ((0, 4.8 * scale, 0.98 * scale), (0, 0, 0.92 * scale), 2.08 * scale),
        "side": ((4.8 * scale, 0, 0.98 * scale), (0, 0, 0.92 * scale), 2.08 * scale),
        "back": ((0, -4.8 * scale, 0.98 * scale), (0, 0, 0.92 * scale), 2.08 * scale),
        "threequarter": ((3.4 * scale, 4.8 * scale, 2.35 * scale), (0, 0, 0.94 * scale), 2.18 * scale),
        "head": ((0, 4.8 * scale, 1.68 * scale), (0, 0, 1.665 * scale), 0.43 * scale),
        "hand": ((2.4 * scale, 2.8 * scale, 1.75 * scale), (0.80 * scale, 0, 1.33 * scale), 0.34 * scale),
    }
    for view, (location, target, ortho_scale) in views.items():
        camera = create_camera(f"Camera_{view.title()}", location, target, ortho_scale)
        scene.camera = camera
        scene.render.filepath = str(outdir / f"preview_{view}.png")
        bpy.ops.render.render(write_still=True)
        if not (outdir / f"preview_{view}.png").exists():
            raise RuntimeError(f"Render did not produce preview_{view}.png")
        bpy.data.objects.remove(camera, do_unlink=True)


def main():
    args = parse_args()
    config_path = args.config.resolve()
    outdir = args.outdir.resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    try:
        from validate_config import validate_config
    except ImportError as exc:
        raise RuntimeError("Could not import scripts/validate_config.py; use a complete repository checkout.") from exc
    errors = validate_config(cfg)
    if errors:
        raise ValueError("Invalid configuration:\n- " + "\n- ".join(errors))
    formats = args.formats or cfg.get("exports", ["glb"])
    if not formats:
        raise ValueError("At least one export format must be requested")
    if len(set(formats)) != len(formats):
        raise ValueError("Duplicate export formats are not allowed")
    outdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights, bpy.data.materials):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    build_character(cfg)
    setup_scene(cfg)
    if args.save_blend:
        blend_path = outdir / "character.blend"
        result = bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        if "FINISHED" not in result or not blend_path.is_file():
            raise RuntimeError(f"Could not save editable Blender scene: {blend_path}")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    parts = {}
    for obj in meshes:
        part = obj.get("character_part", "unclassified")
        parts.setdefault(part, []).append(obj.name)
    report = {
        "name": cfg.get("name", "Character"),
        "generator": "ai-3d-character-creator",
        "generator_version": GENERATOR_VERSION,
        "blender_version": bpy.app.version_string,
        "mesh_object_count": len(meshes),
        "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
        "polygon_count": sum(len(obj.data.polygons) for obj in meshes),
        "triangle_count_base_mesh": sum(sum(len(poly.vertices) - 2 for poly in obj.data.polygons) for obj in meshes),
        "dimensions": object_dimensions(meshes),
        "materials": sorted({mat.name for obj in meshes for mat in obj.data.materials if mat}),
        "part_manifest": {key: sorted(value) for key, value in sorted(parts.items())},
        "requested_formats": list(formats),
        "source_scene": "character.blend" if args.save_blend else None,
        "exports": [],
        "preview_renders": [],
        "visual_review": {
            "status": "required_not_performed_by_generator",
            "reference_comparison": "not_performed_no_reference_input",
        },
        "notes": [
            "Editable static multi-part low-poly character; no armature, skin weights, UV workflow, or animation certification.",
            "Structural checks and visual inspection are separate required gates.",
        ],
    }
    for fmt in formats:
        path = export_asset(fmt, outdir)
        report["exports"].append({"format": fmt, "path": path.name, "bytes": path.stat().st_size})
    if args.render_views and not args.no_render:
        render_views(outdir, float(cfg.get("scale", 1.0)))
        report["preview_renders"] = [
            f"preview_{view}.png" for view in ("front", "side", "back", "threequarter", "head", "hand")
        ]
    (outdir / "character_config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    (outdir / "model_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
