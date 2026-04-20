import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MerolaganiScraper:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        
        # FIX: These settings block notification popups
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2 
        })
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

    def fetch_book_value(self, symbol):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
        wait = WebDriverWait(driver, 15)
        
        try:
            driver.get(url)
            
            # Additional logic to close any alert if it still appears
            try:
                alert = driver.switch_to.alert
                alert.dismiss()
            except:
                pass

            bv_xpath = "//th[contains(text(),'Book Value')]/following-sibling::td"
            book_value = wait.until(EC.presence_of_element_located((By.XPATH, bv_xpath))).text.strip()

            q_tab_id = "ctl00_ContentPlaceHolder1_CompanyDetail1_lnkQuaterlyTab"
            driver.find_element(By.ID, q_tab_id).click()
            time.sleep(1.5)

            date_xpath = "//div[contains(@id, 'divQuaterly')]//table//tr[2]/td[3]"
            raw_date = wait.until(EC.presence_of_element_located((By.XPATH, date_xpath))).text
            clean_date = raw_date.split('AD')[0].strip()

            return {"symbol": symbol, "book_value": book_value, "latest_date": clean_date}
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
        finally:
            driver.quit()