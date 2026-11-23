import test from 'node:test';
import assert from 'node:assert/strict';
import { routeRows, routeCSV, runJSON } from '../js/export.js';

const N = 4;
// a straight path along the first row, then one diagonal step
const path = [0, 1, 2, 7];                       // cells (0,0) (1,0) (2,0) (3,1)
const mu = Float64Array.from({ length: N * N }, (_, i) => i / 10);
const sigma = Float64Array.from({ length: N * N }, () => 0.05);
const w = Float64Array.from(mu, v => Math.max(v, 1e-3));

test('routeRows: cell centres, step costs and cumulative danger', () => {
  const rows = routeRows(path, mu, sigma, w, N);
  assert.equal(rows.length, 4);
  assert.deepEqual([rows[0].x, rows[0].y], [0.5, 0.5]);
  assert.deepEqual([rows[3].x, rows[3].y], [3.5, 1.5]);
  assert.equal(rows[0].step_cost, 0);
  // step 2 enters cell 1 along an axis: cost = w[1] * 1
  assert.ok(Math.abs(rows[1].step_cost - w[1]) < 1e-12);
  // last step is diagonal (sqrt 2 long) from (2,0) to (3,1), cost = w[7] * sqrt(2)
  assert.ok(Math.abs(rows[3].step_cost - w[7] * Math.SQRT2) < 1e-12);
  const total = rows.reduce((s, r) => s + r.step_cost, 0);
  assert.ok(Math.abs(rows[3].cumulative_danger - total) < 1e-12);
});

test('routeCSV: header, one line per row, empty field for missing sigma', () => {
  const rows = routeRows(path, mu, null, w, N);
  const lines = routeCSV(rows).trim().split('\n');
  assert.equal(lines[0], 'step,x_m,y_m,mu,sigma,step_cost,cumulative_danger');
  assert.equal(lines.length, path.length + 1);
  assert.equal(lines[1].split(',')[4], '');   // sigma absent
});

test('runJSON: round-trips the main fields', () => {
  const rows = routeRows(path, mu, sigma, w, N);
  const doc = JSON.parse(runJSON({
    seed: 42, charge_kg: 40, start: 0, disposal: 7, sims: [5, 9], rows,
    routeLength: 3.41, sigmaRel: 0.04, stop: 'converged', N,
  }));
  assert.equal(doc.seed, 42);
  assert.deepEqual(doc.start, { x: 0.5, y: 0.5 });
  assert.deepEqual(doc.disposal, { x: 3.5, y: 1.5 });
  assert.equal(doc.simulations_used, 2);
  assert.deepEqual(doc.simulations[1], { order: 2, x: 1.5, y: 2.5 });
  assert.equal(doc.stop_reason, 'converged');
  assert.equal(doc.route.length, path.length);
  assert.ok(Math.abs(doc.cumulative_danger - rows[3].cumulative_danger) < 1e-12);
});
