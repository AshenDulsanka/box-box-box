#!/usr/bin/env python3
"""
Try exponential degradation for long races.
"""

import json
import os
import math

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

# Exponential degradation
def calc_exp(strategy, race_config, oM, oH, exp_factor):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        age += 1
        lap_time = race_config['base_lap_time'] + offsets[tire]

        # Exponential degradation
        if age > 1:
            deg = exp_factor * (math.exp(age * 0.1) - 1)
            lap_time += deg

        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            age = 0
    return total

# Test
def test_exp(exp_factor):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = calc_exp(strat, tc['input']['race_config'], 1.0, 1.8, exp_factor)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

print("\nTesting exponential degradation:")
for ef in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
    score = test_exp(ef)
    if score >= 20:
        print(f"exp_factor={ef}: {score}/100")
