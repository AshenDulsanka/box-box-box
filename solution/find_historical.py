#!/usr/bin/env python3
"""
Find what formula works for different lap ranges in historical data.
"""

import json
import os
import random

HIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical_races')

# Load historical races
print("Loading historical races...")
all_races = []
for i in range(30):
    with open(os.path.join(HIST_DIR, f'races_{i*1000:05d}-{(i+1)*1000-1:05d}.json')) as f:
        all_races.extend(json.load(f))
        if len(all_races) >= 10000:
            break

print(f"Loaded {len(all_races)} races")

# Test a race with known formula
def calc_time(strategy, laps, base, pit, offsets, thresholds, rates):
    pit_map = {p['lap']: p['to_tire'] for p in strategy['pit_stops']}
    tire = strategy['starting_tire']
    age = 0
    total = 0
    for lap in range(1, laps + 1):
        age += 1
        lap_time = base + offsets.get(tire, 0)
        if age > thresholds.get(tire, 100):
            laps_over = age - thresholds.get(tire, 100)
            deg = rates.get(tire, 0) * (laps_over * (laps_over + 1)) / 2
            lap_time += deg
        total += lap_time
        if lap in pit_map:
            total += pit
            tire = pit_map[lap]
            age = 0
    return total

# Find a race where we know what's happening
# Let's find the simplest race: 1 pit stop, similar strategies

# Find races with similar strategies
simple_races = []
for race in all_races:
    if race['race_config']['total_laps'] < 35:
        simple_races.append(race)

print(f"Simple races (<35 laps): {len(simple_races)}")

# Test different params on simple races
def test_params(params, races):
    oM, oH = params[0], params[1]
    tS, tM, tH = int(params[2]), int(params[3]), int(params[4])
    rS, rM, rH = params[5], params[6], params[7]

    offsets = {'SOFT': 0, 'MEDIUM': oM, 'HARD': oH}
    thresholds = {'SOFT': tS, 'MEDIUM': tM, 'HARD': tH}
    rates = {'SOFT': rS, 'MEDIUM': rM, 'HARD': rH}

    passed = 0
    for race in races:
        results = []
        for strat in race['strategies'].values():
            time = calc_time(strat, race['race_config']['total_laps'],
                           race['race_config']['base_lap_time'],
                           race['race_config']['pit_lane_time'],
                           offsets, thresholds, rates)
            results.append((strat['driver_id'], time))
        results.sort(key=lambda x: x[1])
        pred = [r[0] for r in results]
        if pred == race['finishing_positions']:
            passed += 1
    return passed

# Try random params on simple races
best_score = 0
best_params = None

print("Searching for best params on simple races...")
for i in range(10000):
    params = [
        random.uniform(0.1, 3.0),
        random.uniform(0.5, 5.0),
        random.randint(1, 30),
        random.randint(5, 40),
        random.randint(10, 50),
        random.uniform(0.0001, 0.05),
        random.uniform(0.0001, 0.02),
        random.uniform(0.0001, 0.01),
    ]

    score = test_params(params, simple_races[:200])  # Test on subset

    if score > best_score:
        best_score = score
        best_params = params
        print(f"Iter {i}: Best = {score}/{len(simple_races[:200])}")

print(f"\nBest on simple: {best_score}/{len(simple_races[:200])}")
print(f"Params: {best_params}")
