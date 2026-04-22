import pandas as pd
import re

# Load your provided data
# Replace 'financial_reports_all.csv' with your actual filename
df = pd.read_csv('financial_reports_all.csv')

# Pre-processing: Fill empty titles and ensure everything is a string to prevent errors
df['title'] = df['title'].fillna('').astype(str)

def extract_specific_quarter(title):
    t = title.lower()
    
    # 1. Look for Q1: Matches "1st quarter", "first quarter", "1st quater", etc.
    if re.search(r'(1st|first)\s+(quat?er|quarterly)', t) or re.search(r'first\s+quater', t):
        return 'Q1'
    
    # 2. Look for Q2: Matches "2nd quarter", "second quarter", etc.
    if re.search(r'(2nd|second)\s+(quat?er|quarterly)', t) or re.search(r'second\s+quater', t):
        return 'Q2'
    
    # 3. Look for Q3: Matches "3rd quarter", "third quarter", etc.
    if re.search(r'(3rd|third)\s+(quat?er|quarterly)', t) or re.search(r'third\s+quater', t):
        return 'Q3'
    
    # 4. Look for Q4: Matches "4th quarter", "fourth quarter", "final quarter", etc.
    if re.search(r'(4th|fourth|final)\s+(quat?er|quarterly)', t) or re.search(r'fourth\s+quater', t):
        return 'Q4'
    
    # 5. Fallback: Catching digit mentions like "during the 1st quarter of the fiscal year"
    if '1st quarter' in t or '1st quater' in t: return 'Q1'
    if '2nd quarter' in t or '2nd quater' in t: return 'Q2'
    if '3rd quarter' in t or '3rd quater' in t: return 'Q3'
    if '4th quarter' in t or '4th quater' in t: return 'Q4'

    return None

# Update the 'quarter' column based on the title text
df['quarter'] = df['title'].apply(extract_specific_quarter)

# RULE: Only keep rows where a quarter (1, 2, 3, or 4) was actually found in the title
filtered_df = df.dropna(subset=['quarter']).copy()

# Save the final cleaned report
filtered_df.to_csv('quarterly_announcements_only.csv', index=False)

print(f"Filtering complete. Saved {len(filtered_df)} quarterly announcements.")
# Display snippet of the result
print(filtered_df[['symbol', 'published_date', 'quarter', 'title']].head(10))