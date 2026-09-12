// Read-only verification of pinned published sources. No Python, Faiss, corpus,
// gold rows, retrieval, runtime replay, environment secrets, or output-file writes.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const BASE = '4f2429b257546d6899f3ed48f605cd18210aeae0';
const HR = '89d3169adb65a9a2ab7f289997d7c49eb8ccf25c';
const OLD = 'd2cfbaacdfc52af2ac2077ffa1d87b719a7d0779';
const EVIDENCE = '8217704700d793862a6c43130b88236da551f010';
const git = (...args) => execFileSync('git', args, { maxBuffer: 8 * 1024 * 1024 });
const raw = (commit, path) => git('cat-file', 'blob', `${commit}:${path}`);
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const requireThat = (condition, message) => { if (!condition) throw new Error(message); };
const sources = [];
const commits = [BASE, HR, OLD, EVIDENCE].map(commit => {
  const bytes = git('cat-file', 'commit', commit);
  const calculated = createHash('sha1').update(Buffer.from(`commit ${bytes.length}\0`))
    .update(bytes).digest('hex');
  requireThat(calculated === commit, `Raw commit object mismatch: ${commit}`);
  return { commit, raw_commit_sha256: sha256(bytes), raw_git_object_sha1_verified: true };
});
function record(id, commit, path, expected = null) {
  const bytes = raw(commit, path);
  const blob = git('rev-parse', `${commit}:${path}`).toString().trim();
  const calculatedBlob = createHash('sha1')
    .update(Buffer.from(`blob ${bytes.length}\0`)).update(bytes).digest('hex');
  requireThat(blob === calculatedBlob, `Git blob mismatch: ${path}`);
  const hash = sha256(bytes);
  if (expected !== null) requireThat(hash === expected, `SHA256 mismatch: ${path}`);
  sources.push({ id, commit, path, byte_length: bytes.length, git_blob_sha1: blob,
    sha256: hash, expected_sha256: expected,
    verification: expected ? 'MATCHES_PUBLISHED_DIGEST_AND_RAW_GIT_BLOB' : 'RAW_GIT_BLOB_VERIFIED_DIGEST_RECORDED' });
  return bytes;
}
function sidecarPair(id, commit, path) {
  const sidecar = record(`${id}_SIDECAR`, commit, `${path}.sha256`);
  const expected = sidecar.toString('utf8').trim().split(/\s+/)[0];
  requireThat(/^[a-f0-9]{64}$/.test(expected), `Malformed sidecar: ${path}`);
  return record(id, commit, path, expected);
}
sidecarPair('HR', HR, 'docs/v52/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md');
sidecarPair('OLD', OLD, 'docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md');
const hashList = record('EVIDENCE_HASHES', EVIDENCE, 'evidence/twelve_byte_cost_2026_09_11/HASHES.txt');
const allowed = new Map([
  ['EVIDENCE.json', 'COST'], ['measure_twelve_byte_cost.py', 'COST_SCRIPT'],
  ['README.md', 'COST_README'], ['OPEN_ITEMS_CLOSED.md', 'CLOSURES'],
]);
for (const line of hashList.toString('utf8').trim().split(/\r?\n/)) {
  const match = /^([a-f0-9]{64})  (evidence\/twelve_byte_cost_2026_09_11\/([^/]+))$/.exec(line);
  requireThat(match && allowed.has(match[3]), `Unexpected source in hash list: ${line}`);
  record(allowed.get(match[3]), EVIDENCE, match[2], match[1]);
  allowed.delete(match[3]);
}
requireThat(allowed.size === 0, 'Incomplete evidence hash list');
const report = record('SIMHASH_AUDIT', BASE, 'audit_v52_t4c3/AUDIT_REPORT.md',
  '8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238');
sidecarPair('CLAIM_PROMPT', HR, 'prompts/V52_TWELVE_BYTE_BUDGET_MUSE_AUDIT_TASK_2026-09-11.md');
record('LME_PROTOCOL', BASE, 'docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md');

// Only arithmetic on five already-published scalar percentages, in exact integers.
const seeds = [43001, 43002, 43003, 43004, 43005];
const percentages = ['36.1395390', '39.1393617', '37.9320922', '38.0195035', '40.1278369'];
for (let i = 0; i < seeds.length; i++) {
  requireThat(report.toString('utf8').includes(`- ${seeds[i]}: ${percentages[i]}%`),
    `Published SIMHASH scalar missing for ${seeds[i]}`);
}
const total = percentages.reduce((sum, value) => sum + BigInt(value.replace('.', '')), 0n);
const denominator = 5n * 100n * 10_000_000n;
const scaled = total * 100_000_000n;
const quotient = scaled / denominator;
const remainder = scaled % denominator;
const increment = remainder * 2n > denominator ||
  (remainder * 2n === denominator && quotient % 2n === 1n);
const roundedInteger = quotient + (increment ? 1n : 0n);
const control = `0.${roundedInteger.toString().padStart(8, '0')}`;
requireThat(control === '0.38271667', 'SIMHASH published-scalar derivation mismatch');
process.stdout.write(JSON.stringify({
  status: 'NOT SEALED / NOT AUTHORIZED', base_commit: BASE,
  verification_scope: 'Raw Git object and published digest checks; five published scalar provenance arithmetic only. No runtime replay or retrieval recomputation.',
  commits, sources,
  simhash_provenance: { seeds, percentages, exact_fractional_mean: '0.3827166666',
    rounding_rule: 'Decimal round to nearest at eight fractional places; HALF_EVEN (no tie here).',
    rounded_control: control, tolerance: '1e-6', historical_panel_only: true },
}, null, 2) + '\n');
