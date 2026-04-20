"""
filter_rights_only.py
---------------------
Step 1: Filter your full announcements CSV down to ONLY rows
        that talk about right share issuance.

Input CSV columns expected: symbol, published_date, title

Usage:
    python filter_rights_only.py input.csv output_rights_only.csv
"""

import sys
import pandas as pd

INPUT_FILE  = sys.argv[1] if len(sys.argv) > 1 else "announcements.csv"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "rights_only.csv"

def is_rights_related(title: str) -> bool:
    if not isinstance(title, str):
        return False
    t = title.lower()
    return "right share" in t

df = pd.read_csv(INPUT_FILE)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

rights_df = df[df["title"].apply(is_rights_related)].copy()
rights_df.reset_index(drop=True, inplace=True)

print(f"Total rows        : {len(df)}")
print(f"Rights-only rows  : {len(rights_df)}")
print()
if not rights_df.empty:
    for _, row in rights_df.iterrows():
        print(f"[{row['symbol']}] {row['published_date']}")
        print(f"  {row['title']}")
        print()

rights_df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved to: {OUTPUT_FILE}")