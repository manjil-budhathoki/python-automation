import os
import pandas as pd

# Paths
active_stocks_file = 'data/csv/active_stocks.csv'
source_dir = 'data/Stocks'
target_dir = 'data/active_stocks'

# Create target folder
os.makedirs(target_dir, exist_ok=True)

# Read active stock tickers
try:
    df = pd.read_csv(active_stocks_file)
    ticker_col = 'Ticker' if 'Ticker' in df.columns else df.columns[0]
    active_stocks = df[ticker_col].dropna().astype(str).str.strip()
    expected_files = [f"{ticker}.csv" for ticker in active_stocks]
except FileNotFoundError:
    print(f"❌ Error: {active_stocks_file} not found.")
    exit()

# Check which files exist and which are missing
existing_files = set(os.listdir(source_dir))
missing_files = [f for f in expected_files if f not in existing_files]

# Copy existing ones
copied_count = 0
for filename in expected_files:
    src = os.path.join(source_dir, filename)
    dst = os.path.join(target_dir, filename)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, 'r') as f_in, open(dst, 'w') as f_out:
            f_out.write(f_in.read())
        copied_count += 1

# Print missing files
print(f"\n✅ Copied {copied_count} files to '{target_dir}'.")
if missing_files:
    print("\n❌ Missing files:")
    for f in missing_files:
        print(f"  - {f}")
else:
    print("\n🎉 All files were found and copied.")   