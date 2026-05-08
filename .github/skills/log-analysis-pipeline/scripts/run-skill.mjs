import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pyCandidates = process.platform === 'win32' ? ['py', 'python'] : ['python3', 'python'];
const script = resolve(__dirname, 'run-skill-tests.py');
const root = resolve(__dirname, '..');
let lastError = null;
for (const py of pyCandidates) {
  const result = spawnSync(py, [script, root, 'en-US'], { stdio: 'inherit' });
  if (result.status === 0) process.exit(0);
  lastError = result.error || new Error(`exit ${result.status}`);
}
console.error(lastError?.message || 'Python runtime not found');
process.exit(1);
