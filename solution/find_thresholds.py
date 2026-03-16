#!/usr/bin/env python3
"""
Find degradation parameters that work for long races.
"""

import json
import os
import random

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
            'laps': input_data['race_config']['total_laps']
        })

    return test_cases

def simulate_driver(strategy, race_config, offsets, thresholds, rates):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    current_tire = strategy['starting_tire']
    tire_age = 0
    total_time = 0

    for lap in range(1, race_config['total_laps'] + 1):
        tire_age += 1

        lap_time = race_config['base_lap_time'] + offsets.get(current_tire, 0)

        # Cumulative degradation
        laps_over = tire_age - thresholds.get(current_tire, 100)
        if laps_over > 0:
            deg = rates.get(current_tire, 0) * (laps_over * (laps_over + 1)) / 2
            lap_time += deg

        total_time += lap_time

        if lap in pit_map:
            total_time += race_config['pit_lane_time']
            current_tire = pit_map[lap]
            tire_age = 0

    return total_time

def test_params(params, test_cases):
    oM, oH = params[0], params[1]
    tS, tM, tH = int(params[2]), int(params[3]), int(params[4])
    rS, rM, rH = params[5], params[6], params[7]

    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    short_pass, long_pass = 0, 0

    for tc in test_cases:
        is_long = tc['laps'] >= 40
        expected = tc['expected']

        results = []
        for strat in tc['input']['strategies'].values():
            time = simulate_driver(strat, tc['input']['race_config'], offsets, thresholds, rates)
            results.append((strat['driver_id'], time))

        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]

        if pred == expected:
            if is_long:
                long_pass += 1
            else:
                short_pass += 1

    return short_pass, long_pass

test_cases = load_test_cases()
print(f"Loaded {len(test_cases)} tests")

# Try random search with focus on low thresholds and high rates
best_score = 0
best_params = None

print("Searching for thresholds...")
for i in range(50000):
    # Try lower thresholds = degradation kicks in earlier
    tS = random.randint(1, 8)
    tM = random.randint(3, 15)
    tH = random.randint(5, 25)

    # Try various rates
    rS = random.uniform(0.001, 0.05)
    rM = random.uniform(0.0005, 0.02)
    rH = random.uniform(0.0001, 0.01)

    # Keep offsets at known good values
    oM = 1.0
    oH = 1.8

    params = [oM, oH, tS, tM, tH, rS, rM, rH]
    sp, lp = test_params(params, test_cases)
    score = sp + lp

    if score > best_score:
        best_score = score
        best_params = params
        print(f"Iter {i}: Score = {score} (short={sp}, long={lp})")

    if score >= 80:
        break

print(f"\nBest: {best_score}/100")
if best_params:
    print(f"Params: oM={best_params[0]:.2f}, oH={best_params[1]:.2f}")
    print(f"Thresholds: S={int(best_params[2])}, M={int(best_params[3])}, H={int(best_params[4])}")
    print(f"Rates: S={best_params[5]:.4f}, M={best_params[6]:.4f}, H={best_params[7]:.5f}")
