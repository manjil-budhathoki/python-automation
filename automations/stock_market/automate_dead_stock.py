import requests
import json

cookies = {
    'XSRF-TOKEN': 'eyJpdiI6Ikp0SDRycFgzZ2JsYjFiaDJZbDlWTGc9PSIsInZhbHVlIjoiT3VXWm9TZG5XWko1Y2JmMkVQUHJFblhoRjRoci9LMVVwbXU3MUMxcFlPSHo4VVJaZ3RkdlQ2TDNmRXJJU0tLZDVJMFdOZzMyeDZ0VDVrNXk5Q0ZaNHgrWUZVSy9LdDhnZTFKOGFVREpCbDZsYlQ0aERjdzZ3VTU1Q1lveThCMkYiLCJtYWMiOiJiNWI1OTRlZjdmNzc0N2Q4NGMyYTEyNDYyOTEzODRjYzlkMWNkNjEyOTViN2FhNTIzOTA2MmQxNzE2MGFjNTE2In0=',
    'sharesansar_session': 'eyJpdiI6IlFqV1FqTjRoa1dQRWVhTE9laDQ0Qmc9PSIsInZhbHVlIjoiNFczQW45bisrUWdJV3JjZUQ3MjgwbUdOcFgwQTFUdjVEOFM1dGJ5THZNVXNjb0E1QWJlek1mZWtBazFGUlhRanpqVjhkZkZ5b0Y1cm9QU1pBMXJkV01ScGxNRjIzN2owL1d5NTJNaUVpWmxvVzVOOUszM0dzQWZuUHQ1M0RoNGMiLCJtYWMiOiI0YzkyN2M5OTUxYTc4ZjJlMmYxMGJhYWRhMWU3YjI2YTY5NzdhZThhNWJkZWJlYTYxYzNlMDY5ZDQ5OTI1YjNmIn0=',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.sharesansar.com',
    'referer': 'https://www.sharesansar.com/company/ARDBL',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'x-csrf-token': 'jRAF6VSBuzBE1hSPLHP039FIGzK3LlZ64gwBxZF7',
    'x-requested-with': 'XMLHttpRequest',
}

def fetch_all_price_history(company_id, length=50):
    all_data = []
    start = 0
    draw = 1

    while True:
        data = {
            'draw': str(draw),
            'start': str(start),
            'length': str(length),
            'search[value]': '',
            'search[regex]': 'false',
            'company': company_id,
        }

        response = requests.post(
            'https://www.sharesansar.com/company-price-history',
            cookies=cookies,
            headers=headers,
            data=data
        )

        if response.status_code != 200:
            print(f"Error for company {company_id}: {response.status_code}")
            break

        try:
            json_data = response.json()
            rows = json_data.get('data', [])
            if not rows:
                break
            all_data.extend(rows)
            print(f"Fetched {len(rows)} rows at start={start}")
            start += length
            draw += 1
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for company {company_id}")
            break

    return all_data

# Dictionary of companies: { "Company Name": "ID" }
companies = {
    "NIDC": "156",
    "HATH": "46",
    "KEBL": "154",
    "JBNL": "331",
    "JEFL": "326",
    "GDBL.csv": "163"
}

# Fetch and save data for each company
for name, company_id in companies.items():
    print(f"\nFetching data for {name} (ID: {company_id})...")
    data = fetch_all_price_history(company_id)
    filename = f"{name}_price_history.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} records to {filename}")   