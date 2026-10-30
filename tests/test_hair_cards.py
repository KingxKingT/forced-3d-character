import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from geometry_core import inspect_mesh  # noqa: E402
from hair_cards import build_hair_cards, hair_card_mesh  # noqa: E402


class HairCardGeometryTests(unittest.TestCase):
    def sample_points(self):
        return [
            (-0.03, 0.02, 1.80, 0.075, 0.018),
            (0.00, 0.09, 1.72, 0.052, 0.012),
            (0.025, 0.15, 1.61, 0.0025, 0.002),
        ]

    def test_hair_card_is_closed_outward_and_non_degenerate(self):
        vertices, faces = hair_card_mesh(
            self.sample_points(), face_hint=(0.0, 1.0, 0.0), samples_per_segment=2
        )
        report = inspect_mesh(vertices, faces)
        self.assertEqual(len(vertices), 20)
        self.assertEqual(report["boundary_edges"], 0)
        self.assertEqual(report["inconsistent_winding_edges"], 0)
        self.assertEqual(report["zero_area_faces"], 0)
        self.assertEqual(report["duplicate_faces"], 0)
        self.assertEqual(report["connected_components"], 1)
        self.assertGreater(report["signed_volume"], 0.0)

    def test_card_interpolates_first_and_last_center_points(self):
        points = self.sample_points()
        vertices, _ = hair_card_mesh(points, samples_per_segment=2)
        first_center = tuple(sum(vertices[i][axis] for i in range(4)) / 4 for axis in range(3))
        last_start = len(vertices) - 4
        last_center = tuple(sum(vertices[i][axis] for i in range(last_start, len(vertices))) / 4 for axis in range(3))
        for actual, expected in zip(first_center, points[0][:3]):
            self.assertAlmostEqual(actual, expected, places=7)
        for actual, expected in zip(last_center, points[-1][:3]):
            self.assertAlmostEqual(actual, expected, places=7)

    def test_named_card_builder_preserves_names_and_geometry(self):
        result = build_hair_cards([
            {
                "name": "Bang_Left",
                "face_hint": (0.0, 1.0, 0.0),
                "control_points": self.sample_points(),
            },
            {
                "name": "Temple_Right",
                "face_hint": (1.0, 0.0, 0.0),
                "control_points": self.sample_points(),
            },
        ])
        self.assertEqual([item[0] for item in result], ["Bang_Left", "Temple_Right"])
        for _, vertices, faces in result:
            self.assertTrue(vertices)
            self.assertTrue(faces)
            self.assertEqual(inspect_mesh(vertices, faces)["boundary_edges"], 0)

    def test_invalid_control_point_count_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least three"):
            hair_card_mesh([(0, 0, 0, 0.1, 0.02), (0, 0, 1, 0.01, 0.002)])

    def test_invalid_control_point_dimension_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "x, y, z, width, thickness"):
            hair_card_mesh([(0, 0, 0, 0.1), (0, 0, 1, 0.1), (0, 0, 2, 0.1)])

    def test_collapsed_width_or_thickness_is_rejected(self):
        points = self.sample_points()
        points[-1] = (*points[-1][:3], 0.0, points[-1][4])
        with self.assertRaisesRegex(ValueError, "remain positive"):
            hair_card_mesh(points)

    def test_invalid_face_hint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "face_hint"):
            hair_card_mesh(self.sample_points(), face_hint=(0.0, 1.0))

    def test_sampling_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "samples_per_segment"):
            hair_card_mesh(self.sample_points(), samples_per_segment=0)


if __name__ == "__main__":
    unittest.main()
