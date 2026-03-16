#!/usr/bin/env python3
"""
Try different formula variations:
1. Degradation calculated BEFORE pit (not after)
2. Different lap time calculation order
3. Starting position affects result
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

# Formula 1: Degradation calculated BEFORE the lap (not cumulative from start)
def calc_before_lap(strategy, race_config, oM, oH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        # Calculate age-based deg BEFORE current lap
        age += 1
        lap_time = race_config['base_lap_time'] + offsets[tire]
        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            age = 0
    return total

# Formula 2: Use stint number (1st stint, 2nd stint) as factor
def calc_with_stint(strategy, race_config, oM, oH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    stint = 1
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]
        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            stint += 1
    return total

# Formula 3: First lap of stint is slower (warm-up)
def calc_warmup(strategy, race_config, oM, oH, warmup_penalty):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    is_first_lap = True
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]
        if is_first_lap:
            lap_time += warmup_penalty
        total += lap_time
        is_first_lap = False
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            is_first_lap = True
    return total

# Test each formula
def test_formula(formula_func, oM=1.0, oH=1.8, **kwargs):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = formula_func(strat, tc['input']['race_config'], oM, oH, **kwargs)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

print("\nTesting different formula variations:")

# Test 1: Basic
score = test_formula(calc_before_lap, 1.0, 1.8)
print(f"Basic (oM=1.0, oH=1.8): {score}/100")

# Test 2: Different offsets
for oM in [0.5, 0.8, 1.0, 1.2, 1.5]:
    for oH in [1.0, 1.5, 1.8, 2.0, 2.5]:
        score = test_formula(calc_before_lap, oM, oH)
        if score > 20:
            print(f"Offset oM={oM}, oH={oH}: {score}/100")

# Test 3: Warm-up penalty
for wp in [0.5, 1.0, 1.5, 2.0, -0.5, -1.0]:
    score = test_formula(calc_warmup, 1.0, 1.8, warmup_penalty=wp)
    if score >= 20:
        print(f"Warmup penalty={wp}: {score}/100")
