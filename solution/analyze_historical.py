#!/usr/bin/env python3
"""
Analyze historical races to find the formula.
"""

import json
import os

HIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_races')

# Load first batch of historical races
print("Loading historical races...")
with open(os.path.join(HIST_DIR, 'races_00000-00999.json')) as f:
    races = json.load(f)

print(f"Loaded {len(races)} races")

# Analyze a few races in detail
for i, race in enumerate(races[:5]):
    print(f"\n=== Race {i}: {race['race_config']['track']} ===")
    print(f"Laps: {race['race_config']['total_laps']}")
    print(f"Base lap: {race['race_config']['base_lap_time']}")
    print(f"Pit lane: {race['race_config']['pit_lane_time']}")
    print(f"Temp: {race['race_config']['track_temp']}")

    # Get expected order
    expected = race['finishing_positions']
    print(f"Expected winner: {expected[0]}")

    # Get strategies
    strategies = race['strategies']
    winner_strat = None
    for key, strat in strategies.items():
        if strat['driver_id'] == expected[0]:
            winner_strat = strat
            print(f"Winner strategy: {strat['starting_tire']}, pits: {[(p['lap'], p['to_tire']) for p in strat['pit_stops']]}")
            break

# Check correlation between our calculation and expected for historical races
def calc_time(strategy, laps, base, pit, offsets):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    total = 0
    for lap in range(1, laps + 1):
        total += base + offsets[tire]
        if lap in pit_map:
            total += pit
            tire = pit_map[lap]
    return total

offsets = {'SOFT': 0, 'MEDIUM': 1.0, 'HARD': 1.8}

# Test on historical races
passed = 0
failures = []
for race in races[:1000]:
    results = []
    for strat in race['strategies'].values():
        time = calc_time(strat, race['race_config']['total_laps'],
                       race['race_config']['base_lap_time'],
                       race['race_config']['pit_lane_time'],
                       offsets)
        results.append((strat['driver_id'], time))

    results.sort(key=lambda x: x[1])
    pred = [r[0] for r in results]

    if pred == race['finishing_positions']:
        passed += 1
    else:
        laps = race['race_config']['total_laps']
        failures.append(laps)

print(f"\n\nHistorical accuracy (pure offsets): {passed}/1000 = {passed/10}%")

# Analyze by lap count
lap_buckets = {}
for lap in failures:
    bucket = (lap // 10) * 10
    lap_buckets[bucket] = lap_buckets.get(bucket, 0) + 1

print("Failures by lap count:")
for bucket in sorted(lap_buckets.keys()):
    print(f"  {bucket}-{bucket+9}: {lap_buckets[bucket]}")
