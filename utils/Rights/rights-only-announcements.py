import pandas as pd

# 1. Load your dataset
df = pd.read_csv('announcements.csv')

# 2. STRICT FILTER: Keep only rows that mention "right/rights" AND contain a numeric ratio (X:Y)
mask_rights = df['title'].str.contains(r'(?i)right', na=False)
mask_ratio  = df['title'].str.contains(r'\d+\s*:\s*\d+', na=False)
df_filtered = df[mask_rights & mask_ratio].copy()

# 3. EXTRACT the exact ratio (e.g., 6:5, 1:1, 0.5:1)
# Captures integers or decimals separated by a colon
df_filtered['right_issued_ratio'] = df_filtered['title'].str.extract(r'(\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?)')

# 4. Clean up spaces in the ratio (e.g., "6 : 5" -> "6:5")
df_filtered['right_issued_ratio'] = df_filtered['right_issued_ratio'].str.replace(' ', '', regex=False)

# 5. Select required columns & rename published_date -> announcementdate
result_df = df_filtered[['symbol', 'published_date', 'right_issued_ratio']].copy()
result_df.rename(columns={'published_date': 'announcementdate'}, inplace=True)

# 6. Save to new CSV
output_file = 'rights_output.csv'
result_df.to_csv(output_file, index=False)

print(f"✅ Done! Successfully extracted {len(result_df)} rights announcements to '{output_file}'")
if len(result_df) > 0:
    print("\n📊 Preview:")
    print(result_df.head())
else:
    print("⚠️  No rights issue announcements with a stated ratio were found in the current dataset.")