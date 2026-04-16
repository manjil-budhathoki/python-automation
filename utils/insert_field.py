import pandas as pd

# Load both files
book_df = pd.read_csv("book_value.csv")
bvps_df = pd.read_csv("sorted_output.csv")

# Rename for matching
bvps_df = bvps_df.rename(columns={
    "stock_symbol": "symbol"
})

# Convert to lookup dictionary (fast + clean)
bvps_map = dict(zip(bvps_df["symbol"], bvps_df["book_value_per_share"]))

# Fill missing values in book_value_per_share
book_df["book_value_per_share"] = book_df.apply(
    lambda row: bvps_map.get(row["symbol"], row["book_value_per_share"]),
    axis=1
)

# Save updated file
book_df.to_csv("book_value.csv", index=False)

print("Missing BVPS values filled successfully!")