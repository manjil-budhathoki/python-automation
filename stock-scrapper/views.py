import json
import time
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from utils import to_csv_response

# Import Scrapers from your folders
from shareshansar.announcements import AnnouncementScraper
from shareshansar.dividends import DividendScraper
from merolagani.scraper import MerolaganiScraper
from nepsealpha.scraper import NepseAlphaScraper

router = APIRouter()

# Initialize Scrapers
ann_api = AnnouncementScraper()
div_api = DividendScraper()

# ==========================================
# 1. SHARE SHANSAR (Fast API-based)
# ==========================================

@router.get("/shareshansar/single/announcements", tags=["ShareSansar Single"])
async def ss_single_announcements(symbol: str, company_id: int, format: str = Query("json", pattern="^(json|csv)$")):
    """Get announcements for a single stock by typing symbol/ID"""
    data = ann_api.fetch(company_id)
    if format == "csv":
        return to_csv_response(data, f"{symbol}_announcements", ["published_date", "title"])
    return data

@router.get("/shareshansar/single/dividends", tags=["ShareSansar Single"])
async def ss_single_dividends(symbol: str, company_id: int, format: str = Query("json", pattern="^(json|csv)$")):
    """Get dividend history for a single stock by typing symbol/ID"""
    data = div_api.fetch(company_id)
    if format == "csv":
        fields = ['year', 'bonus_share', 'cash_dividend', 'total_dividend', 'announcement_date', 'bookclose_date', 'distribution_date']
        return to_csv_response(data, f"{symbol}_dividends", fields)
    return data

@router.post("/shareshansar/bulk/announcements", tags=["ShareSansar Bulk"])
async def ss_bulk_announcements(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    """Upload your JSON file to get all announcements"""
    companies = json.loads(await file.read())
    results = []
    for c in companies:
        symbol, cid = c.get('symbol'), c.get('id')
        if not cid: continue
        raw = ann_api.fetch(cid)
        for r in raw: 
            r['symbol'] = symbol
            results.append(r)
        time.sleep(0.4)
    if format == "csv":
        return to_csv_response(results, "bulk_announcements", ["symbol", "published_date", "title"])
    return results

@router.post("/shareshansar/bulk/dividends", tags=["ShareSansar Bulk"])
async def ss_bulk_dividends(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    """Upload your JSON file to get all dividends"""
    companies = json.loads(await file.read())
    results = []
    for c in companies:
        symbol, cid = c.get('symbol'), c.get('id')
        if not cid: continue
        raw = div_api.fetch(cid)
        for r in raw: 
            r['symbol'] = symbol
            results.append(r)
        time.sleep(0.4)
    if format == "csv":
        fields = ['symbol', 'year', 'bonus_share', 'cash_dividend', 'total_dividend', 'announcement_date']
        return to_csv_response(results, "bulk_dividends", fields)
    return results

# ==========================================
# 2. MEROLAGANI (Selenium-based)
# ==========================================

@router.get("/merolagani/single", tags=["Merolagani"])
async def mero_single_bv(symbol: str):
    """Type a stock symbol to get Book Value (Handles Notifications)"""
    scraper = MerolaganiScraper(headless=True)
    return scraper.fetch_book_value(symbol)

@router.post("/merolagani/bulk", tags=["Merolagani"])
async def mero_bulk_bv(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    """Upload JSON to get Book Values for all stocks (Selenium)"""
    companies = json.loads(await file.read())
    results = []
    scraper = MerolaganiScraper(headless=True)
    for c in companies:
        print(f"Scraping Merolagani: {c['symbol']}")
        res = scraper.fetch_book_value(c['symbol'])
        results.append(res)
        time.sleep(1)
    if format == "csv":
        return to_csv_response(results, "bulk_merolagani_bv", ["symbol", "book_value", "latest_date"])
    return results

# ==========================================
# 3. NEPSEALPHA (Stealth-based)
# ==========================================

@router.get("/nepsealpha/single", tags=["NepseAlpha"])
async def nepse_single_eps(symbol: str):
    """Type a stock symbol to get EPS Reported"""
    scraper = NepseAlphaScraper()
    return scraper.fetch_eps(symbol)

@router.post("/nepsealpha/bulk", tags=["NepseAlpha"])
async def nepse_bulk_eps(file: UploadFile = File(...), format: str = Query("json", pattern="^(json|csv)$")):
    """Upload JSON to get EPS for all stocks (Stealth Browser)"""
    companies = json.loads(await file.read())
    results = []
    scraper = NepseAlphaScraper()
    for c in companies:
        print(f"Scraping NepseAlpha: {c['symbol']}")
        res = scraper.fetch_eps(c['symbol'])
        results.append(res)
        time.sleep(2)
    if format == "csv":
        return to_csv_response(results, "bulk_nepsealpha_eps", ["symbol", "eps_actual", "previous_eps"])
    return results