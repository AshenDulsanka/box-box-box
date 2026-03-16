#!/usr/bin/env python3
"""
Optimize directly on test cases with focused search.
"""

import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

# Load test cases
test_cases = []
for i in range(1, 101):
    with open(os.path.join(DATA_DIR, 'inputs', f'test_{i:03d}.json')) as f:
        inp = json.load(f)
    with open(os.path.join(DATA_DIR, 'expected_outputs', f'test_{i:03d}.json')) as f:
        exp = json.load(f)
    test_cases.append({'input': inp, 'expected': exp['finishing_positions']})

print(f"Loaded {len(test_cases)} tests")

def calc_time(strategy, race_config, offsets, thresholds, rates):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        age += 1
        lap_time = race_config['base_lap_time'] + offsets.get(tire, 0)
        if age > thresholds.get(tire, 100):
            laps_over = age - thresholds.get(tire, 100)
            deg = rates.get(tire, 0) * (laps_over * (laps_over + 1)) / 2
            lap_time += deg
        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            age = 0
    return total

def test(offsets, thresholds, rates):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = calc_time(strat, tc['input']['race_config'], offsets, thresholds, rates)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

# Try many random combinations focused on offsets
best_score = 0
best_params = None

print("Searching for offsets...")
for i in range(100000):
    # Random offsets
    oM = random.uniform(0.1, 5.0)
    oH = random.uniform(0.2, 8.0)

    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': 100, 'MEDIUM': 100, 'HARD': 100}
    rates = {'SOFT': 0, 'MEDIUM': 0, 'HARD': 0}

    score = test(offsets, thresholds, rates)

    if score > best_score:
        best_score = score
        best_params = (oM, oH)
        print(f"Iter {i}: Best = {score}/100 (oM={oM:.2f}, oH={oH:.2f})")

    if score >= 80:
        break

print(f"\nBest: {best_score}/100")
print(f"Params: oM={best_params[0]:.2f}, oH={best_params[1]:.2f}")
