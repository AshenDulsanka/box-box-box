#!/usr/bin/env python3
"""
Check what's different about passing tests.
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
    test_cases.append({'input': inp, 'expected': exp['finishing_positions'], 'num': i})

print(f"Loaded {len(test_cases)} tests")

def calc_time(strategy, race_config, oM, oH):
    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, race_config['total_laps'] + 1):
        total += race_config['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += race_config['pit_lane_time']
            tire = pit_map[lap]
    return total

# Find passing tests
passing = []
for tc in test_cases:
    results = []
    for strat in tc['input']['strategies'].values():
        t = calc_time(strat, tc['input']['race_config'], 1.0, 1.8)
        results.append((strat['driver_id'], t))
    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]
    if pred == tc['expected']:
        passing.append(tc)

print(f"Passing tests: {len(passing)}")
print("\nPassing test details:")
for tc in passing:
    cfg = tc['input']['race_config']
    print(f"  {tc['num']:3d}: {cfg['track']:10s} {cfg['total_laps']:2d} laps, {cfg['track_temp']}C, base={cfg['base_lap_time']}, pit={cfg['pit_lane_time']}")
