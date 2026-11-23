"""
delta_stepping.py
Delta-Stepping séquentiel (Meyer & Sanders, 2003) pour le plus court chemin dans un graphe à poids positifs.

L'algorithme range les sommets dans des seaux de largeur Δ :
  - phase légère : on relâche les arêtes de poids <= Δ dans le seau courant, jusqu'à ce qu'il soit vide ;
  - phase lourde : on relâche les arêtes de poids > Δ une fois le seau figé.

Le résultat est identique à Dijkstra (testé dans tests/test_delta_stepping.py) ; Δ ne change que
l'ordre dans lequel les sommets sont traités, et donc le potentiel de parallélisme.

Format du graphe : `adj` est un dictionnaire {noeud: [(voisin, poids), ...]}, identique à dijkstra.py.
"""

import math
from collections import defaultdict

import numpy as np


def calibrate_delta(weights, percentile=25.0):
    """Δ = percentile des poids d'arêtes finis et strictement positifs (25e percentile par défaut)."""
    w = np.array([x for x in weights if math.isfinite(x) and x > 0], dtype=float)
    if w.size == 0:
        return 1.0
    return float(np.percentile(w, percentile))


def delta_stepping(adj, source, target, delta):
    """Plus court chemin de `source` à `target` par Delta-Stepping.

    Retourne (cost, path) : cost = +inf et path = [] si `target` est inaccessible.
    """
    if delta <= 0:
        raise ValueError("delta doit être strictement positif")

    dist = {source: 0.0}
    prev = {source: None}
    buckets = defaultdict(set)
    buckets[0].add(source)

    def bucket_of(d):
        return int(d // delta)

    def relax(u, v, w):
        if math.isinf(w):
            return
        nd = dist[u] + w
        if nd < dist.get(v, math.inf):
            if v in dist:
                buckets[bucket_of(dist[v])].discard(v)
            dist[v] = nd
            prev[v] = u
            buckets[bucket_of(nd)].add(v)

    while True:
        active = [k for k, b in buckets.items() if b]
        if not active:
            break
        i = min(active)
        if target in dist and i > bucket_of(dist[target]):
            break  # le seau de la cible est figé

        settled = set()
        while buckets[i]:  # phase légère : le seau i peut se remplir à nouveau
            current = set(buckets[i])
            buckets[i].clear()
            settled |= current
            for u in current:
                for v, w in adj.get(u, ()):
                    if w <= delta:
                        relax(u, v, w)

        for u in settled:  # phase lourde
            for v, w in adj.get(u, ()):
                if w > delta:
                    relax(u, v, w)

    if target not in dist:
        return math.inf, []
    path = []
    v = target
    while v is not None:
        path.append(v)
        v = prev[v]
    path.reverse()
    return dist[target], path
