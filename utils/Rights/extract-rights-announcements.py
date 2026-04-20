"""
extract_rights_announcements.py
--------------------------------
Reads rights_only.csv and keeps ONLY the primary issuance announcement —
the one that says "XYZ company is issuing / going to issue / has published
an offer letter to issue" a right share with a date range.

Excludes: closing notices, allotment, auction, book closure, distributing,
          deadline reminders, X days remaining, extensions, corrections, etc.

Output CSV columns: symbol, announcement_date, rights_ratio

Usage:
    python extract_rights_announcements.py                        # defaults
    python extract_rights_announcements.py input.csv output.csv  # custom
"""

import re
import sys
import pandas as pd

INPUT_FILE  = sys.argv[1] if len(sys.argv) > 1 else "rights_only.csv"
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "rights_announcements.csv"


# ── Step 1: Keep only primary issuance announcements ─────────────────────────

INCLUDE_PHRASES = [
    "is issuing",
    "is going to issue",
    "will issue",
    "has published an offer letter to issue",
    "has published a notice regarding issuance",
    "has published a notice regarding issue",         # older style
    "has published a notice regarding its.*right share issue",
    "is going to issue",
]

# These phrases disqualify a row even if an INCLUDE phrase matches
EXCLUDE_PHRASES = [
    "closing",
    "is closing",
    "from today",          # "opening from today" = opening day notice, not announcement
    "allot",
    "auction",
    "distribut",
    "certificate",
    "refund",
    "days remaining",
    "deadline",
    "extended",
    "correction",
    "postponed",
    "book closure",
    "is opening",          # opening day notice
    "is reissuing",
    "reissuing",
    "amended",
    "amendment",
    "re-published",
    "urge",
    "dmat",
    "call in advance",
    "advance amount",
    "unsold",
    "promoter right share",  # promoter-only auctions
    "bid opening",
    "collection center",
]


def is_primary_announcement(title: str) -> bool:
    if not isinstance(title, str):
        return False
    t = title.lower()

    # Must have at least one include phrase
    has_include = any(p in t for p in INCLUDE_PHRASES) or bool(
        re.search(r'has published a notice regarding its.*right share issue', t)
    )
    if not has_include:
        return False

    # Must NOT have any disqualifying phrase
    for phrase in EXCLUDE_PHRASES:
        if phrase in t:
            return False

    return True


# ── Step 2: Extract N:M ratio ─────────────────────────────────────────────────

def extract_ratio(title: str) -> str:
    if not isinstance(title, str):
        return ""
    m = re.search(r'\b(\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?)\b', title)
    return m.group(1).replace(" ", "") if m else ""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Reading : {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    required = {"symbol", "published_date", "title"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Filter to primary announcements
    mask = df["title"].apply(is_primary_announcement)
    ann_df = df[mask].copy()

    # Extract ratio, drop rows with no ratio found
    ann_df["rights_ratio"] = ann_df["title"].apply(extract_ratio)
    ann_df = ann_df[ann_df["rights_ratio"] != ""].copy()

    # Drop duplicates: keep first occurrence per symbol+date
    ann_df = ann_df.drop_duplicates(subset=["symbol", "published_date"], keep="first")

    # Build output
    out = ann_df[["symbol", "published_date", "rights_ratio"]].copy()
    out.rename(columns={"published_date": "announcement_date"}, inplace=True)
    out = out.sort_values(["symbol", "announcement_date"]).reset_index(drop=True)

    out.to_csv(OUTPUT_FILE, index=False)

    print(f"Total rows in input   : {len(df)}")
    print(f"Primary announcements : {len(out)}")
    print(f"Saved to              : {OUTPUT_FILE}")
    print()
    print(out.to_string())


if __name__ == "__main__":
    main()