/**
 * Lap time calculation engine.
 * Implements the discovered formula for computing a single lap's time.
 */

'use strict';

const {
  COMPOUND_OFFSET,
  DEGRADATION_THRESHOLD,
  DEGRADATION_RATE,
  TEMP_BASELINE,
  TEMP_COEFFICIENT,
} = require('./constants');

/**
 * Calculate the time for a single lap.
 *
 * @param {number} baseLapTime  - Track's base lap time in seconds
 * @param {string} compound     - Tire compound: 'SOFT' | 'MEDIUM' | 'HARD'
 * @param {number} tireAge      - Number of laps completed on current tires (0 = brand new)
 * @param {number} trackTemp    - Track temperature in °C
 * @returns {number} Lap time in seconds
 */
function calculateLapTime(baseLapTime, compound, tireAge, trackTemp) {
  const compoundOffset = COMPOUND_OFFSET[compound];
  const degradation = calculateDegradation(compound, tireAge, trackTemp);
  return baseLapTime + compoundOffset + degradation;
}

/**
 * Calculate tire degradation penalty for a lap.
 *
 * Degradation is cumulative: after threshold, each lap adds more degradation
 * degradation = rate * sum(ages from threshold+1 to current_age)
 *             = rate * lapsOver * (lapsOver + 1) / 2
 *
 * @param {string} compound  - Tire compound
 * @param {number} tireAge   - Current tire age in laps (1 = first lap on these tires)
 * @param {number} trackTemp - Track temperature in °C
 * @returns {number} Degradation penalty in seconds
 */
function calculateDegradation(compound, tireAge, trackTemp) {
  const threshold = DEGRADATION_THRESHOLD[compound];
  const rate = DEGRADATION_RATE[compound];

  const lapsOver = tireAge - threshold;
  if (lapsOver <= 0) return 0;

  // Cumulative degradation: sum of ages from threshold+1 to tireAge
  // Formula: rate * n * (n + 1) / 2 where n = lapsOver
  const cumulativeSum = lapsOver * (lapsOver + 1) / 2;
  const baseDeg = rate * cumulativeSum;

  // Temperature multiplier: temperature above baseline increases degradation
  const tempEffect = 1 + Math.max(0, trackTemp - TEMP_BASELINE) * TEMP_COEFFICIENT;

  return baseDeg * tempEffect;
}

module.exports = { calculateLapTime, calculateDegradation };
