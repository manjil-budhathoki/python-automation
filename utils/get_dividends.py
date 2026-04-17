import requests
import json
import csv
import time
import re

# Function to remove HTML tags from ShareSansar's response (like <span>0.00</span>)
def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', str(raw_html)).strip()

def scrape_all_dividends():
    # 1. Load the company IDs from your JSON file (Updated to match your VS Code filename)
    filename = 'share_shansar_stock_id.json' 
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            companies = json.load(f)
    except FileNotFoundError:
        print(f"❌ Could not find '{filename}'. Make sure the filename is correct.")
        return

    print(f"✅ Loaded {len(companies)} companies. Using manual browser cookies...")

    # 2. Your exact browser cookies and headers
    cookies = {
        'XSRF-TOKEN': 'eyJpdiI6Im9JaHFiWWpWVzJiZWpvOHdTaTlheWc9PSIsInZhbHVlIjoiTlUyM3J2UkgyUDh6WjNad2s1WUZIOFF3cmY5a3FjWWRTRmpMTDlOTHJ1UDhrUHAxN0V3MzVZUnYxdkx3N2xXT3doQWRkaWw3b2Q5NFJmQVlsTGRzNmRtUmZMdi9Vek10ZHBLT0x3Nk05dWZKS0g5VDJNSkQ0aHRNYjYyM2xBMW4iLCJtYWMiOiJkZmU0MzlkYjE5ZjU5ZGFkZTFjZDVmZjgyMjljMjk0OGU3Y2NmMjU1MzRjYzVhOGQ1MWEyZWQwNDI2ZDQxMWZiIn0%3D',
        'sharesansar_session': 'eyJpdiI6IlNGOG5kVVlRZXpZSW0ya0hMdDZzcUE9PSIsInZhbHVlIjoiYk93QnY4N2thNDBQbkp2eTRQZlZjL0dDRmwwUG8wQUZlMlFLVTZ0cmJpS1MxczluZnBRZDNIYjlSQmxNM1hjbVRLRWpxaGFISDUza1Z5MS9qek1nbXRJOGRuZnNETmROSXZmTjMxM0dMaUp1aEtOdEVZbFNicktLb1ZXdHdDVHciLCJtYWMiOiJmNjdkZTYxOTUyMjgyMjMwYmViNDZmYjFhOTgxODY1NjFmNjU1ZmEyOTA1OTE0MmU1MDk1Njg2MDJhZmEwYmJlIn0%3D',
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.sharesansar.com',
        'priority': 'u=1, i',
        'referer': 'https://www.sharesansar.com/company/wdbl',
        'sec-ch-ua': '"Brave";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        'x-csrf-token': 'V0oFy5tN6UJl08OK00bcVOtHLLECKURvX5c4Hbq8',
        'x-requested-with': 'XMLHttpRequest',
    }

    all_dividends_data =[]

    print("🚀 Starting data extraction... (Press Ctrl+C to stop at any time)")

    # 3. Loop through every company and fetch dividends
    for index, company in enumerate(companies):
        company_id = company['id']
        symbol = company['symbol']
        
        print(f"Fetching[{index+1}/{len(companies)}] : {symbol}")

        # The payload (length 100 gets all history at once)
        data = {
            'draw': '1',
            'columns[0][data]': 'DT_Row_Index', 'columns[0][searchable]': 'false', 'columns[0][orderable]': 'false',
            'columns[1][data]': 'bonus_share', 'columns[1][searchable]': 'false', 'columns[1][orderable]': 'false',
            'columns[2][data]': 'cash_dividend', 'columns[2][searchable]': 'false', 'columns[2][orderable]': 'false',
            'columns[3][data]': 'total_dividend', 'columns[3][searchable]': 'false', 'columns[3][orderable]': 'false',
            'columns[4][data]': 'announcement_date', 'columns[4][searchable]': 'false', 'columns[4][orderable]': 'false',
            'columns[5][data]': 'bookclose_date', 'columns[5][searchable]': 'false', 'columns[5][orderable]': 'false',
            'columns[6][data]': 'distribution_date', 'columns[6][searchable]': 'false', 'columns[6][orderable]': 'false',
            'columns[7][data]': 'bonus_listing_date', 'columns[7][searchable]': 'false', 'columns[7][orderable]': 'false',
            'columns[8][data]': 'year', 'columns[8][searchable]': 'false', 'columns[8][orderable]': 'false',
            'start': '0',
            'length': '100',  
            'search[value]': '',
            'search[regex]': 'false',
            'company': str(company_id)
        }

        try:
            # Pass cookies and headers directly into the requests.post method
            res = requests.post('https://www.sharesansar.com/company-dividend', cookies=cookies, headers=headers, data=data)
            
            # Check if session expired
            if res.status_code in[401, 419]:
                print("\n❌ ERROR: Your XSRF-TOKEN or cookies have expired! You need to grab new ones from your browser network tab.")
                break

            res_json = res.json()
            records = res_json.get('data',[])
            
            if records:
                for row in records:
                    all_dividends_data.append({
                        'symbol': symbol,
                        'year': clean_html(row.get('year')),
                        'cash_dividend': clean_html(row.get('cash_dividend')),
                        'bonus_share': clean_html(row.get('bonus_share')),
                        'total_dividend': clean_html(row.get('total_dividend')),
                        'announcement_date': clean_html(row.get('announcement_date'))
                    })
                    
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e} (Status Code: {res.status_code if 'res' in locals() else 'N/A'})")

        # Sleep for 0.5 seconds between requests so ShareSansar doesn't ban your IP address!
        time.sleep(0.5)

    # 4. Save everything to a CSV file
    if len(all_dividends_data) > 0:
        csv_filename = 'all_dividend_history.csv'
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames =['symbol', 'year', 'cash_dividend', 'bonus_share', 'total_dividend', 'announcement_date']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for row in all_dividends_data:
                writer.writerow(row)

        # Save as JSON as well
        with open('all_dividend_history.json', 'w', encoding='utf-8') as jf:
            json.dump(all_dividends_data, jf, indent=4)

        print(f"\n🎉 DONE! Successfully extracted {len(all_dividends_data)} dividend records.")
        print(f"📁 Data saved to '{csv_filename}' and 'all_dividend_history.json'")
    else:
        print("\n⚠️ Script finished, but no dividend data was found. Double-check your tokens if this is unexpected.")

if __name__ == "__main__":
    scrape_all_dividends()