# Optimal Routing under Blast-Exposure Constraints

Project carried out in 2026 at CentraleSupélec, in partnership with CEA-DAM: find the route from A to B that minimises the cumulative damage caused by an accidental detonation along the way. The method combines an analytical surrogate, a Gaussian process that learns the surrogate's errors, a shortest-path search, and a loop that decides where to run the next expensive simulation.

[Demo]([https://linkedin.com/in/fleurine-jaegler](https://fleurinejaegler.github.io/Optimal-Routing-under-Blast-Exposure-Constraints/demo/))

## How the method works

Method of the project, 2D and 3D pipelines from the public report :

```mermaid
flowchart LR
  S[1. Scene<br/>buildings, terrain, start A, end B] --> K[2. Cheap surrogate<br/>blast law + building masking<br/>3D: raycasting, terrain]
  K --> I[3. Initial design<br/>15 points, Latin hypercube]
  I --> X[4. Simulation<br/>2D: ARMEN, 3D: on a cluster<br/>then damage score: 20 to 300 hPa × building weights]
  X --> G[5. GP on the residuals<br/>simulator − surrogate]
  G --> R[6. Shortest path<br/>2D: Delta-Stepping<br/>3D: directional A*, turn and slope penalties]
  R --> Q{7. Stop?<br/>2D: σ cum,rel below 5 %<br/>or 19 simulations}
  Q -- no --> A[8. Next point<br/>2D: path-coupled corridor<br/>3D: UCB on danger]
  A --> X
  Q -- yes --> D[9. Route A to B<br/>+ stability: Hausdorff distance]
```

## Repository contents

| Folder | Contents |
|---|---|
| [`pathfinding/dijkstra.py`](pathfinding/dijkstra.py) | Dijkstra on a general graph or an 8-connected grid (with or without corner cutting) |
| [`pathfinding/delta_stepping.py`](pathfinding/delta_stepping.py) | Sequential Delta-Stepping (Meyer & Sanders, 2003), with Δ calibrated at the 25th percentile |
| [`pathfinding/vtk_export.py`](pathfinding/vtk_export.py) | Export of a path as ASCII VTK, readable in ParaView, no extra dependency |
| [`visualization/plot_path.py`](visualization/plot_path.py) | Cost map and optimal path, saved as PNG |
| [`tests/`](tests) | Unit tests; Dijkstra and Delta-Stepping are checked against a reference |
| [`demo/`](demo/README.md) | Interactive demo of the method, in the browser (JavaScript, no dependency) |
| [`docs/`](docs) | Public project report |

## Usage

```python
import numpy as np
from pathfinding.dijkstra import grid_graph, shortest_path
from pathfinding.delta_stepping import calibrate_delta, delta_stepping

cost = np.ones((50, 50))          # cost of entering each cell
cost[10:40, 25] = np.inf          # impassable cells (e.g. a building)
adj = grid_graph(cost)

start, end = 0, 50 * 50 - 1       # cell (i=0, j=0) and cell (i=49, j=49)
total, path = shortest_path(adj, start, end)

delta = calibrate_delta([w for edges in adj.values() for _, w in edges])
total_ds, path_ds = delta_stepping(adj, start, end, delta)   # same cost as Dijkstra
```

## Tests

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

For the demo: `cd demo && node --test tests/*.test.js` (Node ≥ 20).

## Demo

The `demo/` folder contains an interactive demo of the full method, from the surrogate law to the acquisition loop. It replaces the confidential simulator with a simple 2D acoustic solver. The demo's README describes the modelling choices and limitations in detail.

## Confidentiality

This project was carried out under a confidentiality agreement with CEA-DAM. **Much of the original code is confidential and is not published here**: the simulator and its integration, the supercomputer job scripts, the scene and simulation data, the mesh processing, and the 3D part of the pipeline. Only general components that do not depend on any project data are published.

The public report describes the method as a whole.
