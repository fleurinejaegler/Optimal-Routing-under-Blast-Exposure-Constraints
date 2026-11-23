"""
dijkstra.py
Plus court chemin de Dijkstra, sur un graphe quelconque ou sur une grille 2D.

Deux usages :
  - graphe général : `adj` est un dictionnaire {noeud: [(voisin, poids), ...]}, poids >= 0 ;
  - grille 2D      : `grid_graph(cost)` construit ce dictionnaire à partir d'une matrice de coûts.

Un poids égal à +inf représente une case ou une arête infranchissable.
"""

import heapq
import math

import numpy as np


def dijkstra(adj, source, target=None):
    """Distances minimales depuis `source`. S'arrête dès que `target` est définitivement fixé.

    Retourne (dist, prev) : dist[v] = coût minimal, prev[v] = prédécesseur sur ce chemin.
    """
    dist = {source: 0.0}
    prev = {source: None}
    done = set()
    heap = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        if u == target:
            break
        for v, w in adj.get(u, ()):
            if math.isinf(w):
                continue
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    return dist, prev


def shortest_path(adj, source, target):
    """Retourne (coût, liste des noeuds du chemin). Coût = +inf et chemin vide si inaccessible."""
    dist, prev = dijkstra(adj, source, target)
    if target not in dist:
        return math.inf, []
    path = []
    v = target
    while v is not None:
        path.append(v)
        v = prev[v]
    path.reverse()
    return dist[target], path


def grid_graph(cost, allow_corner_cutting=False):
    """Graphe 8-connexe d'une grille `cost` (tableau 2D, cost[j, i] = coût d'entrer dans la case (i, j)).

    - le noeud de la case (i, j) est l'entier j * nx + i ;
    - le poids de u vers v est cost[v] * d, avec d = 1 (axe) ou sqrt(2) (diagonale) ;
    - par défaut, une diagonale n'est autorisée que si les deux cases voisines orthogonales sont
      franchissables (pas de coupe de coin) ; `allow_corner_cutting=True` lève cette contrainte.
    """
    cost = np.asarray(cost, dtype=float)
    ny, nx = cost.shape
    moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
    adj = {}
    for j in range(ny):
        for i in range(nx):
            u = j * nx + i
            if math.isinf(cost[j, i]):
                continue
            edges = []
            for di, dj, d in moves:
                ni, nj = i + di, j + dj
                if not (0 <= ni < nx and 0 <= nj < ny):
                    continue
                if math.isinf(cost[nj, ni]):
                    continue
                if not allow_corner_cutting and di != 0 and dj != 0 and (math.isinf(cost[j, ni]) or math.isinf(cost[nj, i])):
                    continue
                edges.append((nj * nx + ni, cost[nj, ni] * d))
            adj[u] = edges
    return adj
