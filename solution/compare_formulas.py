#!/usr/bin/env python3
"""
Compare passing vs failing races to understand what's different.
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
    """Our current formula (pure offsets)"""
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

# Compare passing test 001 (31 laps) with failing test 003 (44 laps)
print("=== PASSING TEST 001 (31 laps) ===")
t1, e1 = load_test('001')
print(f"Track: {t1['race_config']['track']}, Laps: {t1['race_config']['total_laps']}")

# Calculate times
results = []
for key, strat in t1['strategies'].items():
    time = calc_time(strat, t1['race_config']['total_laps'], t1['race_config']['base_lap_time'], t1['race_config']['pit_lane_time'])
    results.append((strat['driver_id'], time, e1['finishing_positions'].index(strat['driver_id'])))

results.sort(key=lambda x: x[1])
pred = [r[0] for r in results]
print(f"Expected: {e1['finishing_positions'][:5]}")
print(f"Predicted: {pred[:5]}")
print(f"Match: {pred == e1['finishing_positions']}")

print("\n=== FAILING TEST 003 (44 laps) ===")
t3, e3 = load_test('003')
print(f"Track: {t3['race_config']['track']}, Laps: {t3['race_config']['total_laps']}")

results = []
for key, strat in t3['strategies'].items():
    time = calc_time(strat, t3['race_config']['total_laps'], t3['race_config']['base_lap_time'], t3['race_config']['pit_lane_time'])
    results.append((strat['driver_id'], time, e3['finishing_positions'].index(strat['driver_id'])))

results.sort(key=lambda x: x[1])
pred = [r[0] for r in results]
print(f"Expected: {e3['finishing_positions'][:5]}")
print(f"Predicted: {pred[:5]}")
print(f"Match: {pred == e3['finishing_positions']}")

# Now check: what if we use GRID as the tiebreaker for races > 40 laps?
print("\n=== What if we use grid position as tiebreaker for long races? ===")

# For test 003, sort by calculated time, then by grid
results_with_grid = []
for key, strat in t3['strategies'].items():
    time = calc_time(strat, t3['race_config']['total_laps'], t3['race_config']['base_lap_time'], t3['race_config']['pit_lane_time'])
    grid = int(key.replace('pos', ''))
    results_with_grid.append((strat['driver_id'], time, grid))

# Sort by time first, then by grid (lower grid = better)
results_with_grid.sort(key=lambda x: (x[1], x[2]))
pred_grid = [r[0] for r in results_with_grid]
print(f"Predicted (time+grid): {pred_grid[:5]}")
print(f"Match: {pred_grid == e3['finishing_positions']}")
