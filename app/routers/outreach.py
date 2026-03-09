# app/routers/outreach.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.services.db_service import db_service
from app.models.lead import Lead
import pandas as pd
import logging
from typing import Optional, List
import json
from datetime import datetime
import re

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create-list")
async def create_outreach_list(
    categories: List[str] = Query(..., description="Categories to include"),
    min_rating: float = Query(4.0, ge=0, le=5, description="Minimum rating"),
    min_employees: int = Query(10, description="Minimum employees"),
    include_with_email: bool = Query(True, description="Only include companies with email"),
    include_with_phone: bool = Query(False, description="Only include companies with phone"),
    include_with_linkedin: bool = Query(False, description="Only include companies with LinkedIn"),
    max_companies: int = Query(100, ge=1, le=1000, description="Maximum companies to include")
):
    """
    🎯 Create a targeted outreach list based on filters
    """
    try:
        all_leads = []
        for category in categories:
            leads = db_service.get_leads(category)
            all_leads.extend(leads)
        
        # Convert to list of dicts for filtering
        filtered = []
        for lead in all_leads:
            # Apply filters
            if lead.rating and float(lead.rating) < min_rating:
                continue
            
            # Employee filter
            emp_text = getattr(lead, 'employees', '0')
            emp_num = 0
            if emp_text and emp_text != 'Unknown':
                emp_match = re.search(r'(\d+)', emp_text)
                if emp_match:
                    emp_num = int(emp_match.group(1))
            if emp_num < min_employees:
                continue
            
            # Contact info filters
            if include_with_email and (not lead.email or lead.email == 'Not available'):
                continue
            
            if include_with_phone and (not getattr(lead, 'phone', None) or lead.phone == 'Not available'):
                continue
            
            if include_with_linkedin and (not getattr(lead, 'linkedin', None) or lead.linkedin == 'Not available'):
                continue
            
            filtered.append(lead)
            if len(filtered) >= max_companies:
                break
        
        # Create outreach list with personalized fields
        outreach_data = []
        for lead in filtered[:max_companies]:
            # Generate personalized email template
            email_template = f"""Dear {lead.company_name} Team,

I came across your profile on Clutch and was impressed by your {lead.rating}-star rating and expertise in {lead.category.replace('-', ' ').title()}.

We're looking for partners who specialize in this area and would love to discuss potential collaboration opportunities.

Would you be available for a brief call next week?

Best regards,
[Your Name]"""
            
            outreach_data.append({
                'company_name': lead.company_name,
                'category': lead.category,
                'rating': lead.rating,
                'location': lead.location,
                'email': lead.email if lead.email != 'Not available' else '',
                'phone': getattr(lead, 'phone', ''),
                'linkedin': getattr(lead, 'linkedin', ''),
                'website': lead.website if lead.website != 'Not available' else '',
                'employees': getattr(lead, 'employees', ''),
                'personalized_message': email_template,
                'outreach_status': 'pending',
                'date_added': datetime.now().strftime('%Y-%m-%d')
            })
        
        # Save to CSV
        df = pd.DataFrame(outreach_data)
        filename = f"outreach_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        return FileResponse(
            path=filename,
            filename=filename,
            media_type='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Outreach list creation error: {e}")
        return {"error": str(e)}

@router.get("/stats")
async def get_outreach_stats():
    """Get statistics for outreach planning"""
    try:
        leads = db_service.get_leads()
        
        stats = {
            'total_companies': len(leads),
            'with_email': sum(1 for l in leads if l.email and l.email != 'Not available'),
            'with_phone': sum(1 for l in leads if getattr(l, 'phone', None) and l.phone != 'Not available'),
            'with_linkedin': sum(1 for l in leads if getattr(l, 'linkedin', None) and l.linkedin != 'Not available'),
            'with_website': sum(1 for l in leads if l.website and l.website != 'Not available'),
            'by_category': {},
            'by_rating': {
                '5_star (4.8+)': 0,
                '4.5_star (4.5-4.8)': 0,
                '4_star (4.0-4.5)': 0,
                'below_4': 0
            }
        }
        
        for lead in leads:
            # Category counts
            cat = lead.category or 'unknown'
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
            
            # Rating distribution
            if lead.rating:
                try:
                    rating = float(lead.rating)
                    if rating >= 4.8:
                        stats['by_rating']['5_star (4.8+)'] += 1
                    elif rating >= 4.5:
                        stats['by_rating']['4.5_star (4.5-4.8)'] += 1
                    elif rating >= 4.0:
                        stats['by_rating']['4_star (4.0-4.5)'] += 1
                    else:
                        stats['by_rating']['below_4'] += 1
                except:
                    pass
        
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

@router.get("/templates")
async def get_email_templates():
    """Get email templates for outreach"""
    templates = {
        "initial_contact": """Hi {company_name} Team,

I found your company on Clutch and was impressed by your {rating}-star rating in {category}.

We're looking for a partner with your expertise. Would you be open to a quick chat?

Best,
[Your Name]""",
        
        "follow_up": """Hi {company_name} Team,

Following up on my previous message. Would love to connect and explore how we might work together.

Are you available for a brief call next week?

Best,
[Your Name]""",
        
        "partnership": """Hi {company_name} Team,

I've been following your work in {category} and think there could be some interesting partnership opportunities between our companies.

Would you be open to a discussion?

Best,
[Your Name]"""
    }
    return templates