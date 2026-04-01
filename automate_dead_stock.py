import requests
import json

cookies = {
    'XSRF-TOKEN': 'eyJpdiI6ImxTM1FrbFZKYzQ3REhGc2diYVFIeEE9PSIsInZhbHVlIjoiZ1FMQmJnaGZJSG5pWFpZeUZNb2NpM2twZ3M4NDZLM3ZuZ284cEVKZ3BNeFFKSTRRcEhPT3VtWWd1aHBtZ1BMdWlIMHlkTDdXNythcGJRZ3VaOGdQaUpZOG1vQnY1RmRhMkNLUWQ5SkpmMkx2d05NVlg4L2FMbGczb1NXZFhvSUEiLCJtYWMiOiI0YmIxMjliZTcyMWZiNjUzNjgwMWZkZDA2NzQ5YTM0MjkzYTJkZDE0NjJiODNiM2RmMTBiYWE1Y2RmOTNiYmQxIn0%3D',
    'sharesansar_session': 'eyJpdiI6ImZuNG9DWVN4b0o0RW5KN2ZpdE1sSlE9PSIsInZhbHVlIjoiK1E5Mjl5V3FvdTlRT1FreVBtcDZ5aEVXSElkMEdnZUJTN2tEdjFJTjhXN0hjV2FrazBZSTUvODBRL3NIUEZsdDh0VllIVHAxYitRbDE4M1RCdTRKZGgvOHMyT0lVNUxWaTUyc084Qjh1NHEwOGVGSGJBWmdCVlB6alVocXF3RGIiLCJtYWMiOiIzOWE4Mjc3Mjc0M2Y5YTA0YjJmOTRlYjY3ZTRjODRkYzBhMDkzMWYwNjExNmQxMDRjYmQ2MjUyMzBkMWEwOWQzIn0%3D',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.sharesansar.com',
    'referer': 'https://www.sharesansar.com/company/ARDBL',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'x-csrf-token': 'OMzlHk61iUunYvO59J3JewK0qMOMDKNhJlNRmtQh',
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
    "KKBL": "411",
    "KMBL": "327",
    "METRO": "334",
    "MIDBL": "310",
    "MMDBL": "349",
    "MSBBL": "321",
    "NBSL": "416",
    "NDFL": "57",
    "NEFL": "84",
    "NGBL": "190",
    "RBSL": "187",
    "RHPC": "468",
    "SAFL": "567",
    "SDBL": "180",
    "SETI": "45",
    "SEWA": "189",
    "SKDBL": "479",
    "SMBF": "79",
    "WOMI": "425",
    "WDBL": "292",
    "UFIL": "93",
    "TNBL": "291",
    "TBBL": "169",
    "TDBL": "338",
    "SUBBL": "184"
}

# Fetch and save data for each company
for name, company_id in companies.items():
    print(f"\nFetching data for {name} (ID: {company_id})...")
    data = fetch_all_price_history(company_id)
    filename = f"{name}_price_history.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} records to {filename}")   