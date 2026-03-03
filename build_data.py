#!/usr/bin/env python3
"""
Rebuild Powerball dataset from NY Open Data.
Adds actual numbers, recomputes combo indices, preserves hasWinner flags.
"""

import json
import urllib.request
import re
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

# --- Load existing hasWinner data from the HTML file ---
print("Loading existing winner flags from HTML...")
with open('index.html', 'r') as f:
    content = f.read()

# Extract all {date, hasWinner} pairs from existing data
existing_winners = {}
pattern = r'"date":\s*"([^"]+)"[^}]*"hasWinner":\s*(true|false)'
for m in re.finditer(pattern, content):
    date = m.group(1)
    has_winner = m.group(2) == 'true'
    existing_winners[date] = has_winner

print(f"  Found {len(existing_winners)} existing draws with winner flags")
print(f"  Winners: {sum(existing_winners.values())}")

# New jackpot winners in the gap period
new_winners = {
    '2025-12-24': True,  # $1.8B Arkansas
    '2026-01-21': True,  # $209.3M North Carolina
}

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
    
    # Determine hasWinner
    if date in new_winners:
        has_winner = new_winners[date]
    elif date in existing_winners:
        has_winner = existing_winners[date]
    else:
        has_winner = False  # Default for unknown
    
    data.append({
        'date': date,
        'numbers': sorted(whites),
        'powerball': pb,
        'comboIndex': idx,
        'hasWinner': has_winner
    })

print(f"  Built {len(data)} draws (skipped {skipped})")
print(f"  Date range: {data[0]['date']} to {data[-1]['date']}")
print(f"  Jackpot winners: {sum(d['hasWinner'] for d in data)}")

# Verify our known winners are in the data
for date, expected in {**existing_winners, **new_winners}.items():
    if expected:
        match = [d for d in data if d['date'] == date and d['hasWinner']]
        if match:
            print(f"  ✓ Winner on {date}: {match[0]['numbers']} PB:{match[0]['powerball']}")

# Save as JSON for inspection
with open('powerball_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f"\nSaved to powerball_data.json")
print(f"Total combo space: 292,201,338")
print(f"Combo index range in data: {min(d['comboIndex'] for d in data):,} - {max(d['comboIndex'] for d in data):,}")
