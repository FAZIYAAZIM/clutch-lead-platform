from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--window-size=1280,800')
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

# Try different possible URLs for AR/VR
urls = [
    "https://clutch.co/developers/ar-vr",
    "https://clutch.co/developers/ar-vr-development",
    "https://clutch.co/developers/vr-development",
    "https://clutch.co/developers/augmented-reality",
    "https://clutch.co/developers/virtual-reality",
    "https://clutch.co/it-services/ar-vr",
    "https://clutch.co/design/ar-vr",
    "https://clutch.co/ar-vr",
    "https://clutch.co/developers/vr",
    "https://clutch.co/developers/ar"
]

print("=" * 60)
print("🔍 Finding AR/VR category URL")
print("=" * 60)

for url in urls:
    print(f"\n📌 Trying: {url}")
    driver.get(url)
    time.sleep(3)
    
    if "page not found" in driver.page_source.lower() or "404" in driver.title.lower():
        print("   ❌ Not found")
    else:
        print(f"   ✅ FOUND! Title: {driver.title}")
        # Check if there are companies
        companies = driver.find_elements(By.CSS_SELECTOR, '.provider-row, .company-card, .provider')
        print(f"   📊 Companies found: {len(companies)}")
        break

driver.quit()