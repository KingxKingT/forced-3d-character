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


if __name__ == "__main__":
    unittest.main()
