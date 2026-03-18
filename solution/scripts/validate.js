/**
 * Validation script — runs simulator against all 100 test cases.
 *
 * Run from repo root:
 *   node solution/scripts/validate.js
 *
 * Also validates against historical races for formula verification.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { simulateRace } = require('../src/simulator');

const INPUTS_DIR = path.join(__dirname, '..', '..', 'data', 'test_cases', 'inputs');
const EXPECTED_DIR = path.join(__dirname, '..', '..', 'data', 'test_cases', 'expected_outputs');
const HISTORICAL_DIR = path.join(__dirname, '..', '..', 'data', 'historical_races');

function arraysEqual(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

/**
 * Run all 100 test cases and report results.
 */
function runTestCases() {
  console.log('\n====================================');
  console.log(' Box Box Box — Test Case Validation');
  console.log('====================================\n');

  const files = fs.readdirSync(INPUTS_DIR)
    .filter(f => f.startsWith('test_') && f.endsWith('.json'))
    .sort();

  let passed = 0;
  let failed = 0;
  const failures = [];

  for (const file of files) {
    const testId = file.replace('.json', '').replace('test_', 'TEST_').toUpperCase();
    const input = JSON.parse(fs.readFileSync(path.join(INPUTS_DIR, file), 'utf-8'));
    const expectedPath = path.join(EXPECTED_DIR, file);

    if (!fs.existsSync(expectedPath)) {
      console.log(`  ? ${testId} — no expected output file`);
      continue;
    }

    const expected = JSON.parse(fs.readFileSync(expectedPath, 'utf-8'));
    const predicted = simulateRace(input.race_config, input.strategies);

    if (arraysEqual(predicted, expected.finishing_positions)) {
      passed++;
      console.log(`  ✓ ${testId}`);
    } else {
      failed++;
      console.log(`  ✗ ${testId}`);
      failures.push({ testId, input, predicted, expected: expected.finishing_positions });
    }
  }

  const total = passed + failed;
  const rate = total > 0 ? (passed / total * 100).toFixed(1) : '0.0';

  console.log('\n====================================');
  console.log(` Results`);
  console.log('====================================');
  console.log(` Total:  ${total}`);
  console.log(` Passed: ${passed}`);
  console.log(` Failed: ${failed}`);
  console.log(` Rate:   ${rate}%`);
  console.log('====================================\n');

  if (failures.length > 0) {
    console.log('Failure details:\n');
    for (const f of failures.slice(0, 10)) {
      const cfg = f.input.race_config;
      console.log(`  ${f.testId} — ${cfg.track}, ${cfg.total_laps} laps, ${cfg.track_temp}°C, pit=${cfg.pit_lane_time}s`);
      console.log(`    Expected:  ${f.expected.slice(0, 8).join(', ')}...`);
      console.log(`    Predicted: ${f.predicted.slice(0, 8).join(', ')}...`);

      // Show differing positions
      const diffs = [];
      for (let i = 0; i < f.expected.length; i++) {
        if (f.expected[i] !== f.predicted[i]) {
          diffs.push(`pos${i+1}: expected ${f.expected[i]}, got ${f.predicted[i]}`);
        }
      }
      console.log(`    Diffs (${diffs.length}): ${diffs.slice(0, 4).join(' | ')}`);
      console.log('');
    }
  }

  return { passed, failed, total };
}

/**
 * Run validation against a sample of historical races.
 */
function validateHistorical(numBatches = 1) {
  console.log(`\n=== Historical Race Validation (${numBatches} batch(es)) ===\n`);

  const files = fs.readdirSync(HISTORICAL_DIR)
    .filter(f => f.endsWith('.json'))
    .sort()
    .slice(0, numBatches);

  let totalPassed = 0;
  let totalFailed = 0;

  for (const file of files) {
    const races = JSON.parse(fs.readFileSync(path.join(HISTORICAL_DIR, file), 'utf-8'));
    let passed = 0;
    let failed = 0;

    for (const race of races) {
      const predicted = simulateRace(race.race_config, race.strategies);
      if (arraysEqual(predicted, race.finishing_positions)) {
        passed++;
      } else {
        failed++;
      }
    }

    const rate = ((passed / races.length) * 100).toFixed(1);
    console.log(`  ${file}: ${passed}/${races.length} (${rate}%)`);
    totalPassed += passed;
    totalFailed += failed;
  }

  const total = totalPassed + totalFailed;
  const rate = total > 0 ? (totalPassed / total * 100).toFixed(1) : '0.0';
  console.log(`\n  Total: ${totalPassed}/${total} (${rate}%)\n`);
}

// Run
const args = process.argv.slice(2);
const mode = args[0] || 'test';

if (mode === 'historical') {
  const batches = parseInt(args[1] || '1', 10);
  validateHistorical(batches);
} else if (mode === 'all') {
  runTestCases();
  validateHistorical(3);
} else {
  runTestCases();
}
