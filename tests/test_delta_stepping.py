"""Delta-Stepping doit donner le même coût que Dijkstra. Lancement : python3 -m unittest discover -s tests"""

import math
import os
import random
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pathfinding.delta_stepping import calibrate_delta, delta_stepping  # noqa: E402
from pathfinding.dijkstra import grid_graph, shortest_path  # noqa: E402


def random_digraph(n, m, seed):
    rnd = random.Random(seed)
    adj = {u: [] for u in range(n)}
    for _ in range(m):
        u, v = rnd.randrange(n), rnd.randrange(n)
        if u != v:
            adj[u].append((v, rnd.uniform(0.01, 10.0)))
    return adj


class TestDeltaStepping(unittest.TestCase):
    def test_random_digraphs_match_dijkstra(self):
        for seed in range(60):
            adj = random_digraph(40, 200, seed)
            weights = [w for edges in adj.values() for _, w in edges]
            delta = calibrate_delta(weights)
            ref, _ = shortest_path(adj, 0, 39)
            cost, path = delta_stepping(adj, 0, 39, delta)
            if math.isinf(ref):
                self.assertEqual(cost, math.inf)
                self.assertEqual(path, [])
            else:
                self.assertAlmostEqual(cost, ref, places=9)
                # arêtes parallèles possibles : on prend la plus légère entre u et v
                walk = sum(min(w for x, w in adj[u] if x == v) for u, v in zip(path, path[1:]))
                self.assertAlmostEqual(walk, cost, places=9)

    def test_grid_matches_dijkstra_for_several_deltas(self):
        rng = np.random.default_rng(1)
        n = 20
        cost = rng.uniform(0.05, 4.0, size=(n, n))
        cost[rng.random((n, n)) < 0.2] = np.inf
        cost[0, 0] = cost[n - 1, n - 1] = 1.0
        adj = grid_graph(cost)
        ref, _ = shortest_path(adj, 0, n * n - 1)
        if math.isinf(ref):
            self.skipTest("grille non connexe pour cette graine")
        weights = [w for edges in adj.values() for _, w in edges]
        for factor in (0.1, 0.5, 1.0, 2.0, 10.0):
            cost_ds, _ = delta_stepping(adj, 0, n * n - 1, calibrate_delta(weights) * factor)
            self.assertAlmostEqual(cost_ds, ref, places=9)

    def test_unreachable(self):
        adj = {0: [(1, 1.0)], 1: [], 2: []}
        self.assertEqual(delta_stepping(adj, 0, 2, 1.0), (math.inf, []))

    def test_source_equals_target(self):
        adj = {0: [(1, 1.0)], 1: []}
        self.assertEqual(delta_stepping(adj, 0, 0, 1.0), (0.0, [0]))

    def test_rejects_non_positive_delta(self):
        with self.assertRaises(ValueError):
            delta_stepping({0: []}, 0, 0, 0.0)

    def test_calibrate_delta_ignores_infinite_and_zero(self):
        self.assertAlmostEqual(calibrate_delta([0.0, math.inf, 1.0, 2.0, 3.0, 4.0], 50), 2.5)


if __name__ == "__main__":
    unittest.main()
