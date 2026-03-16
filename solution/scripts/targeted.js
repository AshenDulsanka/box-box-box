/**
 * TARGETED SOLVER - Correct tire age model (starts at 1, not 0)
 * 
 * From regulations:
 * "At the start of each lap, tire age increments by 1 before calculating lap time"
 * "The first lap on fresh tires is driven at age 1"
 * 
 * So tire age = laps completed on this compound including CURRENT lap
 * - Lap 1 of stint: age = 1
 * - Lap 2 of stint: age = 2
 * - etc.
 * 
 * Degradation per lap = rate * max(0, age - threshold)
 * Total degradation for a stint of L laps:
 *   = rate * TF * sum_{age=1}^{L} max(0, age - threshold)
 *   = rate * TF * sum_{k=threshold+1}^{L} (k - threshold)
 *   = rate * TF * triangularSumNew(L, threshold)
 * 
 * where triangularSumNew(L, T) = sum_{j=1}^{L-T} j = (L-T)(L-T+1)/2  [when L > T]
 * 
 * Also test: maybe "starting position" (pos number) acts as tiny tiebreaker
 * via a position-based time offset like:
 *   total_time += starting_grid_position * 0.001 seconds
 * This would keep start order for identical strategies without affecting 
 * strategy comparisons (since positions differ by at most 19 * 0.001 = 0.019s)
 */
'use strict';
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', '..', 'data', 'historical_races');

