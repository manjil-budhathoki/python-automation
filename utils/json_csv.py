import os
import json
import pandas as pd

# Create output directory if not exists
os.makedirs('missing', exist_ok=True)

# Column mapping
column_map = {
    'published_date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Ltp',
    'per_change': '% Change',
    'traded_quantity': 'Qty',
    'traded_amount': 'Turnover'
}

# Process each JSON file in 'json/' folder
for filename in os.listdir('json'):
    if filename.endswith('.json'):
        company_name = filename.replace('.json', '')
        json_path = os.path.join('json', filename)
        csv_path = os.path.join('missing', f'{company_name}.csv')

        # Read JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to DataFrame
        df = pd.DataFrame(data)
        df = df.rename(columns=column_map)

        # Add Symbol column
        df['Symbol'] = company_name

        # Reorder columns with Symbol first
        cols = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Ltp', '% Change', 'Qty', 'Turnover']
        df = df[cols]

        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"Saved {csv_path}")   