import time
import csv
import random
import numpy as np
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def human_curve_move(driver, element):
    """Calculates a human-like curve and moves the red dot cursor visually."""
    # Get target coordinates on the screen
    location = element.location
    size = element.size
    target_x = location['x'] + size['width'] / 2
    target_y = location['y'] + size['height'] / 2

    # Starting position (usually top left of screen)
    start_x, start_y = 100, 100 

    # Generate a Bezier-like path for the cursor
    steps = random.randint(20, 35)
    points_x = np.linspace(start_x, target_x, steps)
    points_y = np.linspace(start_y, target_y, steps)

    for i in range(len(points_x)):
        # Add slight human 'jitter'
        jitter_x = points_x[i] + random.uniform(-1, 1)
        jitter_y = points_y[i] + random.uniform(-1, 1)
        
        # Update the red dot position on screen
        driver.execute_script(f"""
            var cursor = document.getElementById('ghost-cursor');
            if(cursor) {{
                cursor.style.left = '{jitter_x}px';
                cursor.style.top = '{jitter_y}px';
            }}
        """)
        time.sleep(random.uniform(0.01, 0.02))

def inject_cursor(driver):
    """Injects a red circle to act as the Virtual Mouse cursor."""
    script = """
    if(!document.getElementById('ghost-cursor')){
        var cursor = document.createElement('div');
        cursor.id = 'ghost-cursor';
        cursor.style.position = 'absolute';
        cursor.style.zIndex = '100000';
        cursor.style.width = '12px';
        cursor.style.height = '12px';
        cursor.style.background = 'rgba(255, 0, 0, 0.8)';
        cursor.style.borderRadius = '50%';
        cursor.style.border = '2px solid white';
        cursor.style.pointerEvents = 'none';
        cursor.style.top = '100px';
        cursor.style.left = '100px';
        document.body.appendChild(cursor);
    }
    """
    driver.execute_script(script)

