# test_selenium.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Testing Selenium setup...")

try:
    # Try to get ChromeDriver
    driver_path = ChromeDriverManager().install()
    print(f"✓ ChromeDriver installed at: {driver_path}")
    
    # Try to start Chrome
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    print("✓ Chrome started successfully")
    
    # Try to open a page
    driver.get("https://www.google.com")
    print("✓ Page loaded successfully")
    print(f"Page title: {driver.title}")
    
    time.sleep(2)
    driver.quit()
    print("✓ Test completed successfully!")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")