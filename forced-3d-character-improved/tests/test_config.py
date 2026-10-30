import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_config import validate_config  # noqa: E402


class ConfigValidationTests(unittest.TestCase):
    def test_default_config_is_valid(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_config(data), [])

    def test_reference_style_config_is_valid(self):
        data = json.loads((ROOT / "examples/dark_suit_purple_eyes.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_config(data), [])

    def test_bad_color_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["palette"]["hair"] = "black"
        self.assertTrue(any("palette.hair" in error for error in validate_config(data)))

    def test_bad_export_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["exports"] = ["stl"]
        self.assertTrue(any("unsupported export" in error for error in validate_config(data)))

    def test_scale_bounds_are_enforced(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["scale"] = 20
        self.assertTrue(any("scale" in error for error in validate_config(data)))

    def test_unsupported_pose_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["pose"] = "sitting"
        self.assertTrue(any("pose must be one of" in error for error in validate_config(data)))

    def test_unsupported_style_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["style"] = "photorealistic"
        self.assertTrue(any("style must be one of" in error for error in validate_config(data)))

    def test_unhashable_export_value_is_reported_not_crashed(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["exports"] = [{"format": "glb"}]
        errors = validate_config(data)
        self.assertTrue(any("unsupported export format" in error for error in errors))

    def test_duplicate_export_formats_are_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["exports"] = ["glb", "glb"]
        self.assertTrue(any("duplicate export format" in error for error in validate_config(data)))

    def test_non_object_configuration_is_rejected(self):
        self.assertTrue(any("root must be a JSON object" in error for error in validate_config([])))

    def test_empty_name_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["name"] = "  "
        self.assertTrue(any("name must be a non-empty string" in error for error in validate_config(data)))

    def test_feature_flags_must_be_booleans(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["features"]["beard"] = "false"
        self.assertTrue(any("features.beard must be true or false" in error for error in validate_config(data)))

    def test_unsupported_hair_style_is_rejected(self):
        data = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
        data["features"]["hair_style"] = "long_braids"
        self.assertTrue(any("features.hair_style must be one of" in error for error in validate_config(data)))


if __name__ == "__main__":
    unittest.main()
