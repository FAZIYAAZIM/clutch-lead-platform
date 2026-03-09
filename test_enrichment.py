import logging
from app.services.enrichment_service import enrichment_service

# Configure logging
logging.basicConfig(level=logging.INFO)

def test():
    print("🚀 Testing enrichment on first 5 leads...")
    
    # Get first 5 leads
    leads = enrichment_service.db.get_leads()
    lead_ids = [lead.id for lead in leads[:5]]
    
    print(f"📋 Processing leads: {lead_ids}")
    
    # Use synchronous version
    results = enrichment_service.enrich_batch_sync(lead_ids, find_email=True, analyze=True)
    
    print("\n📊 Enrichment Results:")
    print("=" * 50)
    
    for result in results:
        print(f"\nCompany: {result.get('company', 'Unknown')}")
        print(f"  ID: {result.get('id', 'N/A')}")
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
            continue
        
        # Show emails if found
        if 'emails' in result:
            print(f"  📧 Emails: {', '.join(result['emails'])}")
        else:
            print(f"  📧 Emails: None found")
        
        # Show AI analysis if available
        if 'ai_analysis' in result:
            ai = result['ai_analysis']
            print(f"  🤖 Score: {ai.get('score', 'N/A')}")
            print(f"  📊 Grade: {ai.get('grade', 'N/A')}")
            print(f"  💡 Recommendation: {ai.get('recommendation', 'N/A')}")
            if 'factors' in ai:
                print(f"  🔍 Factors: {', '.join(ai['factors'][:3])}")
    
    enrichment_service.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test()