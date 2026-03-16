/**
 * Box Box Box - F1 Race Simulator
 * Entry point: reads race JSON from stdin, outputs finishing positions to stdout.
 *
 * Usage: cat test_case.json | node solution/race_simulator.js
 */

'use strict';

const fs = require('fs');
const { simulateRace } = require('./src/simulator');

function main() {
  let input;
  try {
    input = fs.readFileSync(0, 'utf-8');
  } catch (err) {
    process.stderr.write(`Error reading stdin: ${err.message}\n`);
    process.exit(1);
  }

  let testCase;
  try {
    testCase = JSON.parse(input);
  } catch (err) {
    process.stderr.write(`Error parsing JSON input: ${err.message}\n`);
    process.exit(1);
  }

  if (!testCase.race_id || !testCase.race_config || !testCase.strategies) {
    process.stderr.write('Invalid input: missing required fields (race_id, race_config, strategies)\n');
    process.exit(1);
  }

  const finishingPositions = simulateRace(testCase.race_config, testCase.strategies);

  const output = {
    race_id: testCase.race_id,
    finishing_positions: finishingPositions,
  };

  process.stdout.write(JSON.stringify(output) + '\n');
}

main();
