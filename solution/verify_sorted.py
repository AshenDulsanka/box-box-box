#!/usr/bin/env python3
"""
Verify: Are expected positions sorted by time?
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

offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}

def calc_time(strategy, race_config):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += race_config['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Check if expected order is sorted by calculated time
for test_num in ['001', '003', '004', '049', '094']:
    inp, exp = load_test(test_num)

    # Calculate times
    times = []
    for strat in inp['strategies'].values():
        t = calc_time(strat, inp['race_config'])
        times.append((strat['driver_id'], t))

    # Sort by time
    times.sort(key=lambda x: x[1])
    predicted = [d for d, t in times]

    # Check if expected is sorted
    is_sorted = (exp['finishing_positions'] == predicted)

    print(f"Test {test_num} ({inp['race_config']['total_laps']} laps): Expected sorted by time? {is_sorted}")
