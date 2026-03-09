import requests
import re
import logging
from urllib.parse import urlparse
import asyncio
import aiohttp
from typing import List, Dict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailFinder:
    def __init__(self):
        self.common_patterns = [
            "info", "contact", "hello", "support", "sales", "admin",
            "marketing", "business", "enquiry", "team", "careers",
            "hr", "billing", "accounts", "office", "reception",
            "post", "mail", "webmaster", "help", "customerservice"
        ]
        
        # You can add API keys here for better results
        self.hunter_api_key = None  # Get from https://hunter.io
        self.clearbit_api_key = None  # Get from https://clearbit.com
    
    # ============== ASYNC METHODS (for internal use) ==============
    
    async def find_emails_async(self, company_name: str, domain: str = None) -> List[str]:
        """Find emails using multiple methods (async)"""
        emails = set()
        
        # If no domain provided, try to extract from company name
        if not domain:
            domain = self.company_to_domain(company_name)
        
        if not domain:
            return []
        
        logger.info(f"🔍 Searching emails for {company_name} ({domain})")
        
        # Method 1: Check common prefixes
        for prefix in self.common_patterns:
            emails.add(f"{prefix}@{domain}")
        
        # Method 2: Scrape website for emails
        try:
            website_emails = await self.scrape_website_for_emails(domain)
            emails.update(website_emails)
            if website_emails:
                logger.info(f"✅ Found {len(website_emails)} emails on website")
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
        
        # Method 3: Hunter.io API (if configured)
        if self.hunter_api_key:
            hunter_emails = await self.check_hunter_api(domain)
            emails.update(hunter_emails)
            if hunter_emails:
                logger.info(f"✅ Found {len(hunter_emails)} emails via Hunter.io")
        
        # Method 4: Clearbit API (if configured)
        if self.clearbit_api_key:
            clearbit_emails = await self.check_clearbit_api(domain)
            emails.update(clearbit_emails)
            if clearbit_emails:
                logger.info(f"✅ Found {len(clearbit_emails)} emails via Clearbit")
        
        # Method 5: Google search simulation (basic)
        google_emails = await self.simulate_google_search(company_name, domain)
        emails.update(google_emails)
        
        # Filter and validate emails
        valid_emails = self.validate_emails(list(emails))
        
        logger.info(f"📧 Total valid emails found: {len(valid_emails)}")
        return valid_emails
    
    async def scrape_website_for_emails(self, domain: str) -> List[str]:
        """Scrape company website for email addresses"""
        emails = set()
        
        # Try common URLs
        urls = [
            f"https://{domain}",
            f"https://www.{domain}",
            f"http://{domain}",
            f"http://www.{domain}",
            f"https://{domain}/contact",
            f"https://{domain}/about",
            f"https://{domain}/team",
            f"https://{domain}/contact-us",
            f"https://{domain}/about-us"
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in urls[:5]:  # Try first 5 URLs
                try:
                    async with session.get(url, timeout=5, ssl=False) as response:
                        if response.status == 200:
                            text = await response.text()
                            
                            # Find email patterns
                            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            found_emails = re.findall(pattern, text)
                            
                            for email in found_emails:
                                # Filter out common false positives
                                if not any(x in email.lower() for x in 
                                         ['example', 'domain', 'yourname', '@email.com', '@yourcompany']):
                                    if domain.replace('www.', '') in email.split('@')[1]:
                                        emails.add(email.lower())
                except Exception as e:
                    logger.debug(f"Error scraping {url}: {e}")
                    continue
        
        return list(emails)
    
    async def check_hunter_api(self, domain: str) -> List[str]:
        """Use Hunter.io API to find emails"""
        if not self.hunter_api_key:
            return []
        
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hunter_api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        emails = [email['value'] for email in data.get('data', {}).get('emails', [])]
                        return emails
        except Exception as e:
            logger.error(f"Hunter.io error: {e}")
        
        return []
    
    async def check_clearbit_api(self, domain: str) -> List[str]:
        """Use Clearbit API to find emails"""
        if not self.clearbit_api_key:
            return []
        
        try:
            url = f"https://person.clearbit.com/v2/combined/find?email={domain}"
            headers = {'Authorization': f'Bearer {self.clearbit_api_key}'}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        email = data.get('email')
                        return [email] if email else []
        except Exception as e:
            logger.error(f"Clearbit error: {e}")
        
        return []
    
    async def simulate_google_search(self, company_name: str, domain: str) -> List[str]:
        """Simulate finding emails via search (basic pattern matching)"""
        emails = []
        
        # Common CEO/Founder email patterns
        name_parts = company_name.lower().split()
        if len(name_parts) > 1:
            # Try ceo@domain.com
            emails.append(f"ceo@{domain}")
            # Try founder@domain.com
            emails.append(f"founder@{domain}")
            # Try contact@domain.com
            emails.append(f"contact@{domain}")
        
        return emails
    
    # ============== SYNC METHODS (for external use) ==============
    
    def find_emails_sync(self, company_name: str, domain: str = None) -> List[str]:
        """Synchronous version - use this in your enrichment service"""
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new one in a separate thread
                logger.debug("Event loop already running, creating new loop")
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(self.find_emails_async(company_name, domain))
                finally:
                    new_loop.close()
                    asyncio.set_event_loop(loop)
            else:
                # If no loop is running, use run_until_complete
                return loop.run_until_complete(self.find_emails_async(company_name, domain))
        except RuntimeError:
            # No event loop exists, create one
            logger.debug("No event loop found, creating new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.find_emails_async(company_name, domain))
            finally:
                loop.close()
    
    def find_emails(self, company_name: str, domain: str = None) -> List[str]:
        """Legacy wrapper - calls sync version"""
        return self.find_emails_sync(company_name, domain)
    
    def find_emails_batch(self, companies: List[Dict]) -> Dict[str, List[str]]:
        """Find emails for multiple companies (synchronous)"""
        results = {}
        for company in companies:
            name = company.get('name', '')
            website = company.get('website', '')
            
            domain = None
            if website and website != 'Not available':
                domain = website.replace('https://', '').replace('http://', '').split('/')[0]
            
            try:
                emails = self.find_emails_sync(name, domain)
                results[name] = emails
                logger.info(f"✅ Found {len(emails)} emails for {name}")
            except Exception as e:
                logger.error(f"Error finding emails for {name}: {e}")
                results[name] = []
        
        return results
    
    # ============== UTILITY METHODS ==============
    
    def company_to_domain(self, company_name: str) -> str:
        """Convert company name to probable domain"""
        # Remove special characters and spaces
        name = re.sub(r'[^\w\s]', '', company_name.lower())
        name = name.replace(' ', '').replace('ltd', '').replace('inc', '').replace('llc', '')
        name = name.replace('pvt', '').replace('private', '').replace('limited', '')
        name = name.replace('technologies', 'tech').replace('software', 'soft').replace('solutions', 'sol')
        
        # Common domain patterns
        domains = [
            f"{name}.com",
            f"{name}.io",
            f"{name}.co",
            f"{name}.org",
            f"{name}.net",
            f"{name}.ai",
            f"{name}.tech",
            f"{name}.app"
        ]
        
        # Return the first one (we'll check them all in website scraping)
        return domains[0]
    
    def validate_emails(self, emails: List[str]) -> List[str]:
        """Validate email format and remove duplicates"""
        valid = []
        seen = set()
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in emails:
            if email not in seen and re.match(pattern, email):
                # Additional validation - no spaces, proper length
                if len(email) < 100 and ' ' not in email:
                    valid.append(email)
                    seen.add(email)
        
        return valid
    
    def extract_domain_from_website(self, website: str) -> str:
        """Extract domain from website URL"""
        if not website or website == 'Not available':
            return None
        
        website = website.replace('https://', '').replace('http://', '').replace('www.', '')
        return website.split('/')[0].split('?')[0]

# Create instance
email_finder = EmailFinder()

# Test function
if __name__ == "__main__":
    # Test the email finder
    test_companies = [
        {"name": "TechnoYuga Soft Pvt. Ltd.", "website": "https://technoyuga.com"},
        {"name": "Simform", "website": "https://simform.com"},
        {"name": "Vention", "website": "https://vention.com"}
    ]
    
    print("🚀 Testing Email Finder...")
    results = email_finder.find_emails_batch(test_companies)
    
    for company, emails in results.items():
        print(f"\n📧 {company}:")
        if emails:
            for email in emails[:3]:
                print(f"   - {email}")
        else:
            print("   No emails found")