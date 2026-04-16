import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
INPUT_FILE = 'symbols.csv'
OUTPUT_FILE = 'stock_data_results.csv'

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # This prevents the "Automation" bar from appearing sometimes
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def visual_copy(driver, element):
    """This function makes the 'Copy' action visible to your eyes"""
    actions = ActionChains(driver)
    
    # 1. Scroll the page so the element is in the middle of your screen
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    
    # 2. Move the virtual mouse to the element
    actions.move_to_element(element).perform()
    
    # 3. Highlight it in Yellow with a Red border (The 'Selection' phase)
    driver.execute_script("arguments[0].style.backgroundColor = 'yellow';", element)
    driver.execute_script("arguments[0].style.border = '3px solid red';", element)
    
    time.sleep(1.5) # Wait so you can see it!
    
    data = element.text.strip()
    
    # 4. Remove highlight after 'copying'
    driver.execute_script("arguments[0].style.backgroundColor = '';", element)
    driver.execute_script("arguments[0].style.border = '';", element)
    
    return data

def get_data_live(driver, symbol):
    url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
    wait = WebDriverWait(driver, 20)
    
    print(f"--- Processing: {symbol} ---")
    
    # The 5 reloads you wanted
    for i in range(1, 6):
        driver.get(url)
        time.sleep(0.5)

    try:
        # --- SECTION 1: BOOK VALUE ---
        # The 'Address' from your 1st HTML screenshot
        bv_xpath = "//th[contains(text(),'Book Value')]/following-sibling::td"
        bv_el = wait.until(EC.presence_of_element_located((By.XPATH, bv_xpath)))
        book_value = visual_copy(driver, bv_el)

        # --- SECTION 2: THE TAB CLICK ---
        # The 'Address' from your 2nd HTML screenshot
        q_tab_id = "ctl00_ContentPlaceHolder1_CompanyDetail1_lnkQuaterlyTab"
        q_tab = wait.until(EC.element_to_be_clickable((By.ID, q_tab_id)))
        
        # Move mouse to tab and click
        actions = ActionChains(driver)
        actions.move_to_element(q_tab).click().perform()
        print(f"  Clicking Quarterly Report Tab...")
        time.sleep(2)

        # --- SECTION 3: THE DATE ---
        # The 'Address' from your 3rd HTML screenshot
        date_xpath = "//div[contains(@id, 'divQuaterly')]//table//tr[2]/td[3]"
        date_el = wait.until(EC.presence_of_element_located((By.XPATH, date_xpath)))
        
        raw_date = visual_copy(driver, date_el)
        clean_date = raw_date.split('AD')[0].strip()

        print(f"  Captured: BV={book_value}, Date={clean_date}")
        return [symbol, book_value, clean_date]

    except Exception as e:
        print(f"  Failed to find section for {symbol}")
        return [symbol, "N/A", "N/A"]

def main():
    # Read the list
    try:
        with open(INPUT_FILE, 'r') as f:
            reader = csv.DictReader(f)
            symbols = [row['Symbol'] for row in reader]
    except:
        print(f"Please create {INPUT_FILE} first!")
        return

    driver = setup_driver()
    all_results = []

    try:
        for sym in symbols:
            result = get_data_live(driver, sym)
            all_results.append(result)

        # 'Paste' into CSV
        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Book Value', 'Latest Date'])
            writer.writerows(all_results)
        
        print(f"\nSUCCESS! Look for {OUTPUT_FILE}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()