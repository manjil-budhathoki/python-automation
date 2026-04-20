import pandas as pd

df = pd.read_csv("announcements.csv")

# Keep only first 100 rows
df_100 = df.head(100)

df_100.to_csv("output_100_rows.csv", index=False)