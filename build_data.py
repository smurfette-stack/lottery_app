#!/usr/bin/env python3
"""
Rebuild Powerball dataset from NY Open Data.
Adds actual numbers, recomputes combo indices, preserves hasWinner flags.
"""

import json
import urllib.request
from math import comb

# --- Combo index calculation ---
# Powerball: 5 white balls from 1-69, 1 red ball from 1-26
# Total combinations: C(69,5) * 26 = 292,201,338
# 
# Combinatorial number system (0-based sorted white balls):
# index = C(b5-1,5) + C(b4-1,4) + C(b3-1,3) + C(b2-1,2) + C(b1-1,1)  [0-indexed]
# Then total_index = white_index * 26 + (powerball - 1)

def combo_index(numbers, powerball):
    """Calculate the unique combo index for a Powerball draw (post Oct 2015 format)."""
    # Sort white balls, convert to 0-indexed
    whites = sorted([n - 1 for n in numbers])
    b1, b2, b3, b4, b5 = whites
    white_index = comb(b5, 5) + comb(b4, 4) + comb(b3, 3) + comb(b2, 2) + comb(b1, 1)
    return white_index * 26 + (powerball - 1)

# --- Load hasWinner data from Texas Lottery (authoritative source) ---
print("Loading winner flags from Texas Lottery data...")
with open('texas_winners.json', 'r') as f:
    texas_winners = json.load(f)

print(f"  Loaded {len(texas_winners)} draws from Texas Lottery")
print(f"  Winners: {sum(texas_winners.values())}")

# Manually patched draws missing from NY Open Data
# 2022-11-07: $2.04B record jackpot — not in NY dataset
manual_draws = [
    {'date': '2022-11-07', 'numbers': [10, 33, 41, 47, 56], 'powerball': 10, 'hasWinner': True},
]

# --- Fetch all draws from NY Open Data (from Oct 2015 onwards) ---
print("\nFetching data from NY Open Data...")
url = "https://data.ny.gov/resource/d6yy-54nr.json?$limit=5000&$where=draw_date>='2015-10-07T00:00:00'&$order=draw_date+ASC"
with urllib.request.urlopen(url) as response:
    raw = json.loads(response.read().decode())

print(f"  Fetched {len(raw)} draws from NY Open Data")

# --- Build new dataset ---
print("\nBuilding new dataset...")
data = []
skipped = 0
for row in raw:
    date = row['draw_date'][:10]  # YYYY-MM-DD
    nums_raw = row['winning_numbers'].split()
    
    # NY Data format: "n1 n2 n3 n4 n5 powerball"
    if len(nums_raw) != 6:
        print(f"  WARNING: unexpected format for {date}: {row['winning_numbers']}")
        skipped += 1
        continue
    
    whites = [int(n) for n in nums_raw[:5]]
    pb = int(nums_raw[5])
    
    # Validate ranges (post Oct 2015 format: 1-69 white, 1-26 PB)
    if not all(1 <= n <= 69 for n in whites) or not (1 <= pb <= 26):
        print(f"  SKIPPING {date}: out-of-range numbers {whites} PB:{pb} (pre-format-change draw)")
        skipped += 1
        continue
    
    # Compute combo index
    idx = combo_index(whites, pb)
    
    # Determine hasWinner from Texas Lottery data
    has_winner = texas_winners.get(date, False)
    
    data.append({
        'date': date,
        'numbers': sorted(whites),
        'powerball': pb,
        'comboIndex': idx,
        'hasWinner': has_winner
    })

# Add manually patched draws
for m in manual_draws:
    if not any(d['date'] == m['date'] for d in data):
        idx = combo_index(m['numbers'], m['powerball'])
        data.append({**m, 'comboIndex': idx})
        print(f"  + Manual patch: {m['date']} {m['numbers']} PB:{m['powerball']} winner:{m['hasWinner']}")

data.sort(key=lambda d: d['date'])
print(f"  Built {len(data)} draws (skipped {skipped})")
print(f"  Date range: {data[0]['date']} to {data[-1]['date']}")
print(f"  Jackpot winners: {sum(d['hasWinner'] for d in data)}")

# Verify some known winners are in the data
known_winners = {'2025-12-24', '2026-01-21', '2016-01-13', '2022-11-07'}
for date in known_winners:
    match = [d for d in data if d['date'] == date and d['hasWinner']]
    if match:
        print(f"  ✓ Winner on {date}: {match[0]['numbers']} PB:{match[0]['powerball']}")
    else:
        print(f"  ✗ Missing winner on {date}")

# Save as JSON for inspection
with open('powerball_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f"\nSaved to powerball_data.json")
print(f"Total combo space: 292,201,338")
print(f"Combo index range in data: {min(d['comboIndex'] for d in data):,} - {max(d['comboIndex'] for d in data):,}")
