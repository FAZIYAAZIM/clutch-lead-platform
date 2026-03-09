from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

logging.basicConfig(level=logging.INFO)
print("=" * 60)
print("🔧 TESTING ALTERNATIVE APPROACH")
print("=" * 60)

# Try using Chrome with different options
options = Options()
options.add_argument('--headless')  # Run in background
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,800')

# Add experimental options
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

print("\n📋 Attempting to launch Chrome...")

try:
    # Let Selenium try to find the driver automatically
    driver = webdriver.Chrome(options=options)
    print("✅ Browser launched successfully!")
    
    print("\n📋 Testing navigation...")
    driver.get("https://clutch.co")
    print(f"✅ Page title: {driver.title}")
    
    print("\n✅✅✅ SUCCESS! Chrome is working!")
    driver.quit()
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    print("\n📋 Trying with explicit path...")
    try:
        # Try with explicit path to your Chrome executable
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        driver = webdriver.Chrome(options=options)
        print("✅ Second attempt successful!")
        driver.quit()
    except Exception as e2:
        print(f"❌ Second attempt failed: {e2}")