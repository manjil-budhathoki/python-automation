import requests
import json
import time

BASE_URL = "https://www.sharesansar.com/company-dividend"

# 🔥 Your company mapping
company_map = {
    "NABIL": 16,
    "ADBL": 5,
    "NICA": 59,
    # add more here
}

def create_session():
    session = requests.Session()

    headers = {
        "user-agent": "Mozilla/5.0",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.sharesansar.com/",
    }

    session.headers.update(headers)
    return session


def fetch_company_dividends(session, company_id):
    all_data = []
    start = 0
    length = 100   # 🔥 increase batch size
    draw = 1

    while True:
        payload = {
            "draw": str(draw),
            "start": str(start),
            "length": str(length),
            "search[value]": "",
            "search[regex]": "false",
            "company": str(company_id),
        }

        response = session.post(BASE_URL, data=payload)

        if response.status_code != 200:
            print(f"Error for company {company_id}")
            break

        json_data = response.json()

        rows = json_data.get("data", [])

        if not rows:
            break

        all_data.extend(rows)

        print(f"Fetched {len(rows)} rows (start={start})")

        # pagination update
        start += length
        draw += 1

        # stop condition
        if len(rows) < length:
            break

        time.sleep(0.5)  # avoid rate limit

    return all_data


def main():
    session = create_session()
    final_data = {}

    for symbol, company_id in company_map.items():
        print(f"\n=== Fetching {symbol} ===")

        data = fetch_company_dividends(session, company_id)

        final_data[symbol] = data

    # save everything
    with open("all_dividends.json", "w") as f:
        json.dump(final_data, f, indent=2)

    print("\n✅ Done. Saved all_dividends.json")


if __name__ == "__main__":
    main()