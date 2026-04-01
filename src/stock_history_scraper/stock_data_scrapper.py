from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil

# --- Configuration ---
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
TARGET_DIR = os.path.join(os.getcwd(), "stock_history")

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

stock_list = [
    "SIL","SMH", "SMHL", "SMJC", "SNLI", "SPARS", "SPDL", "SPIL", "SRBL", "SRLI", "SSHL", 
    "SSIS", "STC", "SUBBL", "SWBBL", "SWMF", "SYFL", "TBBL", "TDBL", "TMDBL", "TNBL", "TPC", "TRH", "UAIL", "UFIL", "UFL", "UHEWA", "UIC", 
    "ULBSL", "ULI", "UMB", "UMHL", "UMRH", "UNL", "UPCL", "UPPER", "USLB", "VLBS", "WDBL", "WNLB", "WOMI"
]

def get_available_symbols():
    """Scrape the select element once to see which symbols actually exist."""
    select_element = driver.find_element(By.NAME, "symbol")
    select = Select(select_element)
    return [option.get_attribute("value") for option in select.options]

def wait_for_download(timeout=15):
    seconds = 0
    while seconds < timeout:
        time.sleep(1)
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.csv')]
        temp_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.crdownload')]
        if files and not temp_files:
            return max([os.path.join(DOWNLOAD_DIR, f) for f in files], key=os.path.getctime)
        seconds += 1
    return None

def process_stock(symbol, available_symbols):
    if symbol not in available_symbols:
        print(f"Skipping: {symbol} (Not found in dropdown)")
        return

    print(f"--- Processing: {symbol} ---")
    
    # 1. Update Dropdown
    driver.execute_script(f'$("select[name=\'symbol\']").val("{symbol}").trigger("change");')
    
    # 2. Filter
    filter_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filter')]"))
    )
    driver.execute_script("arguments[0].click();", filter_btn)
    time.sleep(3) 
    
    # 3. Click CSV
    try:
        csv_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dt-button.buttons-csv.buttons-html5"))
        )
        driver.execute_script("arguments[0].click();", csv_btn)
    except:
        print(f"No data available for {symbol}")
        return
    
    # 4. Wait and Move
    latest_file = wait_for_download()
    if latest_file:
        target_path = os.path.join(TARGET_DIR, f"{symbol}.csv")
        shutil.move(latest_file, target_path)
        print(f"Saved: {symbol}.csv")
    else:
        print(f"Error: Download failed for {symbol}")

# --- Main execution ---
print("Validating symbols...")
available_symbols = get_available_symbols()

for stock in stock_list:
    try:
        process_stock(stock, available_symbols)
    except Exception as e:
        print(f"Failed to process {stock}: {e}")

print("All done!")