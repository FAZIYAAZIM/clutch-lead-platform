# app/services/enrichment_advanced.py
import requests
import re
import logging
from typing import List, Dict, Any
import time

logger = logging.getLogger(__name__)

class AdvancedEnrichment:
    """Advanced company enrichment with multiple data sources"""
    
    def __init__(self):
        self.email_patterns = [
            "info@{domain}",
            "contact@{domain}",
            "hello@{domain}",
            "sales@{domain}",
            "support@{domain}",
            "hr@{domain}",
            "admin@{domain}",
            "office@{domain}"
        ]
        
        # You can add API keys here later
        self.hunter_api_key = None  # Add your hunter.io API key
        self.clearbit_api_key = None  # Add your clearbit API key
    
    def find_emails_multiple_sources(self, company_name: str, website: str) -> List[str]:
        """Find emails using multiple methods"""
        emails = set()
        domain = self._extract_domain(website)
        
        # Method 1: Common patterns
        for pattern in self.email_patterns:
            emails.add(pattern.format(domain=domain))
        
        # Method 2: Hunter.io (if API key available)
        if self.hunter_api_key:
            try:
                response = requests.get(
                    f"https://api.hunter.io/v2/domain-search",
                    params={"domain": domain, "api_key": self.hunter_api_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    for email in data.get('data', {}).get('emails', []):
                        emails.add(email['value'])
            except Exception as e:
                logger.error(f"Hunter.io error: {e}")
        
        # Method 3: Guess from company name
        name_parts = company_name.lower().split()
        if name_parts:
            first_word = name_parts[0].replace(',', '').replace('.', '')
            emails.add(f"{first_word}@{domain}")
        
        return list(emails)
    
    def find_decision_makers(self, linkedin_url: str) -> List[Dict]:
        """Find key people at the company"""
        # This would need LinkedIn API or scraping
        # Placeholder for now
        return [
            {"title": "CEO", "probability": "high"},
            {"title": "CTO", "probability": "high"},
            {"title": "Head of Sales", "probability": "medium"}
        ]
    
    def get_technologies(self, website: str) -> List[str]:
        """Detect technologies used by the company"""
        try:
            response = requests.get(f"https://builtwith.com/{website}")
            # Parse technologies (simplified)
            technologies = []
            if 'shopify' in response.text.lower():
                technologies.append('Shopify')
            if 'wordpress' in response.text.lower():
                technologies.append('WordPress')
            if 'magento' in response.text.lower():
                technologies.append('Magento')
            return technologies
        except:
            return []
    
    def _extract_domain(self, website: str) -> str:
        """Extract domain from website URL"""
        if website == 'Not available' or not website:
            return ''
        domain = website.replace('https://', '').replace('http://', '')
        domain = domain.split('/')[0].split('?')[0]
        return domain

# Create singleton
advanced_enrichment = AdvancedEnrichment()