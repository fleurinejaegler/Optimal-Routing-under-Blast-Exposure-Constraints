// Export of a finished run: the route as CSV, and the whole run as JSON.
// Pure functions, no DOM, so they run in the browser and under `node --test`.
//
// Coordinates are in metres at the centre of each 1 m cell (x + 0.5, y + 0.5), as in the map tooltip.

const fixed = (v, d = 6) => (v == null || !Number.isFinite(v) ? '' : v.toFixed(d));

// One row per cell of the route. `w` is the clipped weight array used by the search,
// so `cumulative_danger` at the last row equals the route cost shown in the summary.
export function routeRows(path, mu, sigma, w, N) {
  const rows = [];
  let cum = 0;
  path.forEach((c, k) => {
    let step = 0;
    if (k > 0) {
      const p = path[k - 1];
      const d = Math.hypot((c % N) - (p % N), ((c / N) | 0) - ((p / N) | 0));
      step = w[c] * d;
      cum += step;
    }
    rows.push({
      step: k,
      x: c % N + 0.5,
      y: ((c / N) | 0) + 0.5,
      mu: mu[c],
      sigma: sigma ? sigma[c] : null,
      step_cost: step,
      cumulative_danger: cum,
    });
  });
  return rows;
}

export function routeCSV(rows) {
  const head = 'step,x_m,y_m,mu,sigma,step_cost,cumulative_danger';
  const lines = rows.map(r => [
    r.step, fixed(r.x, 1), fixed(r.y, 1), fixed(r.mu), fixed(r.sigma), fixed(r.step_cost), fixed(r.cumulative_danger),
  ].join(','));
  return [head, ...lines].join('\n') + '\n';
}

// `info` = { seed, charge_kg, start, disposal (cells), sims (cells, in order), rows, routeLength (m),
//             sigmaRel, stop, N, hausdorffM (m to the previous route, or null) }
export function runJSON(info) {
  const { N } = info;
  const at = c => ({ x: c % N + 0.5, y: ((c / N) | 0) + 0.5 });
  const last = info.rows[info.rows.length - 1];
  const out = {
    tool: 'blast-routing demo',
    seed: info.seed,
    charge_kg_tnt: info.charge_kg,
    start: at(info.start),
    disposal: at(info.disposal),
    simulations: info.sims.map((c, i) => ({ order: i + 1, ...at(c) })),
    simulations_used: info.sims.length,
    sigma_cum_rel: info.sigmaRel,
    route_hausdorff_to_previous_m: info.hausdorffM ?? null,
    stop_reason: info.stop,
    route_length_m: info.routeLength,
    cumulative_danger: last ? last.cumulative_danger : 0,
    route: info.rows.map(r => ({ step: r.step, x: r.x, y: r.y, mu: r.mu, sigma: r.sigma, step_cost: r.step_cost, cumulative_danger: r.cumulative_danger })),
  };
  return JSON.stringify(out, null, 2) + '\n';
}
