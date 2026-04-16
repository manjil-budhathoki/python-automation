import pandas as pd

# load CSV
df = pd.read_csv("value.csv")

# sort by stock symbol column (change name if different)
df_sorted = df.sort_values(by="stock_symbol", ascending=True)

# save result
df_sorted.to_csv("sorted_output.csv", index=False)

print("Sorted successfully!")