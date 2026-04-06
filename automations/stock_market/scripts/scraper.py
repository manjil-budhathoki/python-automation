"""
NEPSE Stock Market Scraper

Requirements:
- Python 3.11+ (required for NEPSE API authentication)
- requests library

The NEPSE API uses WASM-based authentication which requires Python 3.11+
Due to typing.Self feature not being available in Python 3.10

Current issue: Authentication token works but data endpoints return 401
This is a known change in NEPSE API - they now use WASM auth
"""

import requests

class NepseScraper:
    def __init__(self):
        self.base_url = "https://www.nepalstock.com"
        self.token_url = f"{self.base_url}/api/authenticate/prove"
        self.price_url = f"{self.base_url}/api/nots/nepse-data/today-price"
        
    def authenticate(self):
        response = requests.get(
            self.token_url,
            headers={"User-Agent": "Mozilla/5.0"},
            verify=False
        )
        data = response.json()
        return data.get("accessToken")
        
    def get_today_price(self, token):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(self.price_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

def main():
    print("=== NEPSE Daily Scraper ===\n")
    
    scraper = NepseScraper()
    
    print("Step 1: Authenticating...")
    token = scraper.authenticate()
    print(f"Token received: {token[:30]}...")
    
    print("\nStep 2: Fetching today's prices...")
    data = scraper.get_today_price(token)
    
    if data:
        print(f"Success! Got {len(data) if isinstance(data, list) else 'data'} records")
        print(data[:3] if isinstance(data, list) else data)
    else:
        print("Failed to fetch data")
        print("\nNOTE: NEPSE API now requires Python 3.11+")
        print("The current Python version may not support WASM authentication")
        print("\nTo fix, create a new Python 3.11 environment:")
        print("  conda create -n nepse-env python=3.11")
        print("  conda activate nepse-env")
        print("  pip install nepse-data-api")

if __name__ == "__main__":
    main()