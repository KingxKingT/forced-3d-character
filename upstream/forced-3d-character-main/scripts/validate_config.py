"""Validate a character configuration without requiring Blender."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_PALETTE = {"skin", "hair", "suit", "shirt", "tie", "eyes", "eyewhite", "shoe", "gold"}
VALID_FORMATS = {"glb", "gltf", "fbx", "obj"}
VALID_STYLES = {"low_poly_stylized"}
VALID_POSES = {"t_pose"}
VALID_HAIR_STYLES = {"side_swept", "short"}
BOOLEAN_FEATURES = {
    "beard", "eyebrows", "ears", "nose", "mouth", "gold_buttons", "pocket_square"
}
BOOLEAN_OUTFIT_OPTIONS = {"tie", "shirt", "lapels", "cuffs"}


def validate_config(data: Any) -> list[str]:
    """Return human-readable problems. Never execute or mutate input data."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["configuration root must be a JSON object"]

    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors.append("name must be a non-empty string")

    scale = data.get("scale", 1.0)
    if (
        not isinstance(scale, (int, float))
        or isinstance(scale, bool)
        or not math.isfinite(scale)
        or not 0.1 <= scale <= 5.0
    ):
        errors.append("scale must be a finite number between 0.1 and 5.0")

    style = data.get("style", "low_poly_stylized")
    if not isinstance(style, str) or style not in VALID_STYLES:
        errors.append("style must be one of: " + ", ".join(sorted(VALID_STYLES)))
    pose = data.get("pose", "t_pose")
    if not isinstance(pose, str) or pose not in VALID_POSES:
        errors.append("pose must be one of: " + ", ".join(sorted(VALID_POSES)))

    palette = data.get("palette")
    if not isinstance(palette, dict):
        errors.append("palette must be an object")
    else:
        missing = sorted(REQUIRED_PALETTE - set(palette))
        if missing:
            errors.append("palette missing keys: " + ", ".join(missing))
        for key, value in palette.items():
            if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
                errors.append(f"palette.{key} must be a #RRGGBB color")

    features = data.get("features", {})
    if not isinstance(features, dict):
        errors.append("features must be an object")
    else:
        if "eye_color" in features and (
            not isinstance(features["eye_color"], str)
            or not HEX_COLOR.fullmatch(features["eye_color"])
        ):
            errors.append("features.eye_color must be a #RRGGBB color")
        if "hair_style" in features and (
            not isinstance(features["hair_style"], str)
            or features["hair_style"] not in VALID_HAIR_STYLES
        ):
            errors.append("features.hair_style must be one of: " + ", ".join(sorted(VALID_HAIR_STYLES)))
        for key in sorted(BOOLEAN_FEATURES):
            if key in features and not isinstance(features[key], bool):
                errors.append(f"features.{key} must be true or false")

    outfit = data.get("outfit", {})
    if not isinstance(outfit, dict):
        errors.append("outfit must be an object")
    else:
        if "jacket" in outfit and outfit["jacket"] != "tailored":
            errors.append("outfit.jacket currently supports only 'tailored'")
        for key in sorted(BOOLEAN_OUTFIT_OPTIONS):
            if key in outfit and not isinstance(outfit[key], bool):
                errors.append(f"outfit.{key} must be true or false")

    exports = data.get("exports", ["glb"])
    if not isinstance(exports, list) or not exports:
        errors.append("exports must be a non-empty list")
    else:
        invalid = sorted({str(fmt) for fmt in exports if not isinstance(fmt, str) or fmt not in VALID_FORMATS})
        if invalid:
            errors.append("unsupported export format(s): " + ", ".join(invalid))
        valid_formats = [fmt for fmt in exports if isinstance(fmt, str) and fmt in VALID_FORMATS]
        duplicates = sorted({fmt for fmt in valid_formats if valid_formats.count(fmt) > 1})
        if duplicates:
            errors.append("duplicate export format(s): " + ", ".join(duplicates))

    render = data.get("render", {})
    if not isinstance(render, dict):
        errors.append("render must be an object")
    else:
        resolution = render.get("resolution", 900)
        if not isinstance(resolution, int) or isinstance(resolution, bool) or not 128 <= resolution <= 4096:
            errors.append("render.resolution must be an integer from 128 to 4096")
        samples = render.get("samples", 24)
        if not isinstance(samples, int) or isinstance(samples, bool) or not 1 <= samples <= 512:
            errors.append("render.samples must be an integer from 1 to 512")
        if "transparent" in render and not isinstance(render["transparent"], bool):
            errors.append("render.transparent must be true or false")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    errors = validate_config(data)
    if errors:
        print("Configuration invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Configuration valid: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
