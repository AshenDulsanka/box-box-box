#!/usr/bin/env python3
"""
Check why test 94 passes but other 40-lap tests fail.
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

# Compare test 094 (passes) with other 40-lap tests that fail
print("=== Test 094 (PASSES, 40 laps) ===")
t94, e94 = load_test('094')
print(f"Track: {t94['race_config']['track']}")
print(f"Temp: {t94['race_config']['track_temp']}C")
print(f"Base: {t94['race_config']['base_lap_time']}")
print(f"Pit: {t94['race_config']['pit_lane_time']}")

# Get expected order and compare
offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}

results = []
for key, strat in t94['strategies'].items():
    pit_map = {p['lap']: p['to_tire'] for p in strat['pit_stops']}
    tire = strat['starting_tire']
    total = 0
    for lap in range(1, 40 + 1):
        total += t94['race_config']['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += t94['race_config']['pit_lane_time']
            tire = pit_map[lap]
    results.append((strat['driver_id'], total))

results.sort(key=lambda x: x[1])
pred = [r[0] for r in results]

print(f"Expected: {e94['finishing_positions'][:5]}")
print(f"Predicted: {pred[:5]}")
print(f"Match: {pred == e94['finishing_positions']}")

# Now check test 049 (fails)
print("\n=== Test 049 (FAILS, 40 laps) ===")
t049, e049 = load_test('049')
print(f"Track: {t049['race_config']['track']}")
print(f"Temp: {t049['race_config']['track_temp']}C")
print(f"Base: {t049['race_config']['base_lap_time']}")
print(f"Pit: {t049['race_config']['pit_lane_time']}")

results = []
for key, strat in t049['strategies'].items():
    pit_map = {p['lap']: p['to_tire'] for p in strat['pit_stops']}
    tire = strat['starting_tire']
    total = 0
    for lap in range(1, 40 + 1):
        total += t049['race_config']['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += t049['race_config']['pit_lane_time']
            tire = pit_map[lap]
    results.append((strat['driver_id'], total))

results.sort(key=lambda x: x[1])
pred = [r[0] for r in results]

print(f"Expected: {e049['finishing_positions'][:5]}")
print(f"Predicted: {pred[:5]}")
print(f"Match: {pred == e049['finishing_positions']}")
