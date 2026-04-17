import json

# 1. Open and read the messy file
with open('all_dividends.json', 'r') as file:
    content = file.read()

# 2. Find where the actual JSON array starts '[' and ends ']'
start_index = content.find('[')
end_index = content.rfind(']') + 1

# 3. Slice out just the pure JSON string
json_string = content[start_index:end_index]

# 4. Parse it to ensure it's valid and write it to a new clean file
try:
    data = json.loads(json_string)
    
    with open('clean_company_ids.json', 'w') as out_file:
        # indent=4 makes it pretty and readable
        json.dump(data, out_file, indent=4) 
        
    print(f"✅ Successfully cleaned and saved {len(data)} companies to clean_company_ids.json")
    
except json.JSONDecodeError as e:
    print("❌ Error parsing JSON:", e)