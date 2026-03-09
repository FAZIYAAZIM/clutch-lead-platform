from app.services.email_finder import email_finder
from app.services.ai_analyzer import ai_analyzer
from app.services.db_service import db_service
from app.models.lead import Lead
import logging
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self):
        self.db = db_service
    
    def enrich_lead_sync(self, lead_id: int, find_email: bool = True, analyze: bool = True) -> Dict:
        """Synchronous version of enrich_lead (no asyncio)"""
        lead = self.db.db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            return {"error": "Lead not found", "id": lead_id}
        
        result = {
            "id": lead.id,
            "company": lead.company_name,
            "enriched_fields": []
        }
        
        # 1. Find emails (synchronously)
        if find_email:
            logger.info(f"🔍 Finding emails for {lead.company_name}")
            domain = None
            if lead.website and lead.website != 'Not available':
                domain = lead.website.replace('https://', '').replace('http://', '').split('/')[0]
            
            # Use the synchronous version of email finder
            emails = email_finder.find_emails(lead.company_name, domain)
            
            if emails:
                lead.email = ','.join(emails[:3])  # Limit to first 3 emails
                lead.email_verified = True
                result['emails'] = emails[:3]
                result['enriched_fields'].append("emails")
                logger.info(f"✅ Found {len(emails[:3])} emails")
        
        # 2. AI Analysis (synchronously)
        if analyze:
            logger.info(f"🤖 Analyzing {lead.company_name}")
            company_data = {
                'name': lead.company_name,
                'location': lead.location,
                'rating': lead.rating,
                'reviews': lead.reviews,
                'services': json.loads(lead.services) if lead.services else [],
                'hourly_rate': lead.hourly_rate,
                'employees': lead.employees,
                'website': lead.website,
                'linkedin': lead.linkedin
            }
            
            analysis = ai_analyzer.analyze_company(company_data)
            
            if analysis:
                lead.lead_score = analysis.get('score', 0)
                lead.ai_analysis_summary = json.dumps(analysis)
                if hasattr(lead, 'ai_grade'):
                    lead.ai_grade = analysis.get('grade', 'N/A')
                result['ai_analysis'] = analysis
                result['enriched_fields'].append("ai_analysis")
                logger.info(f"✅ Score: {analysis.get('score', 0)} - {analysis.get('grade', 'N/A')}")
        
        # Update timestamp
        if hasattr(lead, 'last_enriched'):
            lead.last_enriched = datetime.now()
        
        self.db.db.commit()
        
        return result
    
    def enrich_batch_sync(self, lead_ids: List[int], find_email: bool = True, analyze: bool = True) -> List[Dict]:
        """Synchronous batch enrichment"""
        results = []
        for lead_id in lead_ids:
            try:
                logger.info(f"📊 Processing lead {lead_id}...")
                result = self.enrich_lead_sync(lead_id, find_email, analyze)
                results.append(result)
            except Exception as e:
                logger.error(f"Error enriching lead {lead_id}: {e}")
                results.append({"id": lead_id, "error": str(e)})
        
        return results
    
    # Keep async versions for API compatibility
    async def enrich_lead(self, lead_id: int, find_email: bool = True, analyze: bool = True) -> Dict:
        """Async wrapper for API endpoints"""
        return self.enrich_lead_sync(lead_id, find_email, analyze)
    
    async def enrich_batch(self, lead_ids: List[int], find_email: bool = True, analyze: bool = True) -> List[Dict]:
        """Async wrapper for API endpoints"""
        return self.enrich_batch_sync(lead_ids, find_email, analyze)
    
    def close(self):
        self.db.close()

# Create instance
enrichment_service = EnrichmentService()