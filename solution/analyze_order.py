#!/usr/bin/env python3
"""
Check if expected order is sorted by something we can calculate.
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

# For each test case, check what metric the expected order is sorted by
for idx, tc in enumerate(test_cases[:5]):  # First 5 tests
    print(f"\n=== Test {idx+1} ===")

    # Calculate various metrics for each driver
    metrics = []
    for key, strat in tc['input']['strategies'].items():
        grid = int(key.replace('pos', ''))
        start_tire = strat['starting_tire']
        num_pits = len(strat['pit_stops'])
        first_pit = strat['pit_stops'][0]['lap'] if strat['pit_stops'] else 999
        last_pit = strat['pit_stops'][-1]['lap'] if strat['pit_stops'] else 0

        metrics.append({
            'driver': strat['driver_id'],
            'grid': grid,
            'start_tire': start_tire,
            'num_pits': num_pits,
            'first_pit': first_pit,
            'last_pit': last_pit
        })

    # Get expected order
    expected = tc['expected']

    # Check correlation: what's the position difference?
    print(f"Expected order with metrics:")
    for pos, driver in enumerate(expected):
        m = next(x for x in metrics if x['driver'] == driver)
        print(f"  {pos+1}. {driver}: grid={m['grid']}, pits={m['num_pits']}, first_pit={m['first_pit']}")

    # Check: is expected sorted by first_pit lap?
    by_first_pit = sorted(metrics, key=lambda x: (x['first_pit'], x['grid']))
    pred = [x['driver'] for x in by_first_pit]
    match = (pred == expected)
    print(f"  Sorted by first pit: {'MATCH' if match else 'no'}")

    # Sorted by grid?
    by_grid = sorted(metrics, key=lambda x: x['grid'])
    pred = [x['driver'] for x in by_grid]
    match = (pred == expected)
    print(f"  Sorted by grid: {'MATCH' if match else 'no'}")
