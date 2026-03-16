#!/usr/bin/env python3
"""
Check which 40-lap tests pass.
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

def calc_time(strategy, laps, base, pit):
    offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, laps + 1):
        total += base + offsets[tire]
        if lap in pit_map:
            total += pit
            tire = pit_map[lap]
    return total

# Check all 40-lap tests
for num in ['049', '050', '055', '087', '089', '094']:
    inp, exp = load_test(num)

    results = []
    for key, strat in inp['strategies'].items():
        time = calc_time(strat, inp['race_config']['total_laps'], inp['race_config']['base_lap_time'], inp['race_config']['pit_lane_time'])
        results.append((strat['driver_id'], time))

    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]

    match = (pred == exp['finishing_positions'])
    print(f"test_{num}: {'PASS' if match else 'FAIL'} ({inp['race_config']['track']}, {inp['race_config']['track_temp']}C)")
