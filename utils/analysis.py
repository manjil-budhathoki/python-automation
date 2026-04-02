import os
import glob
import pandas as pd

folder_path = 'correct_history'
empty_files = []
data_files = []

# Use glob to reliably capture all CSV files
for file_path in glob.glob(os.path.join(folder_path, "*.csv")):
    filename = os.path.basename(file_path)
    symbol = filename.replace('.csv', '')
    
    # Check if file is empty or has only header
    if os.stat(file_path).st_size == 0:
        empty_files.append(filename)
        continue
        
    with open(file_path, 'r') as f:
        lines = f.readlines()
        if len(lines) <= 1:
            empty_files.append(filename)
            continue
    
    # Read and analyze data
    df = pd.read_csv(file_path)
    if 'Date' in df.columns and len(df) > 0:
        df['Date'] = pd.to_datetime(df['Date'])
        start_date = df['Date'].min().strftime('%Y-%m-%d')
        end_date = df['Date'].max().strftime('%Y-%m-%d')
        data_files.append({
            'Stock': symbol,
            'Start': start_date,
            'End': end_date
        })
    else:
        empty_files.append(filename)

# Save results
pd.DataFrame(data_files).to_csv('stock_timeline.csv', index=False)
pd.DataFrame(empty_files, columns=['Empty Files']).to_csv('empty_stock_files.csv', index=False)

print(f"Processed {len(data_files)} data files and {len(empty_files)} empty files.")   