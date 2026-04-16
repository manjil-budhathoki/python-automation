import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    return webdriver.Chrome(options=options)


def scrape_all_rights(driver):
    wait = WebDriverWait(driver, 20)

    print("Waiting for table (no refresh)...")

    # Wait for table already loaded in browser
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable"))
    )

    all_data = []

    while True:
        print("Scraping current page...")

        rows = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")

            if len(cols) >= 5:
                all_data.append({
                    "symbol": cols[0].text.strip(),
                    "ratio": cols[1].text.strip(),
                    "units": cols[2].text.strip(),
                    "opening_date": cols[3].text.strip(),
                    "closing_date": cols[4].text.strip(),
                })

        # Pagination
        try:
            next_btn = driver.find_element(By.ID, "DataTables_Table_0_next")

            if "disabled" in next_btn.get_attribute("class"):
                print("Reached last page.")
                break

            print("Next page...")
            driver.execute_script("arguments[0].click();", next_btn)

            # wait for table refresh (IMPORTANT)
            time.sleep(2)

        except Exception as e:
            print("Pagination error:", e)
            break

    return all_data


def save_data(data):
    with open("rights_data.json", "w") as f:
        json.dump(data, f, indent=2)

    with open("rights_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print("Saved files.")


if __name__ == "__main__":
    driver = setup_driver()

    try:
        data = scrape_all_rights(driver)
        print(f"Total records: {len(data)}")

        if data:
            save_data(data)

    finally:
        driver.quit()

    print("Done")