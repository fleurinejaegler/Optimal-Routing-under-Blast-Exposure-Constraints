"""
plot_path.py
Affiche une carte de coûts (heatmap) et le chemin optimal dessus.

Les cases infranchissables (coût +inf) sont grisées. La couleur du chemin suit le coût local.
"""

import matplotlib

matplotlib.use("Agg")  # figure écrite dans un fichier, sans fenêtre
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def plot_path(cost, path, nx, filename, title="Chemin optimal"):
    """Sauvegarde la carte `cost` (tableau (ny, nx)) et le chemin `path` (indices j * nx + i)."""
    cost = np.asarray(cost, dtype=float)
    ny = cost.shape[0]
    masked = np.ma.masked_invalid(cost)

    fig, ax = plt.subplots(figsize=(6, 5.2))
    im = ax.imshow(masked, origin="lower", cmap="YlOrRd", interpolation="nearest")
    ax.set_facecolor("#444444")  # cases infranchissables
    fig.colorbar(im, ax=ax, label="coût local")

    if len(path) >= 2:
        xs = [v % nx for v in path]
        ys = [v // nx for v in path]
        ax.plot(xs, ys, color="#1f5fa8", linewidth=2.2, label="chemin")
        ax.scatter([xs[0]], [ys[0]], color="green", zorder=3, label="A")
        ax.scatter([xs[-1]], [ys[-1]], color="red", zorder=3, label="B")
        ax.legend(loc="upper left")

    ax.set_title(title)
    ax.set_xlim(-0.5, nx - 0.5)
    ax.set_ylim(-0.5, ny - 0.5)
    fig.tight_layout()
    fig.savefig(filename, dpi=120)
    plt.close(fig)
    return filename
