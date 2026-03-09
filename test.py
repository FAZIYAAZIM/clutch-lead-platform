import asyncio
import json
from app.scraper.clutch_scraper import scrape_clutch
from app.services.db_service import db_service

async def test():
    print("🚀 Testing ENHANCED scraper with COMPLETE data extraction...")
    print("=" * 60)
    
    companies = await scrape_clutch("artificial-intelligence", 1)
    
    print(f"\n✅ Found {len(companies)} companies with COMPLETE data!")
    
    if companies:
        # Show first company with ALL fields
        company = companies[0]
        print("\n📋 FIRST COMPANY - COMPLETE PROFILE:")
        print("=" * 60)
        print(f"🏢 Name: {company.get('name')}")
        print(f"🌐 Website: {company.get('website')}")
        print(f"💼 LinkedIn: {company.get('linkedin')}")
        print(f"🐦 Twitter: {company.get('twitter')}")
        print(f"📘 Facebook: {company.get('facebook')}")
        print(f"📍 Location: {company.get('location')}")
        print(f"⭐ Rating: {company.get('rating')}")
        print(f"📊 Reviews: {company.get('reviews')}")
        print(f"💰 Hourly Rate: {company.get('hourly_rate')}")
        print(f"👥 Employees: {company.get('employees')}")
        print(f"📏 Size Category: {company.get('size_category')}")
        print(f"📅 Founded: {company.get('founded')}")
        print(f"🔧 Services: {', '.join(company.get('services', []))}")
        print(f"📝 Description: {company.get('description')[:200]}..." if company.get('description') else "📝 Description: Not available")
        
        # Save to database
        print("\n💾 Saving to database...")
        result = db_service.save_leads(companies, "artificial-intelligence")
        print(f"📊 Result: {result}")
        
        # Show updated stats
        leads = db_service.get_leads("artificial-intelligence")
        print(f"\n📊 Total leads in DB now: {len(leads)}")
    
    db_service.close()

if __name__ == "__main__":
    asyncio.run(test())