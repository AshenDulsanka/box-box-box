#!/usr/bin/env python3
"""
Test found params on all 100 test cases.
"""

import json
import os

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

# Found params from historical
oM, oH = 2.5, 4.5
tS, tM, tH = 13, 10, 45
rS, rM, rH = 0.011, 0.004, 0.0006

offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

def calc_time(strategy, race_config):
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

# Test
passed = 0
for tc in test_cases:
    results = []
    for strat in tc['input']['strategies'].values():
        t = calc_time(strat, tc['input']['race_config'])
        results.append((strat['driver_id'], t))
    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]
    if pred == tc['expected']:
        passed += 1

print(f"Result: {passed}/100")
