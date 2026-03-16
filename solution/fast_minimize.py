#!/usr/bin/env python3
"""
Fast grid search with scipy minimize.
"""

import json
import os
import numpy as np
from scipy.optimize import minimize

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

def calc_time(strategy, race_config, oM, oH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += race_config['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

def objective(params):
    oM, oH = params[0], params[1]

    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = calc_time(strat, tc['input']['race_config'], oM, oH)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1

    return -passed

# Try different starting points
best_score = 0
best_params = None

print("Running optimization...")
for oM in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    for oH in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]:
        result = minimize(objective, [oM, oH], method='Nelder-Mead',
                        options={'xatol': 0.1, 'fatol': 1, 'maxiter': 100})

        score = -result.fun
        if score > best_score:
            best_score = score
            best_params = result.x
            print(f"New best: {score}/100 (oM={result.x[0]:.2f}, oH={result.x[1]:.2f})")

print(f"\nBest: {best_score}/100")
print(f"Params: {best_params}")
