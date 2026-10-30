"""Optional real Blender integration test; skipped when Blender is unavailable.

Set REQUIRE_BLENDER=1 to turn a missing executable into a failure. Set
BLENDER_BIN to a non-standard executable path. This test builds geometry,
exports GLB, saves a .blend, re-imports the export, and renders inspection views.
It still does not assert artistic quality or resemblance to a reference.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLENDER = os.environ.get("BLENDER_BIN") or shutil.which("blender")


class BlenderRequirementTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("REQUIRE_BLENDER") == "1", "Blender is optional in this run")
    def test_blender_is_available_when_required(self):
        self.assertIsNotNone(BLENDER, "REQUIRE_BLENDER=1 but no Blender executable was found")


@unittest.skipUnless(BLENDER, "Blender executable not found; runtime test not run")
class BlenderIntegrationTests(unittest.TestCase):
    def run_blender(self, *arguments):
        command = [BLENDER, "--background", "--factory-startup", "--python-exit-code", "1", *arguments]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=300)
        if completed.returncode:
            self.fail(
                "Blender command failed:\n"
                + " ".join(command)
                + "\nSTDOUT:\n"
                + completed.stdout[-8000:]
                + "\nSTDERR:\n"
                + completed.stderr[-4000:]
            )

    def test_generate_validate_roundtrip_and_render(self):
        with tempfile.TemporaryDirectory(prefix="character-blender-test-") as temporary:
            outdir = Path(temporary)
            config = json.loads((ROOT / "configs/default_character.json").read_text(encoding="utf-8"))
            config["exports"] = ["glb"]
            config["render"]["resolution"] = 256
            config["render"]["samples"] = 4
            config_path = outdir / "test_config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            generator_args = [
                "--python", str(ROOT / "scripts/blender/create_character.py"), "--",
                "--config", str(config_path), "--outdir", str(outdir),
                "--formats", "glb", "--save-blend",
            ]
            if os.environ.get("SKIP_BLENDER_RENDER") != "1":
                generator_args.append("--render-views")
            self.run_blender(*generator_args)
            self.assertTrue((outdir / "character.blend").is_file())
            self.assertTrue((outdir / "character.glb").stat().st_size > 0)
            self.run_blender(
                str(outdir / "character.blend"),
                "--python", str(ROOT / "scripts/blender/validate_mesh.py"), "--",
                "--report", str(outdir / "source-validation.json"),
                "--max-triangles", "6000", "--strict-budget",
                "--require-watertight", "--require-single-component",
                "--require-character-parts", "--strict-winding",
            )
            self.run_blender(
                "--python", str(ROOT / "scripts/blender/validate_character.py"), "--",
                "--file", str(outdir / "character.glb"),
                "--report", str(outdir / "roundtrip-validation.json"),
                "--require-character-parts",
            )
            source = json.loads((outdir / "source-validation.json").read_text(encoding="utf-8"))
            roundtrip = json.loads((outdir / "roundtrip-validation.json").read_text(encoding="utf-8"))
            self.assertTrue(source["passed"])
            self.assertTrue(roundtrip["passed"])
            self.assertGreater(source["totals"]["triangles"], 500)
            self.assertEqual(roundtrip["visual_review"]["status"], "not_tested")
            if os.environ.get("SKIP_BLENDER_RENDER") != "1":
                for view in ("front", "side", "back", "threequarter", "head", "hand"):
                    self.assertTrue((outdir / f"preview_{view}.png").stat().st_size > 100)


if __name__ == "__main__":
    unittest.main()
