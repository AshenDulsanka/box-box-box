#!/usr/bin/env python3
"""
Quick test: Try linear degradation with a few params.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

def load_test_cases():
    inputs_dir = os.path.join(DATA_DIR, 'inputs')
    expected_dir = os.path.join(DATA_DIR, 'expected_outputs')
    test_cases = []
    for i in range(1, 101):
        with open(os.path.join(inputs_dir, f'test_{i:03d}.json')) as f:
            inp = json.load(f)
        with open(os.path.join(expected_dir, f'test_{i:03d}.json')) as f:
            exp = json.load(f)
        test_cases.append({'input': inp, 'expected': exp['finishing_positions']})
    return test_cases

def simulate(strategy, race_config, offsets, thresholds, rates):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        age += 1
        lap_time = race_config['base_lap_time'] + offsets.get(tire, 0)
        if age > thresholds.get(tire, 100):
            lap_time += rates.get(tire, 0) * age
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
            t = simulate(strat, tc['input']['race_config'], offsets, thresholds, rates)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

test_cases = load_test_cases()
print("Loaded tests")

# Test: no degradation
offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}
thresholds = {'SOFT': 100, 'MEDIUM': 100, 'HARD': 100}
rates = {'SOFT': 0, 'MEDIUM': 0, 'HARD': 0}
print(f"No degradation: {test(offsets, thresholds, rates)}/100")

# Test: linear degradation from lap 1
for rS in [0.001, 0.005, 0.01]:
    for rM in [0.0005, 0.001, 0.005]:
        for rH in [0.0001, 0.0005, 0.001]:
            rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}
            thresholds = {'SOFT': 1, 'MEDIUM': 1, 'HARD': 1}
            score = test(offsets, thresholds, rates)
            if score > 20:
                print(f"Linear from lap1 rates={rS},{rM},{rH}: {score}/100")
