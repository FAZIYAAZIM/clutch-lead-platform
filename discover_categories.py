from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def setup_driver():
    options = Options()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(options=options)

def check_category(url, category_name):
    driver = setup_driver()
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Checking: {category_name}")
        print(f"📌 URL: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        # Check if blocked
        if "just a moment" in driver.page_source.lower():
            print("⏳ Cloudflare detected, waiting...")
            time.sleep(10)
            driver.refresh()
            time.sleep(5)
        
        # Check if page exists
        if "page not found" in driver.page_source.lower() or "404" in driver.title:
            print("❌ Page not found")
            return False
        
        # Look for company elements
        selectors = [
            'div.provider',
            'div.company-card',
            'div[class*="provider"]',
            'div.provider-row',
            'li.provider'
        ]
        
        total_companies = 0
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✅ Found {len(elements)} companies with selector: {selector}")
                total_companies = len(elements)
                break
        
        if total_companies > 0:
            print(f"🎉 SUCCESS! Category '{category_name}' works!")
            # Take screenshot for reference
            driver.save_screenshot(f"{category_name}.png")
            print(f"📸 Screenshot saved: {category_name}.png")
            return True
        else:
            print("⚠️ Page loaded but no companies found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        driver.quit()

# Categories to test for AR/VR
categories_to_test = [
    ("ar-vr-development", "https://clutch.co/developers/ar-vr-development"),
    ("ar-vr", "https://clutch.co/developers/ar-vr"),
    ("virtual-reality", "https://clutch.co/developers/virtual-reality"),
    ("augmented-reality", "https://clutch.co/developers/augmented-reality"),
    ("vr-development", "https://clutch.co/developers/vr-development"),
    ("ar-development", "https://clutch.co/developers/ar-development"),
    ("vr", "https://clutch.co/developers/vr"),
    ("ar", "https://clutch.co/developers/ar"),
    ("virtual-reality-development", "https://clutch.co/developers/virtual-reality-development"),
    ("augmented-reality-development", "https://clutch.co/developers/augmented-reality-development"),
]

print("=" * 60)
print("🔍 DISCOVERING CORRECT AR/VR CATEGORY")
print("=" * 60)

working_categories = []
for cat_name, url in categories_to_test:
    if check_category(url, cat_name):
        working_categories.append(cat_name)
    time.sleep(2)

print("\n" + "=" * 60)
print("📊 RESULTS")
print("=" * 60)
if working_categories:
    print(f"✅ Working categories: {working_categories}")
else:
    print("❌ No working categories found. Let's check the main directory.")
    
    # Check main AR/VR directory
    driver = setup_driver()
    try:
        driver.get("https://clutch.co/developers/virtual-reality")
        time.sleep(5)
        print("\n📄 Checking main VR page...")
        
        # Look for category links
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "/developers/")]')
        vr_links = []
        for link in links:
            href = link.get_attribute('href')
            if 'virtual' in href.lower() or 'vr' in href.lower() or 'augmented' in href.lower():
                vr_links.append(href)
        
        if vr_links:
            print(f"🔗 Found AR/VR related links:")
            for link in vr_links[:10]:
                print(f"   - {link}")
    finally:
        driver.quit()