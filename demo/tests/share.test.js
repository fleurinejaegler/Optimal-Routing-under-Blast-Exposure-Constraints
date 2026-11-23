import test from 'node:test';
import assert from 'node:assert/strict';
import { parseStart, startFromUrl, writeStart, clearStart } from '../js/share.js';

const N = 10;
const fakeWin = href => {
  const win = { location: { href }, history: { replaceState(_s, _t, url) { win.location.href = String(url); } } };
  return win;
};

test('parseStart: valid "x,y" becomes a cell index, anything else is null', () => {
  assert.equal(parseStart('3,2', N), 2 * N + 3);
  assert.equal(parseStart('0,0', N), 0);
  assert.equal(parseStart('10,0', N), null);     // outside the map
  assert.equal(parseStart('3;2', N), null);
  assert.equal(parseStart('-1,2', N), null);
  assert.equal(parseStart(null, N), null);
});

test('startFromUrl: only open cells of this scene are accepted', () => {
  const scene = { comp: new Uint8Array(N * N).fill(1) };
  scene.comp[5 * N + 4] = 0;                       // a building cell
  assert.equal(startFromUrl(scene, N, fakeWin('https://x/?seed=1&a=3,2')), 2 * N + 3);
  assert.equal(startFromUrl(scene, N, fakeWin('https://x/?seed=1&a=4,5')), undefined);
  assert.equal(startFromUrl(scene, N, fakeWin('https://x/?seed=1')), undefined);
});

test('writeStart then clearStart update the URL and keep the seed', () => {
  const win = fakeWin('https://x/?seed=42');
  writeStart(7 * N + 1, N, win);
  assert.equal(new URL(win.location.href).searchParams.get('a'), '1,7');
  assert.equal(new URL(win.location.href).searchParams.get('seed'), '42');
  clearStart(win);
  assert.equal(new URL(win.location.href).searchParams.get('a'), null);
  assert.equal(new URL(win.location.href).searchParams.get('seed'), '42');
});
