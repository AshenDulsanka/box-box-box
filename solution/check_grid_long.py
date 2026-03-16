#!/usr/bin/env python3
"""
Check if expected order for long races is just grid position.
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
    test_cases.append({'input': inp, 'expected': exp['finishing_positions'], 'laps': inp['race_config']['total_laps']})

# Check long races: is expected = grid position?
long_tests = [tc for tc in test_cases if tc['laps'] >= 40]

matches_grid = 0
for tc in long_tests:
    # Get expected order
    expected = tc['expected']

    # Get grid positions in expected order
    grids = []
    for driver in expected:
        for key, strat in tc['input']['strategies'].items():
            if strat['driver_id'] == driver:
                grids.append(int(key.replace('pos', '')))
                break

    # Check if expected is sorted by grid position
    is_sorted = (grids == sorted(grids))

    if is_sorted:
        matches_grid += 1
        print(f"Test (laps={tc['laps']}): MATCHES grid order")

print(f"\nTotal: {matches_grid}/{len(long_tests)} match grid order")

# Check: is expected = REVERSE grid?
matches_reverse = 0
for tc in long_tests:
    expected = tc['expected']

    grids = []
    for driver in expected:
        for key, strat in tc['input']['strategies'].items():
            if strat['driver_id'] == driver:
                grids.append(int(key.replace('pos', '')))
                break

    # Check if sorted in reverse
    is_reverse = (grids == sorted(grids, reverse=True))

    if is_reverse:
        matches_reverse += 1

print(f"Total: {matches_reverse}/{len(long_tests)} match REVERSE grid order")
