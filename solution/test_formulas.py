#!/usr/bin/env python3
"""
Test different offset formulas to find what works.
"""

import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

def load_test_cases():
    inputs_dir = os.path.join(DATA_DIR, 'inputs')
    expected_dir = os.path.join(DATA_DIR, 'expected_outputs')

    test_cases = []
    files = sorted([f for f in os.listdir(inputs_dir) if f.startswith('test_') and f.endswith('.json')])

    for file in files:
        with open(os.path.join(inputs_dir, file)) as f:
            input_data = json.load(f)
        with open(os.path.join(expected_dir, file)) as f:
            expected = json.load(f)
        test_cases.append({
            'input': input_data,
            'expected': expected['finishing_positions'],
            'laps': input_data['race_config']['total_laps']
        })

    return test_cases

# Try different offset formulas
def test_offsets(formula_func, test_cases):
    passed = 0
    for tc in test_cases:
        race_config = tc['input']['race_config']
        strategies = tc['input']['strategies']
        expected = tc['expected']

        results = []
        for strat in strategies.values():
            time = formula_func(strat, race_config)
            results.append((strat['driver_id'], time))

        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]

        if pred == expected:
            passed += 1

    return passed

# Formula 1: Pure offsets (current)
def formula_offsets_only(strategy, race_config):
    offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += race_config['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Formula 2: Percentage offsets
def formula_pct_offsets(strategy, race_config):
    base = race_config['base_lap_time']
    offsets = {'SOFT': 0, 'MEDIUM': 0.012, 'HARD': 0.02}  # As percentage
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += base * (1 + offsets[tire])
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Formula 3: Different offsets per track
def formula_track_offsets(strategy, race_config):
    track = race_config['track']
    offsets = {
        'Monaco': {'SOFT': 0, 'MEDIUM': 1.2, 'HARD': 2.0},
        'Monza': {'SOFT': 0, 'MEDIUM': 0.8, 'HARD': 1.5},
        'Bahrain': {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8},
        'Spa': {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 2.0},
        'Silverstone': {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8},
        'Suzuka': {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8},
        'COTA': {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8},
    }
    off = offsets.get(track, {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8})
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += race_config['base_lap_time'] + off[tire]
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

test_cases = load_test_cases()
print("Testing different offset formulas...")

formulas = [
    ("Pure offsets (M=1.0, H=1.8)", formula_offsets_only),
    ("Percentage offsets", formula_pct_offsets),
    ("Track-specific offsets", formula_track_offsets),
]

for name, func in formulas:
    score = test_offsets(func, test_cases)
    print(f"{name}: {score}/100")

# Also check short vs long
print("\nBy race length:")
for tc in test_cases:
    race_config = tc['input']['race_config']
    strategies = tc['input']['strategies']
    expected = tc['expected']

    results = []
    for strat in strategies.values():
        time = formula_offsets_only(strat, race_config)
        results.append((strat['driver_id'], time))

    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]

    is_short = tc['laps'] < 40
    match = pred == expected
    print(f"  {tc['laps']} laps: {'PASS' if match else 'FAIL'}")
