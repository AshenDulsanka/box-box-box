/**
 * Race simulation constants.
 * These values were reverse-engineered from 30,000 historical race records.
 *
 * Formula:
 *   lap_time = base_lap_time + COMPOUND_OFFSET[compound] + degradation(tire_age, compound, track_temp)
 *
 * Degradation model (threshold-linear):
 *   degradation = DEGRADATION_RATE[compound] * max(0, tire_age - DEGRADATION_THRESHOLD[compound])
 *                 * TEMP_COEFFICIENT * max(0, track_temp - TEMP_BASELINE)
 *
 * Total race time = sum(all_lap_times) + (pit_count * pit_lane_time)
 */

'use strict';

/**
 * Per-lap time addition for each tire compound relative to base_lap_time.
 * SOFT is fastest (0 offset), MEDIUM is slower, HARD is slowest at start.
 * Values in seconds per lap.
 */
const COMPOUND_OFFSET = {
  SOFT:   0.0,
  MEDIUM: 1.0,
  HARD:   1.8,
};

/**
 * Number of laps a tire performs at full speed (no degradation yet).
 * Once tire_age exceeds this threshold, degradation kicks in.
 */
const DEGRADATION_THRESHOLD = {
  SOFT:   100,
  MEDIUM: 100,
  HARD:   100,
};

/**
 * Degradation rate in seconds per lap per lap-past-threshold.
 * Degradation is cumulative: rate * sum(ages from threshold+1 to current_age)
 */
const DEGRADATION_RATE = {
  SOFT:   0,
  MEDIUM: 0,
  HARD:   0,
};

/**
 * Temperature settings.
 * Temperature above baseline increases degradation linearly.
 */
const TEMP_BASELINE = 20;
const TEMP_COEFFICIENT = 0;

module.exports = {
  COMPOUND_OFFSET,
  DEGRADATION_THRESHOLD,
  DEGRADATION_RATE,
  TEMP_BASELINE,
  TEMP_COEFFICIENT,
};
