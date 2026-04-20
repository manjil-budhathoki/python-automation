import json
import io
import csv
import time
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse

from shareshansar.announcements import AnnouncementScraper
from shareshansar.dividends import DividendScraper
from merolagani.scraper import MerolaganiScraper
from nepsealpha.scraper import NepseAlphaScraper

app = FastAPI(title="Nepal Stock Scraper API Hub")

ann_api = AnnouncementScraper()
div_api = DividendScraper()

# --- Helpers ---
def to_csv_response(data: List[Dict], filename: str, fields: List[str]):

    if not data:
        # If no data is found, we don't want to crash, 
        # we return a message or an empty file with headers
        print(f"Warning: No data found for {filename}")

    output = io.StringIO()
    # Adding extrasaction='ignore' allows the writer to skip 
    # fields like 'slug' that we didn't ask for.
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )

def to_json_response(data: List[Dict], filename: str):
    return StreamingResponse(
        io.BytesIO(json.dumps(data, indent=4).encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}.json"}
    )

# --- SINGLE SCRAPER ENDPOINTS ---

@app.get("/single/announcements", tags=["Single Stock"])
# Changed 'regex' to 'pattern' here
async def single_announcements(symbol: str, company_id: int, format: str = Query("json", pattern="^(json|csv)$")):
    data = ann_api.fetch(company_id)
    if format == "csv":
        return to_csv_response(data, f"{symbol}_announcements", ["published_date", "title"])
    return data

@app.get("/single/dividends", tags=["Single Stock"])
# Changed 'regex' to 'pattern' here
async def single_dividends(symbol: str, company_id: int, format: str = Query("json", pattern="^(json|csv)$")):
    data = div_api.fetch(company_id)
    if format == "csv":
        fields = ['year', 'bonus_share', 'cash_dividend', 'total_dividend', 'announcement_date', 'distribution_date']
        return to_csv_response(data, f"{symbol}_dividends", fields)
    return data

# --- BULK SCRAPER ENDPOINTS ---

@app.post("/bulk/announcements", tags=["Bulk Scrape"])
# Changed 'regex' to 'pattern' here
async def bulk_announcements(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    companies = json.loads(await file.read())
    results = []
    for c in companies:
        symbol = c.get('symbol')
        cid = c.get('id')
        if not cid: continue
        
        print(f"Fetching Announcements for {symbol}...")
        raw = ann_api.fetch(cid)
        for r in raw: 
            r['symbol'] = symbol
            results.append(r)
        time.sleep(0.5)
    
    if format == "csv":
        return to_csv_response(results, "bulk_announcements", ["symbol", "published_date", "title"])
    return results

@app.post("/bulk/dividends", tags=["Bulk Scrape"])
# Changed 'regex' to 'pattern' here
async def bulk_dividends(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    companies = json.loads(await file.read())
    results = []
    for c in companies:
        symbol = c.get('symbol')
        cid = c.get('id')
        if not cid: continue

        print(f"Fetching Dividends for {symbol}...")
        raw = div_api.fetch(cid)
        for r in raw: 
            r['symbol'] = symbol
            results.append(r)
        time.sleep(0.5)

    if format == "csv":
        fields = ['symbol', 'year', 'bonus_share', 'cash_dividend', 'total_dividend', 'announcement_date']
        return to_csv_response(results, "bulk_dividends", fields)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)