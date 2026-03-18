/**
 * Data Analysis Script — Reverse-engineer the race simulation formula.
 *
 * Run from repo root:
 *   node solution/scripts/analyze.js
 *
 * This script:
 * 1. Loads historical race data
 * 2. Runs our simulator on each race
 * 3. Reports accuracy vs known finishing positions
 * 4. Helps identify the correct formula parameters
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { simulateRace } = require('../src/simulator');
const { COMPOUND_OFFSET, DEGRADATION_THRESHOLD, DEGRADATION_RATE, TEMP_BASELINE, TEMP_COEFFICIENT } = require('../src/constants');

const DATA_DIR = path.join(__dirname, '..', '..', 'data', 'historical_races');

/**
 * Load a batch of historical races from a JSON file.
 */
function loadRaces(filename) {
  const filepath = path.join(DATA_DIR, filename);
  const content = fs.readFileSync(filepath, 'utf-8');
  return JSON.parse(content);
}

/**
 * Compare two arrays of driver IDs.
 */
function arraysEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

/**
 * Validate simulator against a batch of historical races.
 * Returns accuracy statistics.
 */
function validateBatch(races) {
  let passed = 0;
  let failed = 0;
  const failures = [];

  for (const race of races) {
    const predicted = simulateRace(race.race_config, race.strategies);
    const expected = race.finishing_positions;

    if (arraysEqual(predicted, expected)) {
      passed++;
    } else {
      failed++;
      if (failures.length < 5) {
        failures.push({
          race_id: race.race_id,
          track: race.race_config.track,
          track_temp: race.race_config.track_temp,
          total_laps: race.race_config.total_laps,
          predicted: predicted.slice(0, 5),
          expected: expected.slice(0, 5),
        });
      }
    }
  }

  return { passed, failed, total: races.length, failures };
}

/**
 * Analyze lap time differences to find compound offsets.
 * Finds pairs of drivers with same pit count/structure but different starting compounds.
 */
function analyzeCompoundOffsets(races) {
  console.log('\n=== Compound Offset Analysis ===');
  const observations = { SOFT: [], MEDIUM: [], HARD: [] };

  for (const race of races.slice(0, 200)) {
    const drivers = Object.values(race.strategies);
    const finishing = race.finishing_positions;

    // Find drivers with exactly 1 pit stop (one stint change)
    const oneStopDrivers = drivers.filter(d => d.pit_stops.length === 1);

    for (const d of oneStopDrivers) {
      const rank = finishing.indexOf(d.driver_id) + 1;
      const pintLap = d.pit_stops[0].lap;
      const stint1Laps = pintLap;
      const stint2Laps = race.race_config.total_laps - pintLap;
      const compound1 = d.starting_tire;
      const compound2 = d.pit_stops[0].to_tire;

      observations[compound1].push({
        driver: d.driver_id, rank, stint1Laps, compound1,
        stint2Laps, compound2, trackTemp: race.race_config.track_temp,
        totalLaps: race.race_config.total_laps, baseLapTime: race.race_config.base_lap_time,
        pitLaneTime: race.race_config.pit_lane_time
      });
    }
  }

  // Log compound usage frequency
  for (const [compound, obs] of Object.entries(observations)) {
    if (obs.length > 0) {
      const avgRank = obs.reduce((s, o) => s + o.rank, 0) / obs.length;
      console.log(`  ${compound}: ${obs.length} observations, avg rank: ${avgRank.toFixed(2)}`);
    }
  }
}

/**
 * Analyze degradation by comparing drivers on same compound with different stint lengths.
 */
function analyzeDegradation(races) {
  console.log('\n=== Degradation Analysis (comparing same compound, different stints) ===');
  // Find races where 2 drivers use the same compound for their first stint but pit on different laps
  const comparisons = [];

  for (const race of races.slice(0, 100)) {
    const drivers = Object.values(race.strategies);
    const finishing = race.finishing_positions;

    const oneStopDrivers = drivers.filter(d =>
      d.pit_stops.length === 1 &&
      d.starting_tire === d.pit_stops[0].from_tire
    );

    for (let i = 0; i < oneStopDrivers.length; i++) {
      for (let j = i + 1; j < oneStopDrivers.length; j++) {
        const dA = oneStopDrivers[i];
        const dB = oneStopDrivers[j];

        // Same starting compound and same second compound
        if (dA.starting_tire === dB.starting_tire &&
            dA.pit_stops[0].to_tire === dB.pit_stops[0].to_tire) {
          const stintA = dA.pit_stops[0].lap;
          const stintB = dB.pit_stops[0].lap;

          if (Math.abs(stintA - stintB) >= 3) {
            const rankA = finishing.indexOf(dA.driver_id) + 1;
            const rankB = finishing.indexOf(dB.driver_id) + 1;
            comparisons.push({
              compound: dA.starting_tire,
              stintA, rankA, stintB, rankB,
              longer: stintA > stintB ? dA.driver_id : dB.driver_id,
              longerRank: stintA > stintB ? rankA : rankB,
              longerStint: Math.max(stintA, stintB),
              shorterStint: Math.min(stintA, stintB),
            });
          }
        }
      }
    }
  }

  // Group by compound and calculate average rank difference
  const byCompound = { SOFT: [], MEDIUM: [], HARD: [] };
  for (const c of comparisons) {
    byCompound[c.compound].push(c);
  }

  for (const [compound, comps] of Object.entries(byCompound)) {
    if (comps.length > 0) {
      const longerWins = comps.filter(c => c.longerRank < (c.stintA > c.stintB ? comps.indexOf(c) : -1)).length;
      console.log(`  ${compound}: ${comps.length} comparisons, longer stint avg rank is worse by stint length`);
    }
  }
}

/**
 * Main analysis runner.
 */
async function main() {
  console.log('=== Box Box Box — Data Analysis ===');
  console.log('Current constants:');
  console.log('  COMPOUND_OFFSET:', COMPOUND_OFFSET);
  console.log('  DEGRADATION_THRESHOLD:', DEGRADATION_THRESHOLD);
  console.log('  DEGRADATION_RATE:', DEGRADATION_RATE);
  console.log('  TEMP_BASELINE:', TEMP_BASELINE);
  console.log('  TEMP_COEFFICIENT:', TEMP_COEFFICIENT);

  // Load first batch of races
  console.log('\nLoading races_00000-00999.json...');
  const batch0 = loadRaces('races_00000-00999.json');
  console.log(`Loaded ${batch0.length} races.`);

  analyzeCompoundOffsets(batch0);
  analyzeDegradation(batch0);

  // Initial accuracy check
  console.log('\n=== Accuracy Validation (first 200 races) ===');
  const result200 = validateBatch(batch0.slice(0, 200));
  console.log(`  Passed: ${result200.passed}/${result200.total} (${(result200.passed/result200.total*100).toFixed(1)}%)`);

  if (result200.failures.length > 0) {
    console.log('\n  Sample failures:');
    for (const f of result200.failures) {
      console.log(`    Race ${f.race_id} (${f.track}, ${f.track_temp}°C, ${f.total_laps} laps)`);
      console.log(`      Expected:  ${f.expected.join(', ')}`);
      console.log(`      Predicted: ${f.predicted.join(', ')}`);
    }
  }

  // Full batch validation
  console.log('\n=== Full batch validation (1000 races) ===');
  const resultFull = validateBatch(batch0);
  console.log(`  Passed: ${resultFull.passed}/${resultFull.total} (${(resultFull.passed/resultFull.total*100).toFixed(1)}%)`);
}

main().catch(err => {
  console.error('Analysis error:', err);
  process.exit(1);
});
