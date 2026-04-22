"""
map_dates.py
-------------
Maps announcement/report dates onto eps.csv and bvps.csv.

Announcement file columns:
  Symbol, Quarter(1st/2nd/3rd/4th), BS_Fiscal_Year, AD_Year,
  AD_Fiscal_Year, Full_Company_Name, Report_Date(Mon DD, YYYY)

NOTE: Report_Date contains a comma so the file has 8 actual columns.
      A header row is auto-detected and handled correctly.

Match key:  symbol + quarter(Q1-Q4) + AD_Fiscal_Year
  matches   symbol + quarter        + year   in eps/bvps

Duplicates: if same key appears multiple times, earliest date is kept.
No match:   date column stays blank.

Usage:
    python map_dates.py announcements.csv eps.csv bvps.csv [eps_out.csv] [bvps_out.csv]
    python map_dates.py announcements.csv          # uses default paths
"""

import sys
import pandas as pd

ANN_FILE  = sys.argv[1] if len(sys.argv) > 1 else 'announcements.csv'
EPS_FILE  = sys.argv[2] if len(sys.argv) > 2 else 'eps.csv'
BVPS_FILE = sys.argv[3] if len(sys.argv) > 3 else 'bvps.csv'
EPS_OUT   = sys.argv[4] if len(sys.argv) > 4 else 'eps_with_dates.csv'
BVPS_OUT  = sys.argv[5] if len(sys.argv) > 5 else 'bvps_with_dates.csv'

QUARTER_MAP = {'1st': 'Q1', '2nd': 'Q2', '3rd': 'Q3', '4th': 'Q4'}

COL_NAMES = ['symbol', 'quarter_raw', 'bs_fiscal', 'ad_year',
             'ad_fiscal', 'company', 'date_str']

# ── Load announcement file ────────────────────────────────────────────────────
# Auto-detect header row by checking if first line looks like column names
with open(ANN_FILE, 'r', encoding='utf-8') as f:
    first_line = f.readline().strip().lower()

has_header = (
    first_line.startswith('symbol') or
    'fiscal' in first_line or
    'quarter' in first_line or
    'report' in first_line
)

ann = pd.read_csv(
    ANN_FILE,
    header=0 if has_header else None,
    names=COL_NAMES,
    skiprows=1 if has_header else 0,
    engine='python'
)

print(f"Header detected    : {has_header}")
print(f"Raw rows loaded    : {len(ann)}")

# ── Parse date ────────────────────────────────────────────────────────────────
ann['date'] = pd.to_datetime(ann['date_str'], format='%b %d, %Y', errors='coerce')

# ── Normalise ─────────────────────────────────────────────────────────────────
ann['symbol']    = ann['symbol'].astype(str).str.strip()
ann['ad_fiscal'] = ann['ad_fiscal'].astype(str).str.strip()
ann['quarter']   = (ann['quarter_raw'].astype(str).str.strip().str.lower()
                                      .map(QUARTER_MAP))

# Drop rows with unparseable quarter or date
ann = ann.dropna(subset=['quarter', 'date'])

# Deduplicate: keep earliest date per (symbol, quarter, ad_fiscal)
ann = (ann.sort_values('date')
          .drop_duplicates(subset=['symbol', 'quarter', 'ad_fiscal'], keep='first'))

# ── Build lookup: (symbol, quarter, ad_fiscal) → date string ─────────────────
date_lookup = {
    (r['symbol'], r['quarter'], r['ad_fiscal']): r['date'].strftime('%Y-%m-%d')
    for _, r in ann.iterrows()
}

print(f"Announcement rows  : {len(ann)}")
print(f"Unique date keys   : {len(date_lookup)}")
print()

# ── Fill dates into eps and bvps ──────────────────────────────────────────────
# Q4 reports in the NEXT fiscal year's announcement, Q1-Q3 use SAME fiscal year
def get_fy_for_quarter(year_str, quarter):
    """Get the fiscal year to look up in announcements"""
    year_str = str(year_str).strip()
    if not year_str or year_str == 'nan':
        return year_str
    if '/' not in year_str:
        return year_str
    
    parts = year_str.split('/')
    if len(parts) != 2:
        return year_str
    
    start_yr = int(parts[0])
    end_yr = int(parts[1])
    
    # Q4 uses next year's announcement
    if quarter == 'Q4':
        next_start = start_yr + 1
        next_end = end_yr + 1
        return f"{next_start:02d}/{next_end:02d}"
    # Q1-Q3 use same year
    return year_str

def fill_dates(df):
    df = df.copy()
    df['date'] = df.apply(
        lambda r: date_lookup.get((str(r['symbol']).strip(),
                                   str(r['quarter']).strip(),
                                   get_fy_for_quarter(r['year'], r['quarter'])), ''),
        axis=1
    )
    return df

eps  = pd.read_csv(EPS_FILE)
bvps = pd.read_csv(BVPS_FILE)

eps_out  = fill_dates(eps)
bvps_out = fill_dates(bvps)

# Sort output chronologically by symbol, year, quarter
QUARTER_ORDER = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}

def sort_chronologically(df):
    df = df.copy()
    df['_q_order'] = df['quarter'].map(QUARTER_ORDER)
    df = df.sort_values(['symbol', 'year', '_q_order'])
    df = df.drop('_q_order', axis=1)
    return df

eps_out  = sort_chronologically(eps_out)
bvps_out = sort_chronologically(bvps_out)

# ── Save ──────────────────────────────────────────────────────────────────────
eps_out.to_csv(EPS_OUT,  index=False)
bvps_out.to_csv(BVPS_OUT, index=False)

eps_matched  = (eps_out['date'].astype(str).str.strip() != '').sum()
bvps_matched = (bvps_out['date'].astype(str).str.strip() != '').sum()

print(f"EPS  : {eps_matched}/{len(eps_out)} rows matched  → {EPS_OUT}")
print(f"BVPS : {bvps_matched}/{len(bvps_out)} rows matched → {BVPS_OUT}")
print()
print("=== eps_with_dates.csv ===")
print(eps_out.to_string(index=False))
print()
print("=== bvps_with_dates.csv ===")
print(bvps_out.to_string(index=False))