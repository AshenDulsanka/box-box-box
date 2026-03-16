#!/usr/bin/env python3
"""
Fast random search with multiprocessing to find the formula.
"""

import json
import os
import random
import numpy as np
from multiprocessing import Pool, cpu_count

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

def load_test_cases():
    inputs_dir = os.path.join(DATA_DIR, 'inputs')
    expected_dir = os.path.join(DATA_DIR, 'expected_outputs')

    test_cases = []
    files = sorted([f for f in os.listdir(inputs_dir) if f.startswith('test_') and f.endswith('.json')])

    for file in files:
        with open(os.path.join(inputs_dir, file)) as f:
            input_data = json.load(f)
        with open(os.path.join(expected_dir, file)) as f:
            expected = json.load(f)
        test_cases.append({
            'input': input_data,
            'expected': expected['finishing_positions'],
        })

    return test_cases

def simulate_driver(strategy, total_laps, base_lap_time, pit_lane_time, track_temp,
                   offsets, thresholds, rates, tb, tc):
    pit_map = {pit['lap']: pit['to_tire'] for pit in strategy['pit_stops']}
    current_tire = strategy['starting_tire']
    tire_age = 0
    total_time = 0

    for lap in range(1, total_laps + 1):
        tire_age += 1
        off = offsets.get(current_tire, 0)

        laps_over = tire_age - thresholds.get(current_tire, 100)
        if laps_over > 0:
            deg = rates.get(current_tire, 0) * (laps_over * (laps_over + 1)) / 2
        else:
            deg = 0

        temp_factor = 1 + max(0, track_temp - tb) * tc
        lap_time = base_lap_time + off + deg * temp_factor
        total_time += lap_time

        if lap in pit_map:
            total_time += pit_lane_time
            current_tire = pit_map[lap]
            tire_age = 0

    return total_time

def arrays_equal(a, b):
    return all(a[i] == b[i] for i in range(len(a)))

def test_params(params):
    oM, oH = params[0], params[1]
    tS, tM, tH = int(params[2]), int(params[3]), int(params[4])
    rS, rM, rH = params[5], params[6], params[7]
    tb, tc = params[8], params[9]

    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    passed = 0
    for tc_data in test_cases:
        race_config = tc_data['input']['race_config']
        strategies = tc_data['input']['strategies']
        expected = tc_data['expected']

        results = []
        for strat in strategies.values():
            time = simulate_driver(strat, race_config['total_laps'], race_config['base_lap_time'],
                      race_config['pit_lane_time'], race_config['track_temp'],
                      offsets, thresholds, rates, tb, tc)
            results.append((strat['driver_id'], time))

        results.sort(key=lambda x: x[1])
        predicted = [r[0] for r in results]

        if arrays_equal(predicted, expected):
            passed += 1

    return passed, params

def main():
    global test_cases
    print("Loading test cases...")
    test_cases = load_test_cases()
    print(f"Loaded {len(test_cases)} test cases")

    best_score = 0
    best_params = None

    print(f"Running random search (using {cpu_count()} cores)...")
    iteration = 0
    while iteration < 50000:
        # Generate random params
        params = [
            random.uniform(0.1, 5.0),    # oM
            random.uniform(0.2, 8.0),    # oH
            random.randint(1, 50),        # tS
            random.randint(5, 60),        # tM
            random.randint(10, 70),       # tH
            random.uniform(0.0001, 0.2), # rS
            random.uniform(0.0001, 0.1), # rM
            random.uniform(0.0001, 0.05),# rH
            random.uniform(10, 40),       # tb
            random.uniform(0, 0.1),     # tc
        ]

        score, _ = test_params(params)

        if score > best_score:
            best_score = score
            best_params = params
            print(f"Iter {iteration}: New best = {score}/100")

        if score >= 80:
            break

        iteration += 1

    print(f"\nBest: {best_score}/100")
    if best_params:
        print(f"Params: {best_params}")

if __name__ == "__main__":
    main()
