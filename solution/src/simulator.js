/**
 * Core race simulation engine.
 * Simulates each driver's race independently (no car-to-car interaction).
 * Winner is determined by the shortest total race time.
 */

'use strict';

const { calculateLapTime } = require('./laptime');

/**
 * Simulate a full race and return drivers sorted by finishing position.
 *
 * @param {object} raceConfig - Race configuration object
 * @param {object} strategies - Strategies for pos1..pos20
 * @returns {string[]} Array of driver IDs in finishing order (1st to 20th)
 */
function simulateRace(raceConfig, strategies) {
  const { total_laps, base_lap_time, pit_lane_time, track_temp } = raceConfig;

  const results = [];

  for (const posKey of Object.keys(strategies)) {
    const strategy = strategies[posKey];
    const totalTime = simulateDriver(strategy, total_laps, base_lap_time, pit_lane_time, track_temp);
    results.push({ driver_id: strategy.driver_id, total_time: totalTime });
  }

  // Sort by ascending total time (fastest first)
  results.sort((a, b) => a.total_time - b.total_time);

  return results.map(r => r.driver_id);
}

/**
 * Simulate a single driver's race and return their total time.
 *
 * Pit stop mechanic:
 * - Pit on lap N means: lap N is completed on old tires, then pit_lane_time added,
 *   and lap N+1 starts on new tires with tireAge = 0.
 *
 * @param {object} strategy       - Driver strategy with pit stops and starting tire
 * @param {number} totalLaps      - Number of laps in the race
 * @param {number} baseLapTime    - Track's base lap time
 * @param {number} pitLaneTime    - Time penalty per pit stop
 * @param {number} trackTemp      - Track temperature in °C
 * @returns {number} Total race time in seconds
 */
function simulateDriver(strategy, totalLaps, baseLapTime, pitLaneTime, trackTemp) {
  const { starting_tire, pit_stops } = strategy;

  // Build a map of lap number → new tire compound for quick lookup
  const pitMap = {};
  for (const pit of pit_stops) {
    pitMap[pit.lap] = pit.to_tire;
  }

  let currentTire = starting_tire;
  let tireAge = 0;
  let totalTime = 0;

  for (let lap = 1; lap <= totalLaps; lap++) {
    // According to regulations: tire age increments BEFORE calculating lap time
    // First lap on fresh tires is driven at age 1
    tireAge++;

    // Calculate lap time on current tires
    const lapTime = calculateLapTime(baseLapTime, currentTire, tireAge, trackTemp);
    totalTime += lapTime;

    // If pit stop occurs at end of this lap
    if (pitMap[lap] !== undefined) {
      totalTime += pitLaneTime;
      currentTire = pitMap[lap];
      tireAge = 0;
    }
  }

  return totalTime;
}

module.exports = { simulateRace, simulateDriver };
