#!/usr/bin/env python3
"""
Auto-tuner using scipy differential_evolution.
"""

import json
import numpy as np
from scipy.optimize import differential_evolution
import subprocess
import time

DATA_DIR = 'data/test_cases'

# Fixed cliffs (do not tune)
CLIFF = {
    'SOFT': 10,
    'MEDIUM': 20,
    'HARD': 30,
}

# Load all test cases
print("Loading test cases...")
test_cases = []
for i in range(1, 101):
    with open(f'{DATA_DIR}/inputs/test_{i:03d}.json') as f:
        inp = json.load(f)
    with open(f'{DATA_DIR}/expected_outputs/test_{i:03d}.json') as f:
        exp = json.load(f)
    test_cases.append((i, inp, exp))

print(f"Loaded {len(test_cases)} test cases")


def simulate_race(race_config, strategies, params):
    """Simulate race with given params."""
    base_lap_time = race_config['base_lap_time']
    track_temp = race_config['track_temp']
    total_laps = race_config['total_laps']
    pit_lane_time = race_config['pit_lane_time']

    # Unpack params
    temp_coef, fuel_burn, warmup_penalty = params[0:3]
    soft_offset, soft_deg = params[3:5]
    med_offset, med_deg = params[5:7]
    hard_offset, hard_deg = params[7:9]

    offsets = {'SOFT': soft_offset, 'MEDIUM': med_offset, 'HARD': hard_offset}
    degrades = {'SOFT': soft_deg, 'MEDIUM': med_deg, 'HARD': hard_deg}

    driver_times = []

    for strat in strategies.values():
        driver_id = strat['driver_id']
        starting_tire = strat['starting_tire']
        pit_stops = strat['pit_stops']

        pit_map = {p['lap']: p['to_tire'] for p in pit_stops}

        total_time = 0
        current_tire = starting_tire
        tire_age = 0

        for lap in range(1, total_laps + 1):
            tire_age += 1

            lap_time = base_lap_time
            lap_time += offsets[current_tire]
            deg_factor = degrades[current_tire] * (1 + track_temp * temp_coef)
            deg_penalty = deg_factor * max(0, tire_age - CLIFF[current_tire])
            lap_time += deg_penalty
            lap_time += fuel_burn * (lap - 1)

            if tire_age == 1:
                lap_time += warmup_penalty

            total_time += lap_time

            if lap in pit_map:
                total_time += pit_lane_time
                current_tire = pit_map[lap]
                tire_age = 0

        driver_times.append((driver_id, total_time))

    driver_times.sort(key=lambda x: x[1])
    return [d for d, _ in driver_times]


def score_params(params):
    """Score params on all test cases. Returns negative score for minimization."""
    passed = 0

    for test_id, inp, exp in test_cases:
        pred = simulate_race(inp['race_config'], inp['strategies'], params)
        if pred == exp['finishing_positions']:
            passed += 1

    return -passed  # Negative because we minimize


# Bounds as specified
# [temp_coef, fuel_burn, warmup_penalty, soft_offset, soft_deg, med_offset, med_deg, hard_offset, hard_deg]
bounds = [
    (0.05, 0.15),       # temp_coef
    (-0.005, 0.0),      # fuel_burn
    (0.0, 3.0),         # warmup_penalty
    (2.5, 3.5),         # soft_offset
    (0.30, 0.55),       # soft_deg
    (3.5, 4.5),         # med_offset
    (0.15, 0.28),       # med_deg
    (4.2, 5.2),         # hard_offset
    (0.08, 0.15),       # hard_deg
]

print("Starting differential evolution...")
print(f"Bounds: {bounds}")
print()

best_score = 0
best_params = None
best_iteration = 0

def callback(xk, convergence):
    global best_score, best_params, best_iteration

    # Score current params
    score = -score_params(xk)

    if score > best_score:
        best_score = score
        best_params = xk
        best_iteration = callback.iteration if hasattr(callback, 'iteration') else 0

        print(f"NEW BEST: {score}/100 at iteration {callback.iteration if hasattr(callback, 'iteration') else 0}")
        print(f"  temp_coef={xk[0]:.6f}, fuel_burn={xk[1]:.6f}, warmup_penalty={xk[2]:.4f}")
        print(f"  soft: offset={xk[3]:.4f}, deg={xk[4]:.4f}")
        print(f"  med:  offset={xk[5]:.4f}, deg={xk[6]:.4f}")
        print(f"  hard: offset={xk[7]:.4f}, deg={xk[8]:.4f}")
        print()

    callback.iteration += 1
    return False

callback.iteration = 0

# Run differential evolution
start_time = time.time()
result = differential_evolution(
    score_params,
    bounds,
    maxiter=200,
    popsize=10,
    tol=0.001,
    mutation=(0.5, 1),
    recombination=0.7,
    callback=callback,
    workers=1,
    updating='deferred',
    seed=42,
)

elapsed = time.time() - start_time
print(f"\nOptimization completed in {elapsed:.1f} seconds")
print(f"Best score: {best_score}/100")
print(f"Best params: {best_params}")
