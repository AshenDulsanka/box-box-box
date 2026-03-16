#!/usr/bin/env python3
"""
Check if there's a driver/team pattern.
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

# For each test, get grid position of expected winner
winners = []
for tc in test_cases:
    expected = tc['expected']
    winner = expected[0]

    # Find winner's grid position
    for key, strat in tc['input']['strategies'].items():
        if strat['driver_id'] == winner:
            grid = int(key.replace('pos', ''))
            winners.append({
                'winner': winner,
                'grid': grid,
                'start_tire': strat['starting_tire']
            })
            break

print("Expected winners and their grid positions:")
from collections import Counter
grid_counter = Counter(w['grid'] for w in winners)
driver_counter = Counter(w['winner'] for w in winners)

print("\nBy grid position:")
for grid in sorted(grid_counter.keys()):
    print(f"  Grid {grid}: {grid_counter[grid]} wins")

print("\nBy driver:")
for driver, count in driver_counter.most_common():
    print(f"  {driver}: {count} wins")

# Check: does expected winner tend to start from a specific position?
print("\nGrid position of expected winner:")
for w in winners[:20]:
    print(f"  {w['winner']}: grid {w['grid']}")
