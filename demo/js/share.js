// Shareable start point: the URL carries the seed (?seed=) and the chosen start (?a=x,y),
// so a link reopens the same scene with the same start and skips the picking step.
// Pure functions: `win` is any object with `location.href` and `history.replaceState`.

// "x,y" in whole metres (cell indices) -> cell index, or null if malformed or outside the map.
export function parseStart(value, N) {
  const m = /^(\d+),(\d+)$/.exec(value ?? '');
  if (!m) return null;
  const x = Number(m[1]), y = Number(m[2]);
  if (x >= N || y >= N) return null;
  return y * N + x;
}

// The start from the URL, if it is a valid open cell of this scene; otherwise undefined
// (the visitor then picks A as usual).
export function startFromUrl(scene, N, win = globalThis.window) {
  const c = parseStart(new URL(win.location.href).searchParams.get('a'), N);
  if (c === null || !scene.comp[c]) return undefined;
  return c;
}

export function writeStart(cell, N, win = globalThis.window) {
  const url = new URL(win.location.href);
  url.searchParams.set('a', `${cell % N},${(cell / N) | 0}`);
  try { win.history.replaceState(null, '', url); } catch { /* sandboxed iframe: ignore */ }
}

export function clearStart(win = globalThis.window) {
  const url = new URL(win.location.href);
  url.searchParams.delete('a');
  try { win.history.replaceState(null, '', url); } catch { /* sandboxed iframe: ignore */ }
}
