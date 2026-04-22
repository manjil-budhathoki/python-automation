"""
create_eps_bvps.py
-------------------
Reads ALL CSV files from a folder and produces just TWO output files
containing every stock combined:

  eps.csv
    symbol | date | eps_actual | eps_previous | quarter | year

  bvps.csv
    symbol | date | book_value_per_share_actual | book_value_per_share_previous | quarter | year

Symbol is derived from the filename:
  ACLBSL.csv        -> ACLBSL
  BFC_key-stats.csv -> BFC
  ahl.csv           -> AHL  (uppercased)

- actual   = value for that row's quarter/year
- previous = value from the immediately preceding quarter chronologically
             (Q1 previous = Q4 of prior year; Q2 previous = Q1 same year; etc.)
- date     = left empty (unknown)
- year     = fiscal year string e.g. '2025/26'
- quarter  = Q1 / Q2 / Q3 / Q4

Usage:
    python create_eps_bvps.py /path/to/folder
    python create_eps_bvps.py /path/to/folder /path/to/output_folder
"""

import os
import sys
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
INPUT_FOLDER  = sys.argv[1] if len(sys.argv) > 1 else '.'
OUTPUT_FOLDER = sys.argv[2] if len(sys.argv) > 2 else INPUT_FOLDER

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

EPS_FILE  = os.path.join(OUTPUT_FOLDER, 'eps.csv')
BVPS_FILE = os.path.join(OUTPUT_FOLDER, 'bvps.csv')

QUARTER_ORDER = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}


# ── Helpers ────────────────────────────────────────────────────────────────────

def symbol_from_filename(fname):
    """ACLBSL.csv -> ACLBSL  |  BFC_key-stats.csv -> BFC  |  ahl.csv -> AHL"""
    name = os.path.splitext(fname)[0]
    symbol = name.split('_')[0]
    return symbol.upper()


def clean_value(v):
    """'(7.08)' -> -7.08  |  '-' or blank -> NaN  |  '32.57' -> 32.57"""
    if pd.isna(v) or str(v).strip() in ('', '-', 'nan'):
        return np.nan
    s = str(v).strip().replace(',', '')
    if s.startswith('(') and s.endswith(')'):
        s = '-' + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return np.nan


def process_file(filepath, symbol):
    df = pd.read_csv(filepath, header=0)

    quarters_row = df.iloc[0]
    key_col      = df.columns[0]

    eps_matches  = df[df[key_col].astype(str).str.contains('EPS',                 case=False, na=False)]
    bvps_matches = df[df[key_col].astype(str).str.contains('Book Value per Share', case=False, na=False)]

    if eps_matches.empty or bvps_matches.empty:
        print(f"  WARNING: Could not find EPS or BVPS rows -- skipping")
        return None, None

    eps_row  = eps_matches.iloc[0]
    bvps_row = bvps_matches.iloc[0]

    records = []
    for col in df.columns[1:]:
        year    = col.split('.')[0]
        quarter = str(quarters_row[col]).strip()
        if quarter not in QUARTER_ORDER:
            continue
        records.append({
            'year'    : year,
            'quarter' : quarter,
            'eps'     : clean_value(eps_row[col]),
            'bvps'    : clean_value(bvps_row[col]),
        })

    if not records:
        print(f"  WARNING: No valid quarter data found -- skipping")
        return None, None

    flat = pd.DataFrame(records)
    flat['q_order'] = flat['quarter'].map(QUARTER_ORDER)
    flat = flat.sort_values(['year', 'q_order']).reset_index(drop=True)

    flat['eps_prev']  = flat['eps'].shift(1)
    flat['bvps_prev'] = flat['bvps'].shift(1)

    eps_df = pd.DataFrame({
        'symbol'       : symbol,
        'date'         : '',
        'eps_actual'   : flat['eps'],
        'eps_previous' : flat['eps_prev'],
        'quarter'      : flat['quarter'],
        'year'         : flat['year'],
    })

    bvps_df = pd.DataFrame({
        'symbol'                        : symbol,
        'date'                          : '',
        'book_value_per_share_actual'   : flat['bvps'],
        'book_value_per_share_previous' : flat['bvps_prev'],
        'quarter'                       : flat['quarter'],
        'year'                          : flat['year'],
    })

    return eps_df, bvps_df


# ── Main ──────────────────────────────────────────────────────────────────────
csv_files = sorted([f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.csv')])

if not csv_files:
    print(f"No CSV files found in: {INPUT_FOLDER}")
    sys.exit(1)

print(f"Found {len(csv_files)} CSV file(s) in '{INPUT_FOLDER}'")
print()

all_eps  = []
all_bvps = []

for fname in csv_files:
    filepath = os.path.join(INPUT_FOLDER, fname)
    symbol   = symbol_from_filename(fname)
    print(f"  {fname}  ->  {symbol}")
    eps_df, bvps_df = process_file(filepath, symbol)
    if eps_df is None:
        continue
    print(f"     {len(eps_df)} rows")
    all_eps.append(eps_df)
    all_bvps.append(bvps_df)

if not all_eps:
    print("\nNo data extracted -- check your files have EPS and Book Value per Share rows.")
    sys.exit(1)

eps_combined  = pd.concat(all_eps,  ignore_index=True)
bvps_combined = pd.concat(all_bvps, ignore_index=True)

eps_combined.to_csv(EPS_FILE,  index=False)
bvps_combined.to_csv(BVPS_FILE, index=False)

print()
print(f"Saved: eps.csv  -- {len(eps_combined)} rows, {eps_combined['symbol'].nunique()} symbol(s)")
print(f"Saved: bvps.csv -- {len(bvps_combined)} rows, {bvps_combined['symbol'].nunique()} symbol(s)")
print("Done.")