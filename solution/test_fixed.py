#!/usr/bin/env python3
"""
Test: Fixed degradation per lap (not cumulative)
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

        # FIXED degradation per lap after threshold (not cumulative!)
        if age > thresholds.get(tire, 100):
            deg = rates.get(tire, 0)  # Fixed amount per lap
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

# Try random params with fixed degradation
best_score = 0
best_params = None

print("Testing fixed degradation...")
for i in range(50000):
    oM = random.uniform(0.1, 5.0)
    oH = random.uniform(0.2, 8.0)

    # Fixed degradation per lap
    rS = random.uniform(0.001, 0.1)
    rM = random.uniform(0.001, 0.05)
    rH = random.uniform(0.001, 0.03)

    tS = random.randint(1, 20)
    tM = random.randint(5, 30)
    tH = random.randint(10, 40)

    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    score = test(offsets, thresholds, rates)

    if score > best_score:
        best_score = score
        best_params = (oM, oH, tS, tM, tH, rS, rM, rH)
        print(f"Iter {i}: Best = {score}/100")

print(f"\nBest: {best_score}/100")
if best_params:
    print(f"Params: oM={best_params[0]:.2f}, oH={best_params[1]:.2f}")
    print(f"Thresholds: S={best_params[2]}, M={best_params[3]}, H={best_params[4]}")
    print(f"Rates: S={best_params[5]:.3f}, M={best_params[6]:.3f}, H={best_params[7]:.3f}")
