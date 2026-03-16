#!/usr/bin/env python3
"""
Check the correlation between temperature and passing.
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

# Check passing vs failing by temp
passing_temps = []
failing_temps = []

for i in range(1, 101):
    with open(os.path.join(DATA_DIR, 'inputs', f'test_{i:03d}.json')) as f:
        inp = json.load(f)
    with open(os.path.join(DATA_DIR, 'expected_outputs', f'test_{i:03d}.json')) as f:
        exp = json.load(f)

    laps = inp['race_config']['total_laps']
    temp = inp['race_config']['track_temp']

    results = []
    for strat in inp['strategies'].values():
        t = calc_time(strat, inp['race_config'])
        results.append((strat['driver_id'], t))
    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]

    if pred == exp['finishing_positions']:
        passing_temps.append(temp)
    else:
        failing_temps.append(temp)

print("Passing tests - temperatures:")
print(passing_temps)
print(f"Average: {sum(passing_temps)/len(passing_temps):.1f}")

print("\nFailing tests - temperatures:")
print(failing_temps[:30])
print(f"Average: {sum(failing_temps)/len(failing_temps):.1f}")

# Group by temp
from collections import Counter
print("\nBy temperature:")
for temp in sorted(set(passing_temps + failing_temps)):
    p = passing_temps.count(temp)
    f = failing_temps.count(temp)
    total = p + f
    pct = p / total * 100 if total > 0 else 0
    print(f"  {temp}C: {p}/{total} = {pct:.0f}% passing")
