"""Tests de pathfinding/dijkstra.py. Lancement : python3 -m unittest discover -s tests"""

import math
import os
import sys
import unittest

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra as scipy_dijkstra

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pathfinding.dijkstra import dijkstra, grid_graph, shortest_path  # noqa: E402


class TestGenericGraph(unittest.TestCase):
    def test_small_graph(self):
        adj = {
            "A": [("B", 1.0), ("C", 4.0)],
            "B": [("C", 2.0), ("D", 5.0)],
            "C": [("D", 1.0)],
            "D": [],
        }
        cost, path = shortest_path(adj, "A", "D")
        self.assertAlmostEqual(cost, 4.0)
        self.assertEqual(path, ["A", "B", "C", "D"])

    def test_unreachable(self):
        adj = {0: [(1, 1.0)], 1: [], 2: []}
        cost, path = shortest_path(adj, 0, 2)
        self.assertEqual(cost, math.inf)
        self.assertEqual(path, [])

    def test_infinite_edges_are_ignored(self):
        adj = {0: [(1, math.inf), (2, 3.0)], 2: [(1, 1.0)], 1: []}
        cost, path = shortest_path(adj, 0, 1)
        self.assertAlmostEqual(cost, 4.0)
        self.assertEqual(path, [0, 2, 1])


class TestGrid(unittest.TestCase):
    def test_matches_scipy_on_random_grids(self):
        rng = np.random.default_rng(0)
        checked = 0
        for _ in range(30):
            n = 25
            cost = rng.uniform(0.01, 5.0, size=(n, n))
            cost[rng.random((n, n)) < 0.2] = np.inf
            cost[0, 0] = cost[n - 1, n - 1] = 1.0
            adj = grid_graph(cost)

            # même graphe pour scipy
            rows, cols, data = [], [], []
            for u, edges in adj.items():
                for v, w in edges:
                    rows.append(u)
                    cols.append(v)
                    data.append(w)
            G = csr_matrix((data, (rows, cols)), shape=(n * n, n * n))
            ref = scipy_dijkstra(G, directed=True, indices=0)[n * n - 1]

            ours, path = shortest_path(adj, 0, n * n - 1)
            if math.isinf(ref):
                self.assertEqual(ours, math.inf)
                continue
            checked += 1
            self.assertAlmostEqual(ours, ref, places=9)
            # le chemin rendu doit avoir exactement ce coût
            walk = sum(dict(adj[u])[v] for u, v in zip(path, path[1:]))
            self.assertAlmostEqual(walk, ours, places=9)
        self.assertGreater(checked, 10)

    def test_no_corner_cutting(self):
        # Deux cases bloquées en diagonale : le passage direct est interdit.
        cost = np.array([[1.0, np.inf],
                         [np.inf, 1.0]])
        adj = grid_graph(cost)
        self.assertNotIn(3, [v for v, _ in adj[0]])


if __name__ == "__main__":
    unittest.main()
