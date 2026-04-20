"""
add_previous_ratio.py
----------------------
Takes rights_announcements.csv (symbol, announcement_date, rights_ratio)
and adds a previous_ratio column — the ratio from the most recent PRIOR
rights issue of the same stock.

If a stock has no earlier issue, previous_ratio is left blank.

Usage:
    python add_previous_ratio.py                            # defaults
    python add_previous_ratio.py input.csv output.csv      # custom
"""

import sys
import pandas as pd

INPUT_FILE  = sys.argv[1] if len(sys.argv) > 1 else "rights_announcements.csv"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "rights_with_previous.csv"

df = pd.read_csv(INPUT_FILE)
df["announcement_date"] = pd.to_datetime(df["announcement_date"])
df = df.sort_values(["symbol", "announcement_date"]).reset_index(drop=True)

# For each row, look back within the same symbol and grab the ratio of the
# immediately preceding row (i.e. the most recent earlier rights issue)
df["previous_ratio"] = (
    df.groupby("symbol")["rights_ratio"]
      .shift(1)           # shift down by 1 within each symbol group
)

# Format date back to string
df["announcement_date"] = df["announcement_date"].dt.strftime("%Y-%m-%d")

df.to_csv(OUTPUT_FILE, index=False)
print(f"Done. {len(df)} rows saved to {OUTPUT_FILE}")
print()
print(df.to_string())