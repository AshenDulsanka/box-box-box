#!/usr/bin/env python3
"""
Reverse engineer the formula from expected times.
For each test, calculate what lap times must be to match expected order.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

def load_test(num):
    with open(os.path.join(DATA_DIR, 'inputs', f'test_{num}.json')) as f:
        inp = json.load(f)
    with open(os.path.join(DATA_DIR, 'expected_outputs', f'test_{num}.json')) as f:
        exp = json.load(f)
    return inp, exp

# Let's look at the simplest failing case - test 003 (44 laps)
inp, exp = load_test('003')

print("=== TEST 003 Analysis ===")
print(f"Track: {inp['race_config']['track']}")
print(f"Laps: {inp['race_config']['total_laps']}")
print(f"Base lap: {inp['race_config']['base_lap_time']}")
print(f"Pit lane: {inp['race_config']['pit_lane_time']}")
print(f"Temp: {inp['race_config']['track_temp']}")

# Get expected finishing order
expected = exp['finishing_positions']

# For each driver, calculate what their total time must be
# If expected position is i, their time must be < time of position i+1 and > time of position i-1

# Let's get all drivers' strategies
drivers = {}
for key, strat in inp['strategies'].items():
    drivers[strat['driver_id']] = {
        'grid': int(key.replace('pos', '')),
        'start': strat['starting_tire'],
        'pits': [(p['lap'], p['to_tire']) for p in strat['pit_stops']]
    }

# Show expected winner details
print("\nExpected winner (D016):")
d = drivers['D016']
print(f"  Grid: {d['grid']}, Start: {d['start']}, Pits: {d['pits']}")

# What if we just assume expected order = grid order (with some adjustment)?
# Let's check: what's the correlation?

# Get grid positions in expected order
grids_in_exp = [drivers[d]['grid'] for d in expected]
print("\nGrid positions in expected order:")
print(grids_in_exp)

# Check if there's a simple transformation
# Like: finishing_pos = f(grid_pos, strategy)

# Let's check: for each driver, what's their position difference?
for i, driver in enumerate(expected[:10]):
    d = drivers[driver]
    grid_diff = d['grid'] - (i + 1)
    print(f"Pos{i+1}: {driver} grid={d['grid']} diff={grid_diff}")
