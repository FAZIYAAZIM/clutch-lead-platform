from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.core.database import SessionLocal
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db = SessionLocal()
    
    def save_leads(self, companies: list, category: str):
        """Save scraped companies to database"""
        saved_count = 0
        updated_count = 0
        error_count = 0
        
        for company in companies:
            try:
                # Check if lead already exists
                existing = self.db.query(Lead).filter(
                    Lead.company_name == company.get('name')
                ).first()
                
                # Prepare data
                lead_data = {
                    'company_name': company.get('name'),
                    'website': company.get('website', 'Not available'),
                    'location': company.get('location', 'Unknown'),
                    'rating': float(company.get('rating', 0) or 0) if company.get('rating') and company.get('rating') != 'Not rated' else None,
                    'reviews': int(company.get('reviews', 0) or 0) if company.get('reviews') else None,
                    'linkedin': company.get('linkedin'),
                    'twitter': company.get('twitter'),
                    'employees': company.get('employees'),
                    'hourly_rate': company.get('hourly_rate'),
                    'founded': company.get('founded'),
                    'services': json.dumps(company.get('services', [])) if company.get('services') else None,
                    'description': company.get('description'),
                    'category': category,
                    'source': company.get('source', 'Clutch.co'),
                    'lead_score': 0,
                    'email_status': 'pending'
                }
                
                if existing:
                    # Update existing lead
                    for key, value in lead_data.items():
                        if value is not None:
                            setattr(existing, key, value)
                    updated_count += 1
                else:
                    # Create new lead
                    new_lead = Lead(**lead_data)
                    self.db.add(new_lead)
                    saved_count += 1
                
                self.db.commit()
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error saving company {company.get('name')}: {e}")
                self.db.rollback()
        
        logger.info(f"✅ Saved {saved_count} new leads, updated {updated_count} leads, errors: {error_count}")
        return {"saved": saved_count, "updated": updated_count, "errors": error_count}
    
    def get_leads(self, category=None, min_score=None):
        """Get leads with optional filters"""
        try:
            query = self.db.query(Lead)
            
            if category:
                query = query.filter(Lead.category == category)
            
            if min_score is not None:
                query = query.filter(Lead.lead_score >= min_score)
            
            # Order by newest first
            results = query.order_by(Lead.created_at.desc()).all()
            logger.info(f"Found {len(results)} leads in database")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            return []
    
    def update_lead_emails(self, lead_id: int, emails: list):
        """Update lead with found emails"""
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                lead.email = ','.join(emails) if emails else None
                lead.email_status = 'found' if emails else 'not_found'
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating emails: {e}")
            self.db.rollback()
            return False
    
    def update_lead_score(self, lead_id: int, score: int, analysis: dict):
        """Update lead with AI score and analysis"""
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                lead.lead_score = score
                lead.ai_analysis = json.dumps(analysis)
                lead.ai_insights = json.dumps(analysis.get('insights', {}))
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating score: {e}")
            self.db.rollback()
            return False
    
    def close(self):
        """Close database session"""
        try:
            self.db.close()
        except:
            pass

# Create instance
db_service = DatabaseService()