#!/usr/bin/env python3
"""
Search with degradation.
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

def calc_time(strategy, race_config, oM, oH, tS, tM, tH, rS, rM, rH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        age += 1
        lap_time = race_config['base_lap_time'] + offsets[tire]

        if age > thresholds[tire]:
            laps_over = age - thresholds[tire]
            deg = rates[tire] * (laps_over * (laps_over + 1)) / 2
            lap_time += deg

        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            age = 0
    return total

def test(oM, oH, tS, tM, tH, rS, rM, rH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = calc_time(strat, tc['input']['race_config'], oM, oH, tS, tM, tH, rS, rM, rH)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

# Try many combinations
best_score = 20
best_params = (1.0, 1.8, 100, 100, 100, 0, 0, 0)

print("Testing with degradation...")

# Test with zero degradation (should be 20)
score = test(1.0, 1.8, 100, 100, 100, 0, 0, 0)
print(f"No degradation: {score}/100")

# Try various thresholds and rates
for tS in [5, 10, 15, 20]:
    for rS in [0.001, 0.005, 0.01]:
        for tM in [10, 20, 30]:
            for rM in [0.001, 0.005, 0.01]:
                for tH in [20, 30, 40]:
                    for rH in [0.0005, 0.001, 0.005]:
                        score = test(1.0, 1.8, tS, tM, tH, rS, rM, rH)
                        if score > best_score:
                            best_score = score
                            best_params = (1.0, 1.8, tS, tM, tH, rS, rM, rH)
                            print(f"New best: {score}/100")

print(f"\nBest: {best_score}/100")
print(f"Params: {best_params}")
