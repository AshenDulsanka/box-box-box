#!/usr/bin/env python3
"""
Check the boundary: which laps does expected stop being sorted by time?
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_cases')

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

# Check each test
for i in range(1, 101):
    with open(os.path.join(DATA_DIR, 'inputs', f'test_{i:03d}.json')) as f:
        inp = json.load(f)
    with open(os.path.join(DATA_DIR, 'expected_outputs', f'test_{i:03d}.json')) as f:
        exp = json.load(f)

    laps = inp['race_config']['total_laps']

    # Calculate times
    times = []
    for strat in inp['strategies'].values():
        t = calc_time(strat, inp['race_config'])
        times.append((strat['driver_id'], t))
    times.sort(key=lambda x: x[1])
    predicted = [d for d, _ in times]

    is_sorted = (exp['finishing_positions'] == predicted)
    print(f"Test {i:3d} ({laps:2d} laps): {'PASS' if is_sorted else 'FAIL'}")
