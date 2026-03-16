#!/usr/bin/env python3
"""
Try linear (non-cumulative) degradation.
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
        })

    return test_cases

def simulate_driver_linear(strategy, race_config, offsets, thresholds, rates):
    """Linear degradation: deg = rate * tire_age (not cumulative)"""
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    current_tire = strategy['starting_tire']
    tire_age = 0
    total_time = 0

    for lap in range(1, race_config['total_laps'] + 1):
        tire_age += 1

        lap_time = race_config['base_lap_time'] + offsets.get(current_tire, 0)

        # Linear degradation based on current tire age
        if tire_age > thresholds.get(current_tire, 100):
            deg = rates.get(current_tire, 0) * tire_age
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

    passed = 0
    for tc in test_cases:
        expected = tc['expected']
        results = []
        for strat in tc['input']['strategies'].values():
            time = simulate_driver_linear(strat, tc['input']['race_config'], offsets, thresholds, rates)
            results.append((strat['driver_id'], time))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == expected:
            passed += 1

    return passed

test_cases = load_test_cases()
print(f"Loaded {len(test_cases)} tests")

best_score = 0
best_params = None

print("Testing linear degradation...")
for i in range(50000):
    params = [
        random.uniform(0.1, 3.0),
        random.uniform(0.5, 5.0),
        random.randint(1, 20),
        random.randint(5, 30),
        random.randint(10, 40),
        random.uniform(0.001, 0.1),
        random.uniform(0.0005, 0.05),
        random.uniform(0.0001, 0.02),
    ]

    score = test_params(params, test_cases)

    if score > best_score:
        best_score = score
        best_params = params
        print(f"Iter {i}: Best = {score}/100")

    if score >= 80:
        break

print(f"\nBest: {best_score}/100")
if best_params:
    print(f"Params: {best_params}")
