#!/usr/bin/env python3
"""
Box Box Box - F1 Race Simulator
"""

import json
import sys

# ============================================================================
# PARAMETERS
# ============================================================================

# Fixed cliffs (do not tune)
CLIFF = {
    'SOFT': 10,
    'MEDIUM': 20,
    'HARD': 30,
}

# Optimized parameters from auto-tuner
PARAMS = {
    'SOFT': {
        'offset': 2.5356,
        'deg': 0.4604,
    },
    'MEDIUM': {
        'offset': 3.9781,
        'deg': 0.2307,
    },
    'HARD': {
        'offset': 5.1232,
        'deg': 0.1107,
    },
    'temp_coef': 0.1327,
    'fuel_burn': -0.002875,
    'warmup_penalty': 0.8093,
}


def calculate_lap_time(lap_num, tire_age, compound, track_temp):
    """
    Calculate lap time using the formula:
    lap_time = base_lap_time
             + tire_offset[compound]
             + deg[compound] * (1 + track_temp * temp_coef) * max(0, tire_age - cliff[compound])
             + fuel_burn * (lap_num - 1)
             + warmup_penalty (only on tire_age == 1, first lap of each stint)
    """
    # Note: base_lap_time is passed in, not from PARAMS
    offset = PARAMS[compound]['offset']
    deg = PARAMS[compound]['deg']
    cliff = CLIFF[compound]
    temp_coef = PARAMS['temp_coef']
    fuel_burn = PARAMS['fuel_burn']
    warmup_penalty = PARAMS['warmup_penalty']

    # Base time + tire offset
    lap_time = base + offset

    # Degradation with temperature scaling
    deg_factor = deg * (1 + track_temp * temp_coef)
    deg_penalty = deg_factor * max(0, tire_age - cliff)
    lap_time += deg_penalty

    # Fuel burn (car gets lighter -> faster)
    lap_time += fuel_burn * (lap_num - 1)

    # Warmup penalty (only on first lap of each stint)
    if tire_age == 1:
        lap_time += warmup_penalty

    return lap_time


def simulate_race(race_config, strategies):
    """
    Simulate a race and return finishing order.
    """
    base_lap_time = race_config['base_lap_time']
    track_temp = race_config['track_temp']
    total_laps = race_config['total_laps']
    pit_lane_time = race_config['pit_lane_time']

    # Calculate total time for each driver
    driver_times = []

    for strat in strategies.values():
        driver_id = strat['driver_id']
        starting_tire = strat['starting_tire']
        pit_stops = strat['pit_stops']

        # Build pit stop map
        pit_map = {p['lap']: p['to_tire'] for p in pit_stops}

        # Simulate race
        total_time = 0
        current_tire = starting_tire
        tire_age = 0

        for lap in range(1, total_laps + 1):
            # Increment tire age at start of lap
            tire_age += 1

            # Calculate lap time using our formula
            lap_time = base_lap_time
            lap_time += PARAMS[current_tire]['offset']
            deg_factor = PARAMS[current_tire]['deg'] * (1 + track_temp * PARAMS['temp_coef'])
            deg_penalty = deg_factor * max(0, tire_age - CLIFF[current_tire])
            lap_time += deg_penalty
            lap_time += PARAMS['fuel_burn'] * (lap - 1)

            # Warmup penalty on first lap of stint
            if tire_age == 1:
                lap_time += PARAMS['warmup_penalty']

            total_time += lap_time

            # Pit stop at end of lap
            if lap in pit_map:
                total_time += pit_lane_time
                current_tire = pit_map[lap]
                tire_age = 0

        driver_times.append((driver_id, total_time))

    # Sort by total time (ascending)
    driver_times.sort(key=lambda x: x[1])

    # Return finishing positions
    return [driver_id for driver_id, _ in driver_times]


def main():
    # Read input from STDIN
    input_data = json.load(sys.stdin)

    # Simulate race
    finishing_positions = simulate_race(
        input_data['race_config'],
        input_data['strategies']
    )

    # Output result
    output = {
        'race_id': input_data['race_id'],
        'finishing_positions': finishing_positions,
    }

    print(json.dumps(output))


if __name__ == '__main__':
    main()
