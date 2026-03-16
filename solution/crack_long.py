#!/usr/bin/env python3
"""
Focus on long races - try radically different approaches.
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
    test_cases.append({
        'input': inp,
        'expected': exp['finishing_positions'],
        'laps': inp['race_config']['total_laps']
    })

print(f"Loaded {len(test_cases)} tests")

# Focus on long races
long_tests = [tc for tc in test_cases if tc['laps'] >= 40]
print(f"Long races (>=40 laps): {len(long_tests)}")

# Approach 1: What if degradation is based on TOTAL race laps, not tire age?
def calc_race_based(strategy, race_config, oM, oH, deg_factor):
    """Degradation based on race length, not tire age"""
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    laps = race_config['total_laps']

    for lap in range(1, laps + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]

        # Deg factor based on total race laps
        lap_time += deg_factor * laps

        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Approach 2: What if MORE pit stops = BETTER (fresh tires)?
def calc_more_pits(strategy, race_config, oM, oH, pit_bonus):
    """More pit stops = time bonus (less deg)"""
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

    # Bonus for each pit stop
    num_pits = len(strategy['pit_stops'])
    total -= num_pits * pit_bonus
    return total

# Approach 3: What if degradation is based on stint length squared?
def calc_stint_squared(strategy, race_config, oM, oH, rate):
    """Stint-length squared degradation"""
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    stint_len = 0
    total = 0

    for lap in range(1, race_config['total_laps'] + 1):
        lap_time = race_config['base_lap_time'] + offsets[tire]

        # Deg = rate * stint_len^2
        deg = rate * stint_len * stint_len
        lap_time += deg
        stint_len += 1

        total += lap_time
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
            stint_len = 0
    return total

def test_formula(formula_func, **params):
    passed = 0
    for tc in test_cases:
        results = []
        for strat in tc['input']['strategies'].values():
            t = formula_func(strat, tc['input']['race_config'], **params)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

def test_long(formula_func, **params):
    passed = 0
    for tc in long_tests:
        results = []
        for strat in tc['input']['strategies'].values():
            t = formula_func(strat, tc['input']['race_config'], **params)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == tc['expected']:
            passed += 1
    return passed

print("\n=== Approach 1: Race-based degradation ===")
for deg in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]:
    score = test_long(calc_race_based, oM=1.0, oH=1.8, deg_factor=deg)
    if score > 0:
        print(f"deg_factor={deg}: {score}/{len(long_tests)}")

print("\n=== Approach 2: Pit stop bonus ===")
for pit_bonus in [5, 10, 15, 20, 25, 30, 40, 50]:
    score = test_long(calc_more_pits, oM=1.0, oH=1.8, pit_bonus=pit_bonus)
    if score > 0:
        print(f"pit_bonus={pit_bonus}: {score}/{len(long_tests)}")

print("\n=== Approach 3: Stint squared ===")
for rate in [0.0001, 0.0005, 0.001, 0.005, 0.01]:
    score = test_long(calc_stint_squared, oM=1.0, oH=1.8, rate=rate)
    if score > 0:
        print(f"rate={rate}: {score}/{len(long_tests)}")
