#!/usr/bin/env python3
"""
Test: What if tire age increments AFTER calculating lap time?
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

def simulate_after(strategy, race_config, offsets):
    """Tire age increments AFTER lap time"""
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        # Age 0 for first lap (fresh tires)
        lap_time = race_config['base_lap_time'] + offsets.get(tire, 0)
        total += lap_time

        # Increment age AFTER
        age += 1

        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            age = 0
    return total

def test(offsets):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = simulate_after(strat, tc['input']['race_config'], offsets)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

test_cases = load_test_cases()
print("Loaded tests")

# Test: age after lap time
offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}
print(f"Age after lap time: {test(offsets)}/100")
