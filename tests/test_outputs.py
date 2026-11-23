"""Tests de l'export VTK et du tracé. Lancement : python3 -m unittest discover -s tests"""

import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pathfinding.vtk_export import write_path_vtk  # noqa: E402
from visualization.plot_path import plot_path  # noqa: E402


class TestVtk(unittest.TestCase):
    def test_writes_polydata_with_point_data(self):
        pts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=float)
        with tempfile.TemporaryDirectory() as d:
            fn = os.path.join(d, "path.vtk")
            write_path_vtk(pts, fn, point_data={"cumul": [0.0, 1.0, 2.0]})
            with open(fn) as f:
                text = f.read()
        self.assertIn("DATASET POLYDATA", text)
        self.assertIn("POINTS 3 float", text)
        self.assertIn("LINES 1 4", text)
        self.assertIn("SCALARS cumul float 1", text)

    def test_rejects_bad_shapes(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_path_vtk(np.zeros((3, 2)), os.path.join(d, "x.vtk"))
            with self.assertRaises(ValueError):
                write_path_vtk(np.zeros((3, 3)), os.path.join(d, "x.vtk"), point_data={"a": [1.0]})


class TestPlot(unittest.TestCase):
    def test_saves_png(self):
        cost = np.ones((10, 12))
        cost[3, 4] = np.inf
        path = [0, 1, 2, 14, 26]
        with tempfile.TemporaryDirectory() as d:
            fn = os.path.join(d, "plot.png")
            plot_path(cost, path, nx=12, filename=fn)
            self.assertGreater(os.path.getsize(fn), 1000)


if __name__ == "__main__":
    unittest.main()