def run_scraper(stocks):
    print("🚀 Booting Stealth Browser...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.maximize_window()

    all_data = []

    try:
        for index, symbol in enumerate(stocks):
            print(f"📦 [{index+1}/{len(stocks)}] Navigating to {symbol}...")
            driver.get(f"https://nepsealpha.com/search?q={symbol}")
            
            # Anti-bot check for first page
            if index == 0:
                print("⏳ Waiting 10s for initial load/manual verification...")
                time.sleep(10)
            
            inject_cursor(driver)

            try:
                # 1. Target the 'Financial' button specifically as per your screenshot
                # Target the <a> inside the #details-tabs list
                financial_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul#details-tabs a[href='#financials-menu']"))
                )

                # 2. Move visible cursor to button
                human_curve_move(driver, financial_btn)
                time.sleep(0.5)

                # 3. Virtual Click (Using ActionChains to simulate hardware event)
                driver.execute_script("document.getElementById('ghost-cursor').style.background = 'yellow';")
                actions = ActionChains(driver)
                actions.move_to_element(financial_btn).click().perform()
                print(f"  🖱️ Virtual Mouse clicked 'Financial' for {symbol}")
                time.sleep(0.3)
                driver.execute_script("document.getElementById('ghost-cursor').style.background = 'rgba(255,0,0,0.8)';")

                # 4. Wait for the financial table to appear
                time.sleep(2.5)

                # 5. Extract EPS Reported (Actual and Previous)
                eps_actual, eps_prev = "", ""
                # Look specifically inside the active financials menu
                rows = driver.find_elements(By.CSS_SELECTOR, "#financials-menu table tbody tr")
                
                for row in rows:
                    if "eps reported" in row.text.lower():
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 4:
                            eps_actual = cells[2].text.split('\n')[0].strip()
                            eps_prev = cells[3].text.split('\n')[0].strip()
                            break
                
                print(f"  ✅ Extracted: {eps_actual} | {eps_prev}")
                all_data.append({
                    'symbol': symbol,
                    'eps_actual': eps_actual,
                    'previous': eps_prev,
                    'date': ''
                })

            except Exception as e:
                print(f"  ⚠️ Failed to extract {symbol}. Page structure might be slow.")

            time.sleep(1.5)

    finally:
        # 6. Final Save
        with open('nepse_eps_automated.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['symbol', 'eps_actual', 'previous', 'date'])
            writer.writeheader()
            writer.writerows(all_data)
        
        print("\n🎉 SUCCESS! File saved as 'nepse_eps_automated.csv'")
        driver.quit()

# Full stock list from your request
stock_list = [
    "CMF2", "CORBL", "CREST", "CSY", "CYCL", "CZBIL", "DDBL", 
    "DHEL", "DHPL", "DLBS", "DOLTI", "DORDI", "EBL", "EBLD85", "EBLD86", "EBLD91", "EDBL", "EHPL", 
    "ENL", "FMDBL", "FOWAD", "GBBD85", "GBBL", "GBBLPO", "GBILD8485", "GBILD8687", "GBIME", 
    "GBIMESY2", "GBLBS", "GCIL", "GFCL", "GHL", "GIBF1", "GILB", "GLBSL", "GLH", "GMFBS", "GMFIL", 
    "GMLI", "GRDBL", "GSY", "GUFL", "GVL", "GWFD83", "H8020", "HATHY", "HBL", "HDHPC", "HDL", 
    "HEI", "HEIP", "HFIN", "HHL", "HIDCL", "HIDCLP", "HIMSTAR", "HLBSL", "HLI", "HLICF", "HPPL", 
    "HRL", "HURJA", "ICFC", "ICFCD83", "ICFCD88", "IGI", "IHL", "ILBS", "ILI", "JBBD87", "JBBL", 
    "JBLB", "JFL", "JHAPA", "JOSHI", "JSLBB", "KBL", "KBLPO", "KBSH", "KDBY", "KDL", "KEF", "KKHC", 
    "KMCDB", "KPCL", "KSBBL", "KSBBLD87", "KSY", "LBBL", "LBBLD89", "LBLD86", "LEC", "LICN", 
    "LLBS", "LSL", "LUK", "LVF2", "MABEL", "MAKAR", "MANDU", "MATRI", "MBJC", "MBL", "MBLEF", 
    "MCHL", "MDB", "MEHL", "MEL", "MEN", "MERO", "MFIL", "MHCL", "MHL", "MHNL", "MKCL", "MKHC", 
    "MKHL", "MKJC", "MLBBL", "MLBL", "MLBS", "MLBSL", "MMF1", "MMKJL", "MNBBL", "MNMF1", "MPFL", 
    "MSHL", "MSLB", "NABBC", "NABIL", "NABILP", "NADEP", "NBF2", "NBF3", "NBL", "NESDO", "NFS", 
    "NGPL", "NHDL", "NHPC", "NIBD84", "NIBLGF", "NIBLSTF", "NIBSF2", "NICA", "NICAD2091", "NICBF", 
    "NICFC", "NICGF2", "NICL", "NICLBSL", "NICSF", "NIFRA", "NIL", "NIMB", "NIMBPO", "NLG", "NLIC", 
    "NLICL", "NMB", "NMB50", "NMBHF2", "NMBMF", "NMFBS", "NMIC", "NMLBBL", "NRIC", "NRM", "NRN", 
    "NSIF2", "NSY", "NTC","PBD88", "PBLD84",
    "PRSF","PSF","RBBF40","RBCLPO","RLEL",
    "RMF1", "RMF2","RSY", "RURU", "SADBL", "SAGAR",
    "SANIMA", "SANVI", "SAPDBL","SBCF", "SBID2090", 
    "SBID89", "SBLD84","SEF","SFEF", "SFMF", "SHINED", "SIGS2", "SIGS3", "SKHL", "SLCF","SOHL"
]

if __name__ == "__main__":
    run_scraper(stock_list)