import asyncio
from app.scraper.clutch_scraper import scrape_clutch

async def test():
    categories = [
        "artificial-intelligence",
        "custom-software-development",
        "mobile-app-development",
        "web-development",
        "ecommerce-development"
    ]
    
    for category in categories:
        print(f"\n🔍 Testing: {category}")
        try:
            companies = await scrape_clutch(category, 1)
            print(f"   Found {len(companies)} companies")
        except Exception as e:
            print(f"   Error: {e}")

asyncio.run(test())