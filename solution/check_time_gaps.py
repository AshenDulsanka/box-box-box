#!/usr/bin/env python3
"""
Check the actual time differences between positions in expected order.
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

# Analyze a long race
inp, exp = load_test('003')  # 44 laps, fails

print("=== TEST 003 Analysis ===")
print(f"Laps: {inp['race_config']['total_laps']}")
print(f"Base: {inp['race_config']['base_lap_time']}, Pit: {inp['race_config']['pit_lane_time']}")

# Calculate our times
offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}

times = []
for key, strat in inp['strategies'].items():
    pit_map = {p['lap']: p['to_tire'] for p in strat['pit_stops']}
    tire = strat['starting_tire']
    total = 0
    for lap in range(1, 45):
        total += inp['race_config']['base_lap_time'] + offsets[tire]
        if lap in pit_map:
            total += inp['race_config']['pit_lane_time']
            tire = pit_map[lap]
    times.append((strat['driver_id'], total, key))

times.sort(key=lambda x: x[1])

print("\nOur predicted order (times):")
for i, (d, t, key) in enumerate(times[:5]):
    print(f"  {i+1}. {d}: {t:.1f}s")

print("\nExpected order:")
for i, d in enumerate(exp['finishing_positions'][:5]):
    our_time = next(t[1] for t in times if t[0] == d)
    print(f"  {i+1}. {d}: {our_time:.1f}s")

# The key question: what's the time gap between expected positions?
print("\n=== Time gaps in EXPECTED order ===")
# For expected order, calculate what times would need to be
# (Assuming our calculation is wrong, what would the times need to be?)

# Get expected times assuming our time differences are proportional
expected_order = exp['finishing_positions']

# Find drivers in expected order and their calculated times
driver_times = {d: t for d, t, _ in times}

print("Time differences between consecutive positions (expected):")
prev_time = None
for driver in expected_order[:10]:
    curr_time = driver_times[driver]
    if prev_time:
        diff = curr_time - prev_time
        print(f"  {driver}: {diff:.2f}s from previous")
    prev_time = curr_time
