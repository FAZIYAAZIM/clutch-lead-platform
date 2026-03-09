# test_scraper.py
from app.scraper.clutch_scraper import scrape_category
import logging

logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("🚀 TESTING SCRAPER WITH FIX")
print("=" * 60)

# Try scraping just 1 page
companies = scrape_category("artificial-intelligence", max_pages=1)

if companies:
    print(f"\n✅ SUCCESS! Found {len(companies)} companies")
    if companies:
        print(f"\n📋 First company: {companies[0].get('name')}")
        print(f"   Location: {companies[0].get('location')}")
        print(f"   Rating: {companies[0].get('rating')}")
else:
    print("\n❌ No companies found, but browser is working!")