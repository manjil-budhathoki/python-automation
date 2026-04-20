import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class NepseAlphaScraper:
    def __init__(self):
        self.options = uc.ChromeOptions()
        # NepseAlpha is very sensitive, usually better non-headless
        # self.options.add_argument("--headless") 

    def fetch_eps(self, symbol):
        driver = uc.Chrome(options=self.options)
        try:
            driver.get(f"https://nepsealpha.com/search?q={symbol}")
            wait = WebDriverWait(driver, 20)
            
            # Click Financials Tab
            financial_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#details-tabs a[href='#financials-menu']")))
            actions = ActionChains(driver)
            actions.move_to_element(financial_btn).click().perform()
            time.sleep(3)

            # Extract EPS Reported
            eps_actual, eps_prev = "N/A", "N/A"
            rows = driver.find_elements(By.CSS_SELECTOR, "#financials-menu table tbody tr")
            
            for row in rows:
                if "eps reported" in row.text.lower():
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 4:
                        eps_actual = cells[2].text.split('\n')[0].strip()
                        eps_prev = cells[3].text.split('\n')[0].strip()
                        break
            
            return {"symbol": symbol, "eps_actual": eps_actual, "previous_eps": eps_prev}
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
        finally:
            driver.quit()