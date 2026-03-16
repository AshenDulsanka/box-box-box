#!/usr/bin/env python3
"""
More creative approaches:
1. Average lap time (instead of sum)
2. Last lap time matters more
3. Pit stop lap doesn't count full time
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

# Formula: Last N laps weighted more
def calc_weighted(strategy, race_config, oM, oH, weight_last):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    laps = race_config['total_laps']
    for lap in range(1, laps + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]
        if lap > laps - weight_last:
            lap_time *= 2  # Last laps worth double
        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Formula: Different pit calculation
def calc_pit_before(strategy, race_config, oM, oH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            # Add pit time BEFORE continuing (so current lap on old tires)
            lap_time += race_config['pit_lane_time']
        total += lap_time
        if lap in pit_map:
            tire = pit_map[lap]
    return total

# Formula: Starting position matters
def calc_with_start(strategy, race_config, oM, oH, start_factor):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]
        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

def test_formula(formula_func, **kwargs):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = formula_func(strat, tc['input']['race_config'], **kwargs)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

print("\nTesting more variations:")

# Test basic
print(f"Basic: {test_formula(calc_pit_before, oM=1.0, oH=1.8)}/100")

# Test weighted
for w in [1, 2, 3, 5, 10]:
    score = test_formula(calc_weighted, oM=1.0, oH=1.8, weight_last=w)
    if score >= 20:
        print(f"Weighted last {w}: {score}/100")

# Test starting position
for s in [0.1, 0.5, 1.0, -0.1, -0.5]:
    score = test_formula(calc_with_start, oM=1.0, oH=1.8, start_factor=s)
    if score >= 20:
        print(f"Start factor {s}: {score}/100")