function loadBatches(n) {
  const races = [];
  for (let i = 0; i < n; i++) {
    const start = i * 1000;
    const end = start + 999;
    const file = `races_${String(start).padStart(5, '0')}-${String(end).padStart(5, '0')}.json`;
    races.push(...JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf-8')));
  }
  return races;
}

// NEW: tire age starts at 1
function triangularSumV2(laps, threshold) {
  // sum_{k=1}^{L} max(0, k - T) = sum_{k=T+1}^{L} (k-T) = sum_{j=1}^{L-T} j = (L-T)(L-T+1)/2
  const n = laps - threshold;
  if (n <= 0) return 0;
  return n * (n + 1) / 2;
}

// Preprocess for faster computation
function preprocessRaces(races) {
  return races.map(race => {
    const { total_laps: N, base_lap_time, pit_lane_time, track_temp } = race.race_config;
    
    const drivers = Object.values(race.strategies).map((s, idx) => {
      const stints = [];
      let compound = s.starting_tire;
      let start = 1;
      for (const pit of s.pit_stops) {
        stints.push({ compound, laps: pit.lap - start + 1 });
        compound = pit.to_tire;
        start = pit.lap + 1;
      }
      stints.push({ compound, laps: N - start + 1 });
      
      const baseTime = N * base_lap_time + s.pit_stops.length * pit_lane_time;
      const gridPos = idx + 1; // pos1=1, pos2=2, etc.
      
      return { driver_id: s.driver_id, stints, baseTime, gridPos };
    });
    
    return { track_temp, drivers, expected: race.finishing_positions };
  });
}

console.log('Loading races...');
const t0 = Date.now();
const races = loadBatches(30);
console.log('Loaded:', races.length, 'in', ((Date.now()-t0)/1000).toFixed(1), 's');

console.log('Preprocessing...');
const processed = preprocessRaces(races);
console.log('Done in', ((Date.now()-t0)/1000).toFixed(1), 's');

// Test tiebreaker in historical data
// Check if start order preserved for identical strategies
function testTiebreakerInHistorical() {
  let total = 0, preserved = 0;
  for (const race of processed.slice(0, 200)) {
    const stratKeys = {};
    for (const d of race.drivers) {
      const key = d.stints.map(s => `${s.compound}:${s.laps}`).join('|');
      if (!stratKeys[key]) stratKeys[key] = [];
      stratKeys[key].push(d);
    }
    for (const [key, drvs] of Object.entries(stratKeys).filter(([k, v]) => v.length > 1)) {
      const sortedByStart = [...drvs].sort((a, b) => a.gridPos - b.gridPos);
      const sortedByFinish = [...drvs].sort((a, b) => {
        return race.expected.indexOf(a.driver_id) - race.expected.indexOf(b.driver_id);
      });
      for (let i = 0; i < drvs.length; i++) {
        total++;
        if (sortedByStart[i].driver_id === sortedByFinish[i].driver_id) preserved++;
      }
    }
  }
  console.log(`Tiebreaker check (200 historical races): ${preserved}/${total} = ${(preserved/total*100).toFixed(1)}%`);
}
testTiebreakerInHistorical();

// Fast test function with grid pos tiebreaker
function testParams(p, raceData) {
  const { oS, oM, oH, tS, tM, tH, rS, rM, rH, tb, tc } = p;
  let passed = 0;
  
  for (const race of raceData) {
    const { track_temp, drivers, expected } = race;
    const TF = tc === 0 ? 1 : 1 + Math.max(0, track_temp - tb) * tc;
    
    const times = drivers.map(d => {
      let adj = 0;
      for (const { compound, laps } of d.stints) {
        let off, thresh, rate;
        if (compound === 'SOFT') { off = oS; thresh = tS; rate = rS; }
        else if (compound === 'MEDIUM') { off = oM; thresh = tM; rate = rM; }
        else { off = oH; thresh = tH; rate = rH; }
        
        adj += laps * off + rate * TF * triangularSumV2(laps, thresh);
      }
      // Grid position tiebreaker (tiny offset to preserve start order for ties)
      return { id: d.driver_id, t: d.baseTime + adj + d.gridPos * 0.0001 };
    });
    
    times.sort((a, b) => a.t - b.t);
    
    let ok = true;
    for (let i = 0; i < times.length; i++) {
      if (times[i].id !== expected[i]) { ok = false; break; }
    }
    if (ok) passed++;
  }
  return passed;
}

// Focused search informed by regulations + what we know
console.log('\n=== Focused search with V2 tire age model ===');

const search = {
  oS: [0],
  oM: [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0],
  oH: [0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0],
  tS: [0, 1, 2, 3, 5, 8, 10],
  tM: [3, 5, 8, 10, 12, 15, 20, 25],
  tH: [5, 8, 10, 15, 20, 25, 30, 40],
  rS: [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20],
  rM: [0.005, 0.008, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08],
  rH: [0.001, 0.002, 0.005, 0.008, 0.01, 0.015, 0.02, 0.03],
  tb: [15, 20, 22, 25, 28, 30],
  tc: [0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05],
};

const validationSet = processed.slice(0, 300);
const total = Object.values(search).reduce((a, b) => a * b.length, 1);
console.log(`Searching ${total.toLocaleString()} combinations...`);

let bestAcc = 0, bestP = null, iter = 0;
const t1 = Date.now();

outer:
for (const oS of search.oS) {
  for (const oM of search.oM) {
    for (const oH of search.oH) {
      if (oH <= oM) continue;
      for (const tS of search.tS) {
        for (const tM of search.tM) {
          for (const tH of search.tH) {
            for (const rS of search.rS) {
              for (const rM of search.rM) {
                for (const rH of search.rH) {
                  for (const tb of search.tb) {
                    for (const tc of search.tc) {
                      iter++;
                      const p = { oS, oM, oH, tS, tM, tH, rS, rM, rH, tb, tc };
                      const acc = testParams(p, validationSet) / validationSet.length;
                      if (acc > bestAcc) {
                        bestAcc = acc;
                        bestP = { ...p };
                        const el = ((Date.now()-t1)/1000).toFixed(1);
                        console.log(`  [${iter}] ${(acc*100).toFixed(1)}% → off=(${oS},${oM},${oH}) t=(${tS},${tM},${tH}) r=(${rS},${rM},${rH}) temp=(${tb},${tc}) [${el}s]`);
                        if (acc >= 1.0) { console.log('PERFECT!'); break outer; }
                      }
                      if (iter % 200000 === 0) {
                        const el = ((Date.now()-t1)/1000).toFixed(1);
                        console.log(`  Progress: ${iter.toLocaleString()} [${el}s] best=${(bestAcc*100).toFixed(1)}%`);
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

console.log('\nBest accuracy (300 races):', (bestAcc*100).toFixed(2) + '%');
console.log('Best params:', JSON.stringify(bestP, null, 2));

if (bestP) {
  const allAcc = testParams(bestP, processed) / processed.length;
  console.log(`All 30k races accuracy: ${(allAcc*100).toFixed(2)}%`);
}
