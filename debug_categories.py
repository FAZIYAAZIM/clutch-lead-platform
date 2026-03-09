from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    options = Options()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def check_category_url(category_name, expected_path):
    """Test if a category URL works"""
    driver = None
    try:
        driver = setup_driver()
        
        # Try different possible paths
        paths = [
            f"https://clutch.co/{expected_path}/{category_name}",
            f"https://clutch.co/developers/{category_name}",
            f"https://clutch.co/design/{category_name}",
            f"https://clutch.co/marketing/{category_name}",
            f"https://clutch.co/it-services/{category_name}",
            f"https://clutch.co/business-services/{category_name}"
        ]
        
        print(f"\n{'='*60}")
        print(f"🔍 Testing category: {category_name}")
        print(f"{'='*60}")
        
        for url in paths:
            print(f"\n📌 Trying: {url}")
            driver.get(url)
            time.sleep(3)
            
            # Check if page loaded successfully
            page_title = driver.title.lower()
            page_source = driver.page_source.lower()
            
            if "page not found" in page_source or "404" in page_title:
                print("   ❌ Not found")
            elif "just a moment" in page_source:
                print("   ⚠️  Blocked by Cloudflare")
                time.sleep(5)
                driver.refresh()
                time.sleep(3)
                # Check again after refresh
                if "just a moment" not in driver.page_source.lower():
                    print("   ✅ Page loaded after refresh!")
                    # Try to find company elements
                    companies = driver.find_elements(By.CSS_SELECTOR, 'div.provider, div.company-card, div[class*="provider"]')
                    print(f"   📊 Found {len(companies)} company elements")
            else:
                print("   ✅ Page loaded successfully!")
                # Try to find company elements
                from selenium.webdriver.common.by import By
                companies = driver.find_elements(By.CSS_SELECTOR, 'div.provider, div.company-card, div[class*="provider"], div[class*="company"]')
                print(f"   📊 Found {len(companies)} company elements")
                
                # Get page title
                print(f"   📄 Page title: {driver.title}")
                
                # Take screenshot
                driver.save_screenshot(f"{category_name}_test.png")
                print(f"   📸 Screenshot saved: {category_name}_test.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            driver.quit()

# Test some categories that might have different paths
categories_to_test = [
    ("design-agencies", "design"),
    ("web-design", "design"),
    ("seo", "marketing"),
    ("ppc", "marketing"),
    ("cybersecurity", "it-services"),
    ("lead-generation", "business-services"),
    ("artificial-intelligence", "developers"),  # This one works
]

if __name__ == "__main__":
    for category_name, expected_path in categories_to_test:
        check_category_url(category_name, expected_path)
        time.sleep(2)