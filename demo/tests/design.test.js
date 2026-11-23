// Initial design: Latin hypercube of N_INIT points on the main component, away from the border.
import test from 'node:test';
import assert from 'node:assert/strict';
import { generateScene, N } from '../js/scene.js';
import { initialDesign } from '../js/pipeline.js';
import { N_INIT } from '../js/acquisition.js';

test('initial design: N_INIT distinct free cells, inside the border margin', () => {
  for (const seed of [1, 2, 42]) {
    const sc = generateScene(seed);
    const d = initialDesign(sc, seed);
    assert.equal(d.length, N_INIT);
    assert.equal(new Set(d).size, N_INIT);
    for (const c of d) {
      const x = c % N, y = (c / N) | 0;
      assert.ok(sc.comp[c], 'cell not in the main component');
      assert.ok(x >= 3 && y >= 3 && x < N - 3 && y < N - 3, 'cell too close to the border');
    }
  }
});

test('initial design is deterministic for a seed', () => {
  const sc = generateScene(42);
  assert.deepEqual(initialDesign(sc, 42), initialDesign(sc, 42));
});
