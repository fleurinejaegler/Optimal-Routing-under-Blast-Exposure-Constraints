"""
vtk_export.py
Écrit un chemin au format VTK « legacy ASCII POLYDATA », lisible par ParaView, sans dépendance externe.
"""

import numpy as np


def write_path_vtk(points, filename, point_data=None):
    """Écrit une polyligne reliant `points` (tableau (n, 3)).

    point_data : dictionnaire {nom: tableau de n valeurs} ajouté comme données scalaires par point.
    """
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError("points doit être de forme (n, 3)")
    n = len(pts)
    if n < 2:
        raise ValueError("un chemin contient au moins deux points")

    with open(filename, "w") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("Chemin optimal\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")
        f.write(f"POINTS {n} float\n")
        for x, y, z in pts:
            f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
        f.write(f"LINES 1 {n + 1}\n")
        f.write(f"{n} " + " ".join(str(i) for i in range(n)) + "\n")
        if point_data:
            f.write(f"POINT_DATA {n}\n")
            for name, values in point_data.items():
                vals = np.asarray(values, dtype=float)
                if vals.shape != (n,):
                    raise ValueError(f"'{name}' doit contenir {n} valeurs")
                f.write(f"SCALARS {name} float 1\n")
                f.write("LOOKUP_TABLE default\n")
                for v in vals:
                    f.write(f"{v:.6f}\n")
