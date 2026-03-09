import csv
import pandas as pd
from io import StringIO, BytesIO
from typing import List
from app.models.lead import Lead

class CSVExporter:
    @staticmethod
    def export_to_csv(leads: List[Lead]) -> str:
        """Export leads to CSV and return as string"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'ID', 'Company Name', 'Location', 'Rating', 'Reviews', 'Email',
            'Phone', 'Website', 'LinkedIn', 'Twitter', 'Facebook', 'Employees',
            'Hourly Rate', 'Founded', 'Services', 'Category', 'Description',
            'Lead Score', 'Email Status', 'CRM Status', 'Source', 'Created At'
        ])
        
        # Write data
        for lead in leads:
            writer.writerow([
                lead.id,
                lead.company_name,
                lead.location,
                lead.rating,
                lead.reviews,
                lead.email,
                lead.phone,
                lead.website,
                lead.linkedin,
                lead.twitter,
                lead.facebook,
                lead.employees,
                lead.hourly_rate,
                lead.founded,
                lead.services,
                lead.category,
                lead.description,
                lead.lead_score,
                lead.email_status,
                lead.crm_status,
                lead.source,
                lead.created_at
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_to_excel(leads: List[Lead]) -> bytes:
        """Export leads to Excel and return as bytes"""
        data = []
        for lead in leads:
            data.append({
                'ID': lead.id,
                'Company Name': lead.company_name,
                'Location': lead.location,
                'Rating': lead.rating,
                'Reviews': lead.reviews,
                'Email': lead.email,
                'Phone': lead.phone,
                'Website': lead.website,
                'LinkedIn': lead.linkedin,
                'Twitter': lead.twitter,
                'Facebook': lead.facebook,
                'Employees': lead.employees,
                'Hourly Rate': lead.hourly_rate,
                'Founded': lead.founded,
                'Services': lead.services,
                'Category': lead.category,
                'Description': lead.description,
                'Lead Score': lead.lead_score,
                'Email Status': lead.email_status,
                'CRM Status': lead.crm_status,
                'Source': lead.source,
                'Created At': lead.created_at
            })
        
        df = pd.DataFrame(data)
        
        # Save to BytesIO buffer instead of returning directly
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Get the bytes value
        return output.getvalue()

# Create instance
csv_exporter = CSVExporter()