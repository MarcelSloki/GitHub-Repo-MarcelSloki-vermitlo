import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const page = await readFile(new URL('../app/page.tsx', import.meta.url), 'utf8');

test('keeps the Stage 2 sequence within the evidenced claim ceiling', () => {
  assert.match(page, /Intended synthetic product path/);
  assert.doesNotMatch(page, /Golden path surfaced by the current backend/);
  assert.match(page, /exposes this sequence as an overview/);
  assert.match(page, /Persisted workflow states/);
  assert.match(page, /official-source ingestion/);
  assert.match(page, /Golden Path proof are not active yet/);
  assert.match(page, /Human approval/);
  assert.match(page, /Synthetic data is used for the current demo path\./);
  assert.match(page, /No real tender portal submission is executed\./);
  assert.match(page, /No real customer payment is charged\./);
});

test('does not add readiness or activation language', () => {
  assert.doesNotMatch(page, /pilot[- ]ready/i);
  assert.doesNotMatch(page, /production[- ]ready/i);
  assert.doesNotMatch(page, /live ingestion (?:is )?(?:active|enabled)/i);
});
