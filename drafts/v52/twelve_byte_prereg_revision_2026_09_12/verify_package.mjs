// Document/provenance validation only. Does not import or invoke a research runner.
import { readFileSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const directory = dirname(fileURLToPath(import.meta.url));
const namespace = 'drafts/v52/twelve_byte_prereg_revision_2026_09_12/';
const base = '4f2429b257546d6899f3ed48f605cd18210aeae0';
const root = resolve(directory, '../../..');
const requireThat = (condition, message) => { if (!condition) throw new Error(message); };
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const read = name => readFileSync(join(directory, name));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const payload = [
  'PREREG_DRAFT.md', 'PREREG_DRAFT.md.sha256', 'PROPOSED_CONSTANTS.json',
  'README.md', 'SOURCE_EVIDENCE_MAP.md', 'SOURCE_VERIFICATION.json',
  'UNRESOLVED_DECISIONS.md', 'verify_package.mjs', 'verify_sources.mjs',
];
const expectedInventory = [...payload, 'SHA256SUMS', 'SHA256SUMS.sha256'].sort();
requireThat(JSON.stringify(readdirSync(directory).sort()) === JSON.stringify(expectedInventory),
  'Unexpected or missing package file');
function verifyList(name, expectedNames) {
  const listed = [];
  for (const line of read(name).toString('utf8').trim().split('\n')) {
    const match = /^([a-f0-9]{64})  ([A-Za-z0-9_.-]+)$/.exec(line);
    requireThat(match && expectedNames.includes(match[2]), `Unexpected digest entry in ${name}`);
    requireThat(!listed.includes(match[2]), `Duplicate digest entry in ${name}`);
    requireThat(sha(read(match[2])) === match[1], `Digest mismatch: ${match[2]}`);
    listed.push(match[2]);
  }
  requireThat(JSON.stringify(listed.sort()) === JSON.stringify([...expectedNames].sort()),
    `Incomplete digest entries: ${name}`);
}
verifyList('SHA256SUMS.sha256', ['SHA256SUMS']);
verifyList('SHA256SUMS', payload);
verifyList('PREREG_DRAFT.md.sha256', ['PREREG_DRAFT.md']);
for (const name of expectedInventory) {
  const bytes = read(name);
  requireThat(!bytes.includes(13), `CR/CRLF found: ${name}`);
  requireThat(!(bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf), `BOM found: ${name}`);
}
const sourceReplay = execFileSync(process.execPath, [join(directory, 'verify_sources.mjs')],
  { cwd: root, maxBuffer: 8 * 1024 * 1024 });
requireThat(sourceReplay.equals(read('SOURCE_VERIFICATION.json')), 'Source receipt differs from raw-source verification');
const constants = JSON.parse(read('PROPOSED_CONSTANTS.json'));
requireThat(constants.status.includes('NOT HR-APPROVED'), 'Proposal status missing');
requireThat(constants.primary_contrast_proposal === 'SIGN96 - PQ96', 'Primary proposal mismatch');
requireThat(constants.primary_metric_hr_bound === 'Fractional Evidence Recall@100', 'Primary metric mismatch');
requireThat(JSON.stringify(constants.secondary_k_hr_bound) === '[3,10,1000]', 'Secondary metric mismatch');
requireThat(constants.marginal_cap_bytes_hr_bound === 12, 'Byte cap mismatch');
requireThat(constants.bootstrap_replicates_hr_bound === 10000, 'Bootstrap count mismatch');
const panels = Object.entries(constants).filter(([key, value]) => key.includes('seeds_proposed') && Array.isArray(value));
requireThat(panels.length === 7, 'Missing seed panel');
const allSeeds = panels.flatMap(([key, values]) => {
  requireThat(values.length >= 20 && new Set(values).size === values.length && values.every(Number.isSafeInteger),
    `Invalid literal seed panel: ${key}`);
  return values;
});
requireThat(new Set(allSeeds).size === allSeeds.length, 'Unexpected overlap between independent proposed panels');
requireThat(JSON.stringify(constants.haar_rotation_seeds_proposed.slice(0, 5)) ===
  JSON.stringify(constants.historical_simhash_control_seeds_only), 'Historical Haar panel not retained');
requireThat(JSON.stringify(constants.itq_within96_seeds_proposed.slice(0, 5)) ===
  JSON.stringify(constants.historical_itq_control_seeds_only), 'Historical ITQ panel not retained');
const bins = constants.gold_cardinality_strata_proposed;
requireThat(bins[0].min_inclusive === 1 && bins.at(-1).max_inclusive === null, 'Stratum endpoints invalid');
for (let i = 1; i < bins.length; i++) {
  requireThat(bins[i].min_inclusive === bins[i - 1].max_inclusive + 1, 'Strata overlap or gap');
}
for (const key of ['corpus_execution_authorized', 'outcome_access_authorized', 'seal_authorized']) {
  requireThat(constants[key] === false, `Unexpected authority: ${key}`);
}
requireThat(git('merge-base', base, 'HEAD') === base, 'Unexpected base ancestry');
const changes = [git('diff', '--name-only', base, '--'), git('ls-files', '--others', '--exclude-standard')]
  .flatMap(value => value ? value.split('\n') : []);
requireThat(changes.length > 0 && changes.every(path => path.startsWith(namespace)), 'Change outside owned namespace');
requireThat(git('config', '--local', '--get', 'core.autocrlf') === 'false', 'core.autocrlf is not false');
requireThat(git('remote', 'get-url', 'origin') === 'https://github.com/haliltalhaertan/llmzip.git', 'Unexpected true origin');
git('diff', '--check', base, '--');
process.stdout.write(JSON.stringify({
  status: 'PASS: document/provenance verification only; NOT SEALED / NOT AUTHORIZED',
  base_commit: base, payload_files_verified: payload.length,
  total_package_files_verified: expectedInventory.length,
  source_receipt_reproduced: true, seed_panels_checked: panels.length,
  namespace_only_changes: true, recursive_self_hash: false,
  historical_cost_script_replay: 'NOT PERFORMED; PARENT GATE OPEN; SPECIFIC ITEM CAN CLOSE ON VERIFIED REPLAY',
  future_runner_integration: 'OPEN; SEPARATE FROM HISTORICAL REPLAY',
  primary_seeds_strata_disposition: 'PROPOSALS; LEAD DISPOSITION OPEN',
}, null, 2) + '\n');
