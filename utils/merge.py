"""
merge_and_clean.py
==================
1. Reads  dividend.csv   (symbol, announcement_date, total_dividend, distribution_date)
2. Reads  complete.csv   (symbol, Announcement Date, Total Dividend)
3. Cleans dividend.csv:
   - Drops the distribution_date column
   - Fixes rows where announcement_date is corrupt/missing/wrong
   - Fills every remaining NaN announcement_date by matching
     (symbol + total_dividend) against complete.csv
4. Outputs a clean 3-column CSV: symbol, announcement_date, total_dividend

Usage:
    python merge_and_clean.py
    python merge_and_clean.py dividend.csv complete.csv merged_output.csv
"""

import sys
import re
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
raw_path      = sys.argv[1] if len(sys.argv) > 1 else "dividend.csv"
complete_path = sys.argv[2] if len(sys.argv) > 2 else "complete.csv"
out_path      = sys.argv[3] if len(sys.argv) > 3 else "merged_output.csv"

print(f"\n  Reading raw      : {raw_path}")
print(f"  Reading complete : {complete_path}")
print(f"  Writing output   : {out_path}")


# ── Helper: safely parse a number that may have commas e.g. "1,270.00" ────────
def parse_number(val):
    """Convert '1,270.00' or '12.50' or NaN to float, or None if unparseable."""
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


# ── Helper: check if a value looks like a real date ───────────────────────────
DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}$"
    r"|^\d{1,2}/\d{1,2}/\d{2,4}$"
    r"|^\w{3}\s+\d{1,2},\s*\d{4}$"
)

def is_valid_date(val):
    if pd.isna(val):
        return False
    return bool(DATE_RE.match(str(val).strip()))


# ── Load everything as strings to avoid pandas mangling commas ────────────────
df_raw  = pd.read_csv(raw_path,      dtype=str)
df_comp = pd.read_csv(complete_path, dtype=str)

df_raw.columns  = [c.strip() for c in df_raw.columns]
df_comp.columns = [c.strip() for c in df_comp.columns]

df_comp = df_comp.rename(columns={
    "Announcement Date": "announcement_date",
    "Total Dividend":    "total_dividend",
})

print(f"  Raw columns      : {df_raw.columns.tolist()}")
print(f"  Complete columns : {df_comp.columns.tolist()}")


# ── Step 1 – Drop distribution_date ───────────────────────────────────────────
if "distribution_date" in df_raw.columns:
    df_raw = df_raw.drop(columns=["distribution_date"])
    print("  Dropped  distribution_date  column")

df_raw = df_raw[["symbol", "announcement_date", "total_dividend"]].copy()


# ── Step 2 – Parse total_dividend safely (handles commas) ─────────────────────
df_raw["_total_num"]  = df_raw["total_dividend"].apply(parse_number)
df_comp["_total_num"] = df_comp["total_dividend"].apply(parse_number)

unparseable = df_raw["_total_num"].isna().sum()
if unparseable:
    print(f"  WARNING: {unparseable} rows had unparseable total_dividend values")


# ── Step 3 – Blank out bad announcement_dates ─────────────────────────────────
bad_mask  = ~df_raw["announcement_date"].apply(is_valid_date)
bad_count = bad_mask.sum()
print(f"  Found {bad_count} rows with missing/corrupt announcement_date")
df_raw.loc[bad_mask, "announcement_date"] = pd.NA


# ── Step 4 – Build lookup: (symbol, rounded_total) -> first known date ────────
df_comp["_key_total"] = df_comp["_total_num"].apply(
    lambda x: round(x, 2) if x is not None else None
)
df_raw["_key_total"] = df_raw["_total_num"].apply(
    lambda x: round(x, 2) if x is not None else None
)

comp_dated   = df_comp[df_comp["announcement_date"].apply(is_valid_date)].copy()
comp_lookup  = (
    comp_dated
    .dropna(subset=["_key_total"])
    .groupby(["symbol", "_key_total"])["announcement_date"]
    .first()
    .to_dict()
)


# ── Step 5 – Fill missing dates ───────────────────────────────────────────────
filled        = 0
still_missing = 0

for idx, row in df_raw.iterrows():
    if pd.isna(row["announcement_date"]):
        key_total = row["_key_total"]
        if key_total is not None:
            date = comp_lookup.get((row["symbol"], key_total))
            if date:
                df_raw.at[idx, "announcement_date"] = date
                filled += 1
                continue
        still_missing += 1

print(f"  Filled  {filled} dates  from complete.csv")
if still_missing:
    print(f"  {still_missing} rows still have no date (not in complete.csv)")


# ── Step 6 – Final tidy-up ────────────────────────────────────────────────────
df_raw = df_raw.drop(columns=["_key_total", "_total_num"])

def normalise_date(val):
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return ""
    try:
        return pd.to_datetime(str(val)).strftime("%Y-%m-%d")
    except Exception:
        return str(val).strip()

df_raw["announcement_date"] = df_raw["announcement_date"].apply(normalise_date)

def clean_total(val):
    n = parse_number(val)
    return round(n, 4) if n is not None else ""

df_raw["total_dividend"] = df_raw["total_dividend"].apply(clean_total)


# ── Save ──────────────────────────────────────────────────────────────────────
df_raw.to_csv(out_path, index=False)


# ── Summary ───────────────────────────────────────────────────────────────────
total          = len(df_raw)
has_date       = (df_raw["announcement_date"] != "").sum()
no_date        = total - has_date
unique_symbols = df_raw["symbol"].nunique()

print(f"\n{'─'*52}")
print(f"  Output saved  ->  {out_path}")
print(f"{'─'*52}")
print(f"  Total rows        : {total}")
print(f"  Unique symbols    : {unique_symbols}")
print(f"  Rows with date    : {has_date}")
print(f"  Rows without date : {no_date}  (no date source found)")
print(f"{'─'*52}")

if no_date > 0:
    missing_df = df_raw[df_raw["announcement_date"] == ""][["symbol", "total_dividend"]]
    print(f"\n  Rows still missing a date:")
    for _, r in missing_df.iterrows():
        print(f"    {r['symbol']:<14}  total={r['total_dividend']}")

print()