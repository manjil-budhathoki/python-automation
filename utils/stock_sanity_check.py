import csv
import os
from pathlib import Path


def sanity_check_stock_files(stocks_dir: str) -> dict:
    """
    Sanity check: Verify that each stock CSV file's name matches the 'Symbol' column inside.
    
    Args:
        stocks_dir: Directory containing individual stock CSV files
    
    Returns:
        Dictionary with sanity check results
    """
    results = {
        "valid": [],
        "mismatched": [],
        "empty_files": [],
        "errors": []
    }
    
    stocks_dir_path = Path(stocks_dir)
    csv_files = list(stocks_dir_path.glob("*.csv"))
    
    for file_path in csv_files:
        symbol = file_path.stem
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    results["empty_files"].append(symbol)
                    continue
                
                if "Symbol" not in rows[0]:
                    results["errors"].append({
                        "symbol": symbol,
                        "error": "Missing 'Symbol' column"
                    })
                    continue
                
                file_symbol = rows[0]["Symbol"]
                
                if file_symbol == symbol:
                    results["valid"].append(symbol)
                else:
                    results["mismatched"].append({
                        "symbol": symbol,
                        "expected": symbol,
                        "found": file_symbol
                    })
                
        except Exception as e:
            results["errors"].append({
                "symbol": symbol,
                "error": str(e)
            })
    
    return results


def print_sanity_results(results: dict) -> None:
    """Print formatted sanity check results."""
    print("=" * 50)
    print("STOCK FILES SANITY CHECK RESULTS")
    print("=" * 50)
    
    print(f"\n✓ Valid files: {len(results['valid'])}")
    if results['valid']:
        print(f"  Sample: {results['valid'][:5]}")
    
    print(f"\n✗ Mismatched files: {len(results['mismatched'])}")
    for m in results['mismatched']:
        print(f"  File: {m['symbol']}.csv -> Symbol column: '{m['found']}'")
    
    print(f"\n! Empty files: {len(results['empty_files'])}")
    for m in results['empty_files'][:10]:
        print(f"  {m}.csv is empty")
    
    print(f"\n! Errors: {len(results['errors'])}")
    for e in results['errors']:
        print(f"  {e['symbol']}: {e['error']}")
    
    total = len(results['valid']) + len(results['mismatched']) + len(results['empty_files']) + len(results['errors'])
    print(f"\nTotal processed: {total}")
    print("=" * 50)


if __name__ == "__main__":
    stocks_dir = "/home/navya/Desktop/python-automation/data/Stocks"
    
    results = sanity_check_stock_files(stocks_dir)
    print_sanity_results(results)