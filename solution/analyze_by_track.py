#!/usr/bin/env python3
"""
Analyze which tracks pass and which fail.
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
    test_cases.append({'input': inp, 'expected': exp['finishing_positions'], 'track': inp['race_config']['track']})

print(f"Loaded {len(test_cases)} tests")

def calc_time(strategy, race_config):
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

# Test each track
track_results = {}
for tc in test_cases:
    track = tc['track']
    if track not in track_results:
        track_results[track] = {'pass': 0, 'fail': 0}

    results = []
    for strat in tc['input']['strategies'].values():
        t = calc_time(strat, tc['input']['race_config'])
        results.append((strat['driver_id'], t))
    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]

    if pred == tc['expected']:
        track_results[track]['pass'] += 1
    else:
        track_results[track]['fail'] += 1

print("\nResults by track:")
for track, results in sorted(track_results.items()):
    total = results['pass'] + results['fail']
    pct = results['pass'] / total * 100
    print(f"  {track}: {results['pass']}/{total} = {pct:.1f}%")
