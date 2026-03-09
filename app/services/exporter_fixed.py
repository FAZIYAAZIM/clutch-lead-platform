import csv
import pandas as pd
import json
from io import StringIO, BytesIO
from typing import List
from app.models.lead import Lead

class FixedExporter:
    @staticmethod
    def to_csv(leads: List[Lead]) -> str:
        """Export leads to CSV with ALL fields (safe version)"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write ALL headers
        writer.writerow([
            'ID', 'Company Name', 'Location', 'Rating', 'Reviews', 
            'Email', 'Email Verified', 'Phone', 'Website', 'LinkedIn', 
            'Twitter', 'Facebook', 'Employees', 'Size Category', 
            'Hourly Rate', 'Founded', 'Founded Year', 'Services',
            'Description', 'Category', 'Lead Score', 'AI Grade',
            'AI Recommendation', 'AI Summary', 'Source', 'Last Enriched'
        ])
        
        for lead in leads:
            # Parse services from JSON (safe)
            services = []
            if hasattr(lead, 'services') and lead.services:
                try:
                    services = json.loads(lead.services)
                except:
                    services = []
            services_str = ', '.join(services) if services else ''
            
            # Parse AI analysis (safe)
            ai_summary = ''
            ai_grade = ''
            ai_recommendation = ''
            
            if hasattr(lead, 'ai_analysis_summary') and lead.ai_analysis_summary:
                try:
                    ai_data = json.loads(lead.ai_analysis_summary)
                    ai_grade = ai_data.get('grade', 'N/A')
                    ai_recommendation = ai_data.get('recommendation', 'N/A')
                    ai_summary = str(ai_data)[:100] + '...' if len(str(ai_data)) > 100 else str(ai_data)
                except:
                    ai_summary = lead.ai_analysis_summary[:100] if lead.ai_analysis_summary else ''
            
            # Get email verified status (safe)
            email_verified = 'Yes' if hasattr(lead, 'email_verified') and lead.email_verified else 'No'
            
            # Get founded year (safe)
            founded_year = getattr(lead, 'founded_year', '')
            
            # Get last enriched (safe)
            last_enriched = getattr(lead, 'last_enriched', '')
            
            writer.writerow([
                lead.id,
                lead.company_name,
                lead.location or '',
                lead.rating or '',
                lead.reviews or '',
                lead.email or '',
                email_verified,
                getattr(lead, 'phone', '') or '',
                lead.website or '',
                getattr(lead, 'linkedin', '') or '',
                getattr(lead, 'twitter', '') or '',
                getattr(lead, 'facebook', '') or '',
                getattr(lead, 'employees', '') or '',
                getattr(lead, 'size_category', '') or '',
                getattr(lead, 'hourly_rate', '') or '',
                getattr(lead, 'founded', '') or '',
                founded_year,
                services_str,
                getattr(lead, 'description', '') or '',
                lead.category or '',
                lead.lead_score or 0,
                ai_grade,
                ai_recommendation,
                ai_summary,
                lead.source or 'Clutch.co',
                last_enriched
            ])
        
        return output.getvalue()
    
    @staticmethod
    def to_excel(leads: List[Lead]) -> bytes:
        """Export leads to Excel with ALL fields (safe version)"""
        data = []
        for lead in leads:
            # Parse services from JSON (safe)
            services = []
            if hasattr(lead, 'services') and lead.services:
                try:
                    services = json.loads(lead.services)
                except:
                    services = []
            services_str = ', '.join(services) if services else ''
            
            # Parse AI analysis (safe)
            ai_grade = ''
            ai_recommendation = ''
            
            if hasattr(lead, 'ai_analysis_summary') and lead.ai_analysis_summary:
                try:
                    ai_data = json.loads(lead.ai_analysis_summary)
                    ai_grade = ai_data.get('grade', 'N/A')
                    ai_recommendation = ai_data.get('recommendation', 'N/A')
                except:
                    pass
            
            data.append({
                'ID': lead.id,
                'Company Name': lead.company_name,
                'Location': lead.location or '',
                'Rating': lead.rating or '',
                'Reviews': lead.reviews or '',
                'Email': lead.email or '',
                'Email Verified': 'Yes' if hasattr(lead, 'email_verified') and lead.email_verified else 'No',
                'Phone': getattr(lead, 'phone', '') or '',
                'Website': lead.website or '',
                'LinkedIn': getattr(lead, 'linkedin', '') or '',
                'Twitter': getattr(lead, 'twitter', '') or '',
                'Facebook': getattr(lead, 'facebook', '') or '',
                'Employees': getattr(lead, 'employees', '') or '',
                'Size Category': getattr(lead, 'size_category', '') or '',
                'Hourly Rate': getattr(lead, 'hourly_rate', '') or '',
                'Founded': getattr(lead, 'founded', '') or '',
                'Founded Year': getattr(lead, 'founded_year', '') or '',
                'Services': services_str,
                'Description': getattr(lead, 'description', '') or '',
                'Category': lead.category or '',
                'Lead Score': lead.lead_score or 0,
                'AI Grade': ai_grade,
                'AI Recommendation': ai_recommendation,
                'Source': lead.source or 'Clutch.co',
                'Last Enriched': getattr(lead, 'last_enriched', '') or ''
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')
        
        return output.getvalue()

fixed_exporter = FixedExporter()