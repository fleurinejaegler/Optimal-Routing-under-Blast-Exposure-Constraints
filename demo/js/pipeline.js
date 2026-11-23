// Glue between the pure modules: initial design, GP posterior, route, next point.
// Shared by the guided experience (main.js) and the headless tests. No DOM.

import { N } from './scene.js';
import { makeRng } from './rng.js';
import { fitGP, predictGrid } from './gp.js';
import { clipWeights, deltaFor, deltaStepping, pathLength, pathCost } from './path.js';
import { corridorMask, eligibleMask, acquisitionScore, sigmaRel, stopRule, N_INIT } from './acquisition.js';

// Latin-hypercube design of k points over the interior of the map (report, sec. 4.1.1):
// the range is cut into k strata along each axis, one point per stratum and per row, and
// each point is then moved to the nearest free cell of the main component that is still unused.
// Cells closer than 3 m to the border are left out (as for B): the corners threaten almost nothing.
export function initialDesign(scene, seed, k = N_INIT) {
  const lo = 3, hi = N - 3, span = (hi - lo) / k;
  const rng = makeRng((seed ^ 0x5eed) >>> 0);
  const shuffled = () => {
    const p = Array.from({ length: k }, (_, i) => i);
    for (let i = k - 1; i > 0; i--) {
      const j = Math.floor(rng.next() * (i + 1));
      [p[i], p[j]] = [p[j], p[i]];
    }
    return p;
  };
  const px = shuffled(), py = shuffled();
  const cells = [];
  for (let i = 0; i < N * N; i++) {
    const x = i % N, y = (i / N) | 0;
    if (scene.comp[i] && x >= lo && y >= lo && x < hi && y < hi) cells.push(i);
  }
  const used = new Set(), chosen = [];
  for (let s = 0; s < k; s++) {
    const tx = lo + (px[s] + rng.next()) * span, ty = lo + (py[s] + rng.next()) * span;
    let best = -1, bd = Infinity;
    for (const c of cells) {
      if (used.has(c)) continue;
      const d = ((c % N) + 0.5 - tx) ** 2 + (((c / N) | 0) + 0.5 - ty) ** 2;
      if (d < bd) { bd = d; best = c; }
    }
    used.add(best);
    chosen.push(best);
  }
  return chosen;
}

// GP on residuals r_i = s_true(x_i) − s_KB(x_i) (normalised danger units).
// Returns mu = s_KB + posterior residual mean, sigma, the model and the residuals.
export function posterior(scene, sKB, obs) {
  const X = [], y = [];
  for (const o of obs) { X.push((o.cell % N) + 0.5, ((o.cell / N) | 0) + 0.5); y.push(o.s - sKB[o.cell]); }
  const model = fitGP(X, y);
  const { mean, sd } = predictGrid(model, N, scene.free);
  const mu = new Float32Array(N * N);
  for (let i = 0; i < N * N; i++) if (scene.free[i]) mu[i] = sKB[i] + mean[i];
  return { model, mu, sigma: sd, resid: y };
}

// Delta-Stepping route on a danger map.
export function route(scene, mu, A, B) {
  const w = clipWeights(mu, scene.comp);
  const delta = deltaFor(w, scene.comp, N);
  const r = deltaStepping(w, scene.comp, N, A, B, delta);
  return { ...r, w, length: pathLength(r.path, N) };
}

// Corridor, acquisition score, convergence measure and decision for the current route.
export function acquire(scene, mu, sigma, path, simulated) {
  const corridor = corridorMask(path, scene.comp, N);
  const eligible = eligibleMask(scene.comp, simulated, N);
  const { score, best } = acquisitionScore(mu, sigma, corridor, eligible);
  const rel = sigmaRel(mu, sigma, corridor);
  return { corridor, score, next: best, rel, stop: stopRule(rel, simulated.length) };
}

// Share of the route lying more than `tol` m away from the other route.
export function routeShift(path, other, tol = 2) {
  if (!path.length) return 0;
  let off = 0;
  for (const c of path) {
    const x = c % N, y = (c / N) | 0;
    let near = false;
    for (const o of other) if (((o % N) - x) ** 2 + (((o / N) | 0) - y) ** 2 <= tol * tol) { near = true; break; }
    if (!near) off++;
  }
  return off / path.length;
}

export { pathCost };
