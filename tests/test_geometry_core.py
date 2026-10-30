import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from geometry_core import (  # noqa: E402
    almond_lens,
    catmull_rom,
    extrude_xz_polygon,
    horizontal_loft,
    inspect_mesh,
    sweep_mesh,
    validate_mesh_data,
    weld_mesh,
)


def cube_mesh():
    vertices = [
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    return vertices, faces


class GeometryConstructionTests(unittest.TestCase):
    def test_horizontal_loft_is_closed_and_outward(self):
        mesh = horizontal_loft([(0, 0, 0, 1, 0.8), (1, 0, 0, 0.7, 0.6)], segments=8)
        result = inspect_mesh(*mesh)
        self.assertEqual(result["boundary_edges"], 0)
        self.assertEqual(result["inconsistent_winding_edges"], 0)
        self.assertGreater(result["signed_volume"], 0)
        self.assertEqual(result["triangles"], 28)

    def test_superellipse_changes_shape_not_ring_size(self):
        mesh = horizontal_loft(
            [(0, 0, 0, 1, 1), (1, 0, 0, 1, 1)], segments=12, exponent=4
        )
        self.assertEqual(len(mesh[0]), 24)
        self.assertTrue(all(len(face) in (3, 4, 12) for face in mesh[1]))

    def test_sweep_samples_endpoints_and_preserves_topology(self):
        points = [(0, 0, 0), (1, 0, 0), (2, 0.1, 0.2)]
        mesh = sweep_mesh(points, [0.1, 0.08, 0.03], [0.08, 0.07, 0.02], sides=6, samples_per_segment=2)
        result = inspect_mesh(*mesh)
        self.assertEqual(len(mesh[0]), 30)
        self.assertEqual(result["boundary_edges"], 0)
        self.assertEqual(result["inconsistent_winding_edges"], 0)
        self.assertGreater(result["signed_volume"], 0)
        self.assertTrue(all(math.isfinite(value) for vertex in mesh[0] for value in vertex))

    def test_vertical_sweep_handles_parallel_reference(self):
        mesh = sweep_mesh(
            [(0, 0, 0), (0, 0, 1)], [0.1, 0.05], [0.1, 0.05],
            sides=6, samples_per_segment=1, thickness_reference=(0, 0, 1),
        )
        self.assertEqual(inspect_mesh(*mesh)["zero_area_faces"], 0)

    def test_catmull_rom_interpolates_control_points(self):
        result = catmull_rom([(0, 0, 0), (1, 2, 3), (2, 0, 0)], 4)
        self.assertEqual(result[0], (0, 0, 0))
        self.assertEqual(result[4], (1, 2, 3))
        self.assertEqual(result[-1], (2, 0, 0))

    def test_panel_and_lens_are_closed_outward_solids(self):
        for mesh in (
            extrude_xz_polygon([(-1, 0), (1, 0), (1, 1), (-1, 1)], 0.2, -0.2),
            almond_lens((0, 0, 0), 0.2, 0.1, 0.02),
        ):
            result = inspect_mesh(*mesh)
            self.assertEqual(result["boundary_edges"], 0)
            self.assertEqual(result["inconsistent_winding_edges"], 0)
            self.assertGreater(result["signed_volume"], 0)

    def test_malformed_sweep_parameters_fail_before_blender(self):
        with self.assertRaises(ValueError):
            sweep_mesh([(0, 0, 0), (1, 0, 0)], [0.1], [0.1, 0.1])
        with self.assertRaises(ValueError):
            horizontal_loft([(0, 0, 0, 0, 1), (1, 0, 0, 1, 1)])

    def test_source_array_validation_rejects_bad_indices_and_repeats(self):
        with self.assertRaisesRegex(ValueError, "invalid vertex"):
            validate_mesh_data([(0, 0, 0)] * 3, [(0, 1, 9)])
        with self.assertRaisesRegex(ValueError, "repeats"):
            validate_mesh_data([(0, 0, 0)] * 3, [(0, 1, 1)])


class StructuralInspectionTests(unittest.TestCase):
    def test_cube_has_no_structural_defects(self):
        result = inspect_mesh(*cube_mesh())
        self.assertEqual(result["connected_components"], 1)
        self.assertEqual(result["duplicate_faces"], 0)
        self.assertTrue(result["edge_manifold_closed"])
        self.assertAlmostEqual(result["signed_volume"], 8.0)

    def test_open_surface_is_not_mistaken_for_closed(self):
        result = inspect_mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)])
        self.assertEqual(result["boundary_edges"], 3)
        self.assertFalse(result["edge_manifold_closed"])

    def test_duplicate_face_is_detected(self):
        vertices, faces = cube_mesh()
        faces.append(faces[0])
        self.assertEqual(inspect_mesh(vertices, faces)["duplicate_faces"], 1)

    def test_reversed_adjacent_face_is_detected(self):
        vertices, faces = cube_mesh()
        faces[0] = tuple(reversed(faces[0]))
        result = inspect_mesh(vertices, faces)
        self.assertGreater(result["inconsistent_winding_edges"], 0)

    def test_inward_closed_mesh_has_negative_volume(self):
        vertices, faces = cube_mesh()
        faces = [tuple(reversed(face)) for face in faces]
        self.assertLess(inspect_mesh(vertices, faces)["signed_volume"], 0)

    def test_disconnected_components_are_counted(self):
        vertices, faces = cube_mesh()
        offset = len(vertices)
        vertices += [(x + 4, y, z) for x, y, z in list(vertices)]
        faces += [tuple(index + offset for index in face) for face in list(faces)]
        self.assertEqual(inspect_mesh(vertices, faces)["connected_components"], 2)

    def test_zero_length_edge_and_coincident_vertex_are_detected(self):
        result = inspect_mesh([(0, 0, 0), (0, 0, 0), (0, 1, 0)], [(0, 1, 2)])
        self.assertEqual(result["zero_length_edges"], 1)
        self.assertEqual(result["zero_area_faces"], 1)
        self.assertGreaterEqual(result["coincident_vertices"], 1)

    def test_welding_restores_split_cube_topology_for_analysis(self):
        vertices, faces = cube_mesh()
        split_vertices = [vertex for face in faces for vertex_index in face for vertex in [vertices[vertex_index]]]
        split_faces = []
        for face_index in range(len(faces)):
            start = face_index * 4
            split_faces.append(tuple(range(start, start + 4)))
        self.assertEqual(inspect_mesh(split_vertices, split_faces)["boundary_edges"], 24)
        welded = weld_mesh(split_vertices, split_faces)
        result = inspect_mesh(*welded)
        self.assertEqual(result["vertices"], 8)
        self.assertEqual(result["boundary_edges"], 0)

    def test_non_planar_quad_is_detected(self):
        result = inspect_mesh(
            [(0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 0)], [(0, 1, 2, 3)]
        )
        self.assertEqual(result["non_planar_ngons"], 1)


if __name__ == "__main__":
    unittest.main()
