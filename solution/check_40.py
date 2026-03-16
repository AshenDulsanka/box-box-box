#!/usr/bin/env python3
"""
Find what makes the 40-lap passing test different from failing ones.
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

# Find all 40-lap tests
all_tests = []
for i in range(1, 101):
    inp, exp = load_test(f'{i:03d}')
    laps = inp['race_config']['total_laps']
    track = inp['race_config']['track']
    all_tests.append((i, laps, track))

print("All 40-lap tests:")
for num, laps, track in all_tests:
    if laps == 40:
        print(f"  test_{num:03d}: {track}")

# Compare track, temp, etc for 40-lap tests
print("\n=== Comparing 40-lap tests ===")
for num, laps, track in all_tests:
    if laps == 40:
        inp, exp = load_test(f'{num:03d}')
        print(f"test_{num:03d}: {track}, temp={inp['race_config']['track_temp']}, base={inp['race_config']['base_lap_time']}, pit={inp['race_config']['pit_lane_time']}")
