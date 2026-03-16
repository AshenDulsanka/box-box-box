#!/usr/bin/env python3
"""
Try to find what makes test 049 fail - check different offsets.
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

t049, e049 = load_test('049')

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

# Test many offsets
best_score = 0
best_offsets = (1.0, 1.8)

for oM in [i*0.1 for i in range(5, 40)]:
    for oH in [i*0.1 for i in range(10, 60)]:
        results = []
        for strat in t049['strategies'].values():
            t = calc_time(strat, t049['race_config'], oM, oH)
            results.append((strat['driver_id'], t))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]

        # Count how many positions match
        matches = sum(1 for i in range(20) if pred[i] == e049['finishing_positions'][i])

        if matches > best_score:
            best_score = matches
            best_offsets = (oM, oH)
            print(f"oM={oM:.1f}, oH={oH:.1f}: {matches}/20 match")

print(f"\nBest: {best_score}/20 with offsets {best_offsets}")
