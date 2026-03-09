import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== HELPER FUNCTIONS ==============

def setup_driver():
    """Setup Chrome driver with options"""
    options = Options()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')
    
    # Add these options to help with Cloudflare
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Remove any references to Service or ChromeDriverManager
    # Let Selenium handle the driver automatically
    driver = webdriver.Chrome(options=options)
    return driver

def extract_company_data(element):
    """Extract all data from a single company element"""
    result = {}
    
    try:
        # ========== COMPANY NAME AND PROFILE URL ==========
        name_selectors = [
            './/h3/a',
            './/h3',
            './/a[contains(@href, "/profile/")]',
            './/*[contains(@class, "company_name")]/a',
            './/*[contains(@class, "provider__title")]/a',
            './/a[contains(@class, "company-title")]',
            './/span[contains(@class, "company-name")]'
        ]
        
        for selector in name_selectors:
            try:
                name_elem = element.find_element(By.XPATH, selector)
                if name_elem and name_elem.text.strip():
                    result['name'] = name_elem.text.strip()
                    
                    # Try to get profile URL
                    if name_elem.tag_name == 'a':
                        result['profile_url'] = name_elem.get_attribute('href')
                    else:
                        # Check if there's a link inside
                        try:
                            link_elem = name_elem.find_element(By.XPATH, './/a')
                            result['profile_url'] = link_elem.get_attribute('href')
                        except:
                            result['profile_url'] = None
                    break
            except:
                continue
        
        if not result.get('name'):
            return None
        
        # If no profile URL found, try direct profile link selectors
        if not result.get('profile_url'):
            try:
                profile_link = element.find_element(By.XPATH, './/a[contains(@href, "/profile/")]')
                result['profile_url'] = profile_link.get_attribute('href')
            except:
                result['profile_url'] = None
        
        # ... rest of your existing extraction code ...
        
        # ========== WEBSITE ==========
        try:
            website_elem = element.find_element(By.XPATH, './/a[contains(@href, "http") and not(contains(@href, "clutch.co"))]')
            result['website'] = website_elem.get_attribute('href') or 'Not available'
        except:
            result['website'] = 'Not available'
        
        # ========== LINKEDIN ==========
        try:
            li_elem = element.find_element(By.XPATH, './/a[contains(@href, "linkedin.com")]')
            result['linkedin'] = li_elem.get_attribute('href') or 'Not available'
        except:
            result['linkedin'] = 'Not available'
        
        # ========== TWITTER ==========
        try:
            tw_elem = element.find_element(By.XPATH, './/a[contains(@href, "twitter.com") or contains(@href, "x.com")]')
            result['twitter'] = tw_elem.get_attribute('href') or 'Not available'
        except:
            result['twitter'] = 'Not available'
        
        # ========== FACEBOOK ==========
        try:
            fb_elem = element.find_element(By.XPATH, './/a[contains(@href, "facebook.com")]')
            result['facebook'] = fb_elem.get_attribute('href') or 'Not available'
        except:
            result['facebook'] = 'Not available'
        
        # ========== PHONE / CONTACT NUMBER ==========
        # Try multiple methods to find contact numbers
        phone_found = False
        
        # Method 1: Look for tel: links
        try:
            phone_elem = element.find_element(By.XPATH, './/a[starts-with(@href, "tel:")]')
            phone = phone_elem.get_attribute('href').replace('tel:', '').replace(' ', '').strip()
            if phone:
                result['phone'] = phone
                phone_found = True
        except:
            pass
        
        # Method 2: Look for phone in text (pattern matching)
        if not phone_found:
            try:
                # Look for elements containing phone-like text
                all_text = element.text
                import re
                # US/Canada phone patterns: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
                phone_patterns = [
                    r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # (123) 456-7890
                    r'\+\d{1,2}\s*\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # +1 (123) 456-7890
                    r'\d{3}[-.]\d{3}[-.]\d{4}',  # 123-456-7890
                    r'\+\d{1,2}\s*\d{3}\s*\d{3}\s*\d{4}'  # +1 123 456 7890
                ]
                
                for pattern in phone_patterns:
                    phone_match = re.search(pattern, all_text)
                    if phone_match:
                        result['phone'] = phone_match.group()
                        phone_found = True
                        break
            except:
                pass
        
        # Method 3: Look for "Contact" button/link that might reveal phone
        if not phone_found:
            try:
                contact_btn = element.find_element(By.XPATH, './/button[contains(text(), "Contact") or contains(text(), "contact")]')
                # Can't get phone from button directly, but flag for enrichment
                result['has_contact_btn'] = True
            except:
                pass
        
        if not phone_found:
            result['phone'] = 'Not available'
        
        # ========== LOCATION ==========
        try:
            loc_elem = element.find_element(By.XPATH, './/*[contains(@class, "locality") or contains(@class, "location") or contains(@class, "address")]')
            result['location'] = loc_elem.text.strip()
        except:
            result['location'] = 'Unknown'
        
        # ========== RATING ==========
        try:
            rating_elem = element.find_element(By.XPATH, './/*[contains(@class, "rating") or contains(@class, "star-rating")]')
            rating = rating_elem.text.strip()
            import re
            rating_match = re.search(r'(\d+\.?\d*)', rating)
            result['rating'] = rating_match.group(1) if rating_match else 'Not rated'
        except:
            result['rating'] = 'Not rated'
        
        # ========== REVIEWS ==========
        try:
            review_elem = element.find_element(By.XPATH, './/*[contains(@class, "reviews-count") or contains(@class, "reviews")]')
            reviews = review_elem.text.strip()
            review_match = re.search(r'(\d+)', reviews)
            result['reviews'] = review_match.group(1) if review_match else '0'
        except:
            result['reviews'] = '0'
        
        # ========== HOURLY RATE ==========
        try:
            rate_elem = element.find_element(By.XPATH, './/*[contains(@class, "hourly-rate") or contains(@class, "rate") or contains(text(), "$")]')
            result['hourly_rate'] = rate_elem.text.strip()
        except:
            result['hourly_rate'] = 'Not specified'
        
        # ========== EMPLOYEES ==========
        try:
            emp_elem = element.find_element(By.XPATH, './/*[contains(@class, "employees") or contains(@class, "company-size") or contains(@class, "employee-count")]')
            employees = emp_elem.text.strip()
            result['employees'] = employees
            
            # Size category
            emp_match = re.search(r'(\d+)[\s-]*(\d*)', employees)
            if emp_match:
                num = int(emp_match.group(1))
                if num < 10:
                    result['size_category'] = 'Startup'
                elif num < 50:
                    result['size_category'] = 'Small'
                elif num < 200:
                    result['size_category'] = 'Medium'
                elif num < 1000:
                    result['size_category'] = 'Large'
                else:
                    result['size_category'] = 'Enterprise'
            else:
                # Check for text like "10-50 employees"
                if "employee" in employees.lower():
                    result['size_category'] = 'Unknown'
                else:
                    result['size_category'] = 'Unknown'
        except:
            result['employees'] = 'Unknown'
            result['size_category'] = 'Unknown'
        
        # ========== SERVICES ==========
        try:
            service_elem = element.find_element(By.XPATH, './/*[contains(@class, "services") or contains(@class, "focus-areas") or contains(@class, "specialties")]')
            service_text = service_elem.text.strip()
            # Split by common separators
            services = []
            for s in service_text.split('\n'):
                if s.strip():
                    services.append(s.strip())
            if not services:
                services = ['Not specified']
            result['services'] = services[:10]  # Limit to 10 services
        except:
            result['services'] = ['Not specified']
        
        # ========== DESCRIPTION ==========
        try:
            desc_elem = element.find_element(By.XPATH, './/*[contains(@class, "description") or contains(@class, "about") or contains(@class, "summary")]')
            result['description'] = desc_elem.text.strip()[:500]
        except:
            result['description'] = ''
        
        # ========== FOUNDED ==========
        try:
            founded_elem = element.find_element(By.XPATH, './/*[contains(@class, "founded") or contains(@class, "year-established") or contains(text(), "Founded")]')
            founded = founded_elem.text.strip()
            year_match = re.search(r'\b(19|20)\d{2}\b', founded)
            result['founded'] = year_match.group() if year_match else founded
        except:
            result['founded'] = 'Unknown'
        
        # ========== EMAIL (if visible) ==========
        try:
            email_elem = element.find_element(By.XPATH, './/a[contains(@href, "mailto:")]')
            email = email_elem.get_attribute('href').replace('mailto:', '').strip()
            result['email'] = email
        except:
            result['email'] = 'Not available'
        
        # ========== CONTACT INFO SUMMARY ==========
        # Add a field that combines contact info
        contact_info = []
        if result.get('phone') and result['phone'] != 'Not available':
            contact_info.append(f"Phone: {result['phone']}")
        if result.get('email') and result['email'] != 'Not available':
            contact_info.append(f"Email: {result['email']}")
        if result.get('linkedin') and result['linkedin'] != 'Not available':
            contact_info.append("LinkedIn available")
        
        result['contact_summary'] = ' | '.join(contact_info) if contact_info else 'No contact info'
        
        # ========== SOURCE ==========
        result['source'] = 'Clutch.co'
        
    except Exception as e:
        logger.error(f"Error in extract_company_data: {e}")
        return None
    
    return result


def scrape_company_profile_enhanced(profile_url, driver):
    """
    Enhanced profile scraping with more data points
    """
    company_details = {
        'phone': 'Not available',
        'email': 'Not available',
        'linkedin': 'Not available',
        'twitter': 'Not available',
        'facebook': 'Not available',
        'instagram': 'Not available',
        'youtube': 'Not available',
        'website': 'Not available',
        'founded_year': 'Unknown',
        'employees': 'Unknown',
        'headquarters': 'Unknown',
        'services_offered': [],
        'clients': [],
        'awards': []
    }
    
    try:
        logger.info(f"🔍 Enhanced profile scrape: {profile_url}")
        driver.get(profile_url)
        time.sleep(3)
        
        # ========== PHONE (Multiple methods) ==========
        phone_selectors = [
            '//a[starts-with(@href, "tel:")]',
            '//span[contains(@class, "phone")]',
            '//div[contains(@class, "phone")]',
            '//li[contains(@class, "phone")]',
            '//*[contains(text(), "Tel:")]/following-sibling::*',
            '//*[contains(text(), "Phone:")]/following-sibling::*'
        ]
        
        for selector in phone_selectors:
            try:
                phone_elem = driver.find_element(By.XPATH, selector)
                if phone_elem:
                    if 'tel:' in phone_elem.get_attribute('href', ''):
                        phone = phone_elem.get_attribute('href').replace('tel:', '').strip()
                    else:
                        phone = phone_elem.text.strip()
                    if phone and len(phone) > 5:
                        company_details['phone'] = phone
                        logger.info(f"📞 Found phone: {phone}")
                        break
            except:
                continue
        
        # ========== EMAIL (Multiple methods) ==========
        email_selectors = [
            '//a[starts-with(@href, "mailto:")]',
            '//span[contains(@class, "email")]',
            '//div[contains(@class, "email")]',
            '//li[contains(@class, "email")]',
            '//*[contains(text(), "Email:")]/following-sibling::*'
        ]
        
        for selector in email_selectors:
            try:
                email_elem = driver.find_element(By.XPATH, selector)
                if email_elem:
                    if 'mailto:' in email_elem.get_attribute('href', ''):
                        email = email_elem.get_attribute('href').replace('mailto:', '').strip()
                    else:
                        email = email_elem.text.strip()
                    if email and '@' in email:
                        company_details['email'] = email
                        logger.info(f"📧 Found email: {email}")
                        break
            except:
                continue
        
        # ========== SOCIAL MEDIA (All platforms) ==========
        social_patterns = {
            'linkedin': 'linkedin.com',
            'twitter': ['twitter.com', 'x.com'],
            'facebook': 'facebook.com',
            'instagram': 'instagram.com',
            'youtube': 'youtube.com'
        }
        
        all_links = driver.find_elements(By.XPATH, '//a[@href]')
        for link in all_links:
            href = link.get_attribute('href')
            if not href:
                continue
            
            for platform, patterns in social_patterns.items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if pattern in href and company_details[platform] == 'Not available':
                            company_details[platform] = href
                            logger.info(f"🔗 Found {platform}: {href}")
                else:
                    if patterns in href and company_details[platform] == 'Not available':
                        company_details[platform] = href
                        logger.info(f"🔗 Found {platform}: {href}")
        
        # ========== FOUNDED YEAR ==========
        try:
            founded_elem = driver.find_element(By.XPATH, '//*[contains(text(), "Founded") or contains(text(), "Established")]')
            founded_text = founded_elem.text
            year_match = re.search(r'\b(19|20)\d{2}\b', founded_text)
            if year_match:
                company_details['founded_year'] = year_match.group()
        except:
            pass
        
        # ========== HEADQUARTERS ==========
        try:
            location_selectors = [
                '//*[contains(@class, "location")]',
                '//*[contains(@class, "address")]',
                '//*[contains(@class, "headquarters")]',
                '//*[contains(text(), "Headquarters")]/following-sibling::*'
            ]
            for selector in location_selectors:
                try:
                    loc_elem = driver.find_element(By.XPATH, selector)
                    if loc_elem and loc_elem.text.strip():
                        company_details['headquarters'] = loc_elem.text.strip()
                        break
                except:
                    continue
        except:
            pass
        
        # ========== CLIENTS/AWARDS ==========
        page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        if 'client' in page_text:
            # Extract client names (simplified)
            pass
        
        if 'award' in page_text or 'recognized' in page_text:
            company_details['awards'] = ['Industry recognition found']
        
    except Exception as e:
        logger.error(f"Enhanced profile scrape error: {e}")
    
    return company_details



def scrape_company_profile(profile_url, driver):
    """
    Scrape detailed information from a company's profile page
    Returns phone, email, and social media links
    """
    company_details = {
        'phone': 'Not available',
        'email': 'Not available',
        'linkedin': 'Not available',
        'twitter': 'Not available',
        'facebook': 'Not available',
        'website': 'Not available'
    }
    
    try:
        logger.info(f"🔍 Scraping profile: {profile_url}")
        driver.get(profile_url)
        time.sleep(3)
        
        # ========== PHONE NUMBER ==========
        try:
            # Method 1: Look for tel: links
            phone_elem = driver.find_element(By.XPATH, '//a[starts-with(@href, "tel:")]')
            if phone_elem:
                phone = phone_elem.get_attribute('href').replace('tel:', '').strip()
                if phone:
                    company_details['phone'] = phone
                    logger.info(f"📞 Found phone: {phone}")
        except:
            pass
        
        if company_details['phone'] == 'Not available':
            try:
                # Method 2: Look for phone in text with pattern matching
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                phone_patterns = [
                    r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # (123) 456-7890
                    r'\+\d{1,2}\s*\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # +1 (123) 456-7890
                    r'\d{3}[-.]\d{3}[-.]\d{4}',  # 123-456-7890
                    r'\+\d{1,2}\s*\d{3}\s*\d{3}\s*\d{4}'  # +1 123 456 7890
                ]
                for pattern in phone_patterns:
                    phone_match = re.search(pattern, page_text)
                    if phone_match:
                        company_details['phone'] = phone_match.group()
                        logger.info(f"📞 Found phone from text: {company_details['phone']}")
                        break
            except:
                pass
        
        # ========== EMAIL ==========
        try:
            # Method 1: Look for mailto: links
            email_elem = driver.find_element(By.XPATH, '//a[starts-with(@href, "mailto:")]')
            if email_elem:
                email = email_elem.get_attribute('href').replace('mailto:', '').strip()
                if email:
                    company_details['email'] = email
                    logger.info(f"📧 Found email: {email}")
        except:
            pass
        
        if company_details['email'] == 'Not available':
            try:
                # Method 2: Look for email pattern in text
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                email_match = re.search(email_pattern, page_text)
                if email_match:
                    company_details['email'] = email_match.group()
                    logger.info(f"📧 Found email from text: {company_details['email']}")
            except:
                pass
        
        # ========== LINKEDIN ==========
        try:
            linkedin_elem = driver.find_element(By.XPATH, '//a[contains(@href, "linkedin.com/company")]')
            if linkedin_elem:
                company_details['linkedin'] = linkedin_elem.get_attribute('href')
                logger.info(f"🔗 Found LinkedIn: {company_details['linkedin']}")
        except:
            pass
        
        # ========== TWITTER ==========
        try:
            twitter_elem = driver.find_element(By.XPATH, '//a[contains(@href, "twitter.com") or contains(@href, "x.com")]')
            if twitter_elem:
                company_details['twitter'] = twitter_elem.get_attribute('href')
                logger.info(f"🐦 Found Twitter: {company_details['twitter']}")
        except:
            pass
        
        # ========== FACEBOOK ==========
        try:
            fb_elem = driver.find_element(By.XPATH, '//a[contains(@href, "facebook.com")]')
            if fb_elem:
                company_details['facebook'] = fb_elem.get_attribute('href')
                logger.info(f"📘 Found Facebook: {company_details['facebook']}")
        except:
            pass
        
        # ========== WEBSITE ==========
        try:
            website_elem = driver.find_element(By.XPATH, '//a[contains(@href, "http") and not(contains(@href, "clutch.co")) and not(contains(@href, "linkedin")) and not(contains(@href, "twitter")) and not(contains(@href, "facebook"))]')
            if website_elem:
                company_details['website'] = website_elem.get_attribute('href')
                logger.info(f"🌐 Found website: {company_details['website']}")
        except:
            pass
        
    except Exception as e:
        logger.error(f"Error scraping profile {profile_url}: {e}")
    
    return company_details





def extract_companies_from_page(driver, page_num, limit=50):
    """Extract company data from current page"""
    companies = []
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.company-card, div[class*="provider"], div[class*="company"], a[href*="/profile/"]'))
        )
    except TimeoutException:
        logger.warning(f"⏱️ Timeout waiting for companies on page {page_num}")
        return []
    
    # Try different selectors to find company elements
    elements = []
    selectors = [
        'div.company-card',
        'div.provider',
        'div[class*="provider"]',
        'div[class*="company"]',
        'li.provider',
        'div.provider-row',
        'div.list-item',
        'a[href*="/profile/"]'  # Sometimes each profile link is a company
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
            break
    
    if not elements:
        # Try XPath as last resort
        elements = driver.find_elements(By.XPATH, '//div[contains(@class, "company") or contains(@class, "provider")]')
    
    logger.info(f"🔍 Found {len(elements)} potential company elements on page {page_num}")
    
    for idx, element in enumerate(elements[:limit]):
        try:
            company = extract_company_data(element)
            if company and company.get('name'):
                companies.append(company)
        except Exception as e:
            logger.error(f"Error extracting company {idx}: {e}")
            continue
    
    return companies
# ============== MAIN SCRAPING FUNCTIONS ==============

def scrape_category(category, max_pages=5, scrape_profiles=False):
    """
    Scrape companies from a specific category
    Example: scrape_category("artificial-intelligence", 3, scrape_profiles=True)
    
    Args:
        category: Category slug to scrape
        max_pages: Number of pages to scrape
        scrape_profiles: If True, visit each company's profile page to get contact info
    """
    all_companies = []
    driver = None
    
    try:
        driver = setup_driver()
        
        # CORRECT URL MAPPINGS based on debug results
        url_mappings = {
            # Development (all work under /developers/)
            "artificial-intelligence": "developers",
            "blockchain": "developers",
            "web-developers": "developers",
            "software-development": "developers",
            "mobile-app-development": "developers",
            "iphone-app-development": "developers",
            "android-app-development": "developers",
            "ecommerce": "developers",
            "virtual-reality": "developers",
            "ar-vr": "developers",
            "iot": "developers",
            "ruby-on-rails": "developers",
            "shopify": "developers",
            "wordpress-developers": "developers",
            "drupal": "developers",
            "magento": "developers",
            "dotnet": "developers",
            "php": "developers",
            "wearables": "developers",
            "software-testing": "developers",
            "react-native": "developers",
            "python-django": "developers",
            "flutter": "developers",
            "laravel": "developers",
            "gaming-apps": "developers",
            "microsoft-sharepoint": "developers",
            "bigcommerce": "developers",
            "finance-apps": "developers",
            "webflow": "developers",
            "java": "developers",
            "woocommerce": "developers",
            
            # IT Services
            "cybersecurity": "it-services",  # ✅ Works!
            "cloud-consulting": "it-services",
            "bi-and-big-data": "it-services",
            "it-support": "it-services",
            "systems-integration": "it-services",
            "erp": "it-services",
            "azure": "it-services",
            "staff-augmentation": "it-services",
            "penetration-testing": "it-services",
            "salesforce": "it-services",
            "aws": "it-services",
            "managed-service-providers": "it-services",
            "account-takeover-prevention": "it-services",
            
            # Design - Need to verify these
            "web-design": "design",  # Might need different naming
            "user-experience": "design",
            "product-design": "design",
            "graphic-design": "design",
            "logo-design": "design",
            "digital-design": "design",
            "packaging-design": "design",
            "design-agencies": "design",  # This might be wrong
            "design-concepts": "design",
            "full-service-design": "design",
            
            # Marketing - Need to verify these
            "digital-marketing": "marketing",
            "seo": "marketing",
            "ppc": "marketing",
            "social-media-marketing": "marketing",
            "email-marketing": "marketing",
            "content-marketing": "marketing",
            "advertising": "marketing",
            "media-buying-planning": "marketing",
            "branding": "marketing",
            "creative": "marketing",
            "naming": "marketing",
            "public-relations": "marketing",
            "market-research": "marketing",
            "digital-strategy": "marketing",
            "video-production": "marketing",
            "explainer-videos": "marketing",
            "commercials": "marketing",
            "corporate-videos": "marketing",
            "2d-animation": "marketing",
            "3d-animation": "marketing",
            "motion-graphics": "marketing",
            
            # Business Services - Need to verify these
            "hr-consulting": "business-services",
            "accounting": "business-services",
            "legal": "business-services",
            "sales-outsourcing": "business-services",
            "customer-support": "business-services",
            "lead-generation": "business-services",
            "lead-qualification": "business-services",
            "bpo": "business-services",
            "call-centers": "business-services",
            "answering-services": "business-services",
            "outbound-call-centers": "business-services",
            "private-equity": "business-services",
            "payroll-processing": "business-services",
            "mergers-acquisitions": "business-services",
            "wealth-asset-management": "business-services",
            "appointment-setting": "business-services",
            "virtual-receptionist": "business-services",
            "virtual-assistant": "business-services",
            "data-entry": "business-services",
            "hr-recruiting": "business-services",
            "hr-staffing": "business-services",
            "executive-search": "business-services"
        }
        
        # Get the correct path from mapping, default to developers
        path = url_mappings.get(category, "developers")
        base_url = f"https://clutch.co/{path}/{category}"
        
        logger.info(f"🎯 Scraping category: {category}")
        logger.info(f"📄 URL: {base_url}")
        logger.info(f"🔍 Profile scraping: {'ON' if scrape_profiles else 'OFF'}")
        
        driver.get(base_url)
        time.sleep(5)
        
        # Handle Cloudflare
        page_source = driver.page_source.lower()
        if "just a moment" in page_source or "cloudflare" in page_source:
            logger.info("⏳ Cloudflare detected, waiting 10 seconds...")
            time.sleep(10)
            driver.refresh()
            time.sleep(5)
        
        # Check if page exists
        if "page not found" in driver.page_source.lower() or "404" in driver.title:
            logger.warning(f"⚠️ Category {category} not found at {base_url}")
            return []
        
        # Page 1
        companies = extract_companies_from_page(driver, 1)
        
        # If profile scraping is enabled, scrape each company's profile
        if scrape_profiles and companies:
            logger.info(f"🔍 Scraping profiles for {len(companies)} companies on page 1...")
            for i, company in enumerate(companies):
                if company.get('profile_url'):
                    logger.info(f"   [{i+1}/{len(companies)}] Scraping profile for {company.get('name', 'Unknown')}")
                    profile_details = scrape_company_profile(company['profile_url'], driver)
                    # Update company with profile details
                    company.update(profile_details)
                    time.sleep(2)  # Be nice to the server
                else:
                    logger.warning(f"   ⚠️ No profile URL for {company.get('name', 'Unknown')}")
        
        all_companies.extend(companies)
        logger.info(f"📊 Page 1: Found {len(companies)} companies")
        
        # More pages
        if len(companies) > 0 and max_pages > 1:
            for page_num in range(2, max_pages + 1):
                try:
                    next_url = f"{base_url}?page={page_num}"
                    logger.info(f"📄 Navigating to page {page_num}")
                    
                    driver.get(next_url)
                    time.sleep(3)
                    
                    page_companies = extract_companies_from_page(driver, page_num)
                    
                    # Scrape profiles for this page if enabled
                    if scrape_profiles and page_companies:
                        logger.info(f"🔍 Scraping profiles for {len(page_companies)} companies on page {page_num}...")
                        for i, company in enumerate(page_companies):
                            if company.get('profile_url'):
                                logger.info(f"   [{i+1}/{len(page_companies)}] Scraping profile for {company.get('name', 'Unknown')}")
                                profile_details = scrape_company_profile(company['profile_url'], driver)
                                company.update(profile_details)
                                time.sleep(2)
                            else:
                                logger.warning(f"   ⚠️ No profile URL for {company.get('name', 'Unknown')}")
                    
                    all_companies.extend(page_companies)
                    logger.info(f"📊 Page {page_num}: Found {len(page_companies)} companies")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error on page {page_num}: {e}")
                    break
        
        # Summary stats
        if scrape_profiles:
            companies_with_phone = sum(1 for c in all_companies if c.get('phone') and c['phone'] != 'Not available')
            companies_with_email = sum(1 for c in all_companies if c.get('email') and c['email'] != 'Not available')
            companies_with_linkedin = sum(1 for c in all_companies if c.get('linkedin') and c['linkedin'] != 'Not available')
            
            logger.info(f"📊 Profile scraping summary:")
            logger.info(f"   📞 Companies with phone: {companies_with_phone}")
            logger.info(f"   📧 Companies with email: {companies_with_email}")
            logger.info(f"   🔗 Companies with LinkedIn: {companies_with_linkedin}")
        
        logger.info(f"✅ Total companies from {category}: {len(all_companies)}")
        return all_companies
        
    except Exception as e:
        logger.error(f"Error in scrape_category: {e}")
        return []
        
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

# ============== BACKWARD COMPATIBILITY ==============
# Keep old function names for compatibility
scrape_clutch = scrape_category  # Alias for old code




def scrape_main_directory(max_pages=5):
    """
    Scrape ALL companies from the main directory
    This gets companies from ALL categories
    """
    all_companies = []
    driver = None
    
    try:
        driver = setup_driver()
        
        base_url = "https://clutch.co/developers"
        logger.info(f"📚 Scraping MAIN DIRECTORY: {base_url}")
        
        driver.get(base_url)
        time.sleep(5)
        
        # Handle Cloudflare/anti-bot
        page_source = driver.page_source.lower()
        if "just a moment" in page_source or "cloudflare" in page_source or "captcha" in page_source:
            logger.info("⏳ Anti-bot detected, waiting 10 seconds...")
            time.sleep(10)
            driver.refresh()
            time.sleep(5)
            
            # Check if still blocked
            if "just a moment" in driver.page_source.lower():
                logger.warning("⚠️ Still blocked by Cloudflare. Try again later.")
                return []
        
        # Page 1
        companies = extract_companies_from_page(driver, 1, limit=50)
        all_companies.extend(companies)
        logger.info(f"📊 Page 1: Found {len(companies)} companies")
        
        # More pages
        if len(companies) > 0 and max_pages > 1:
            for page_num in range(2, max_pages + 1):
                try:
                    next_url = f"{base_url}?page={page_num}"
                    logger.info(f"📄 Navigating to page {page_num}")
                    
                    driver.get(next_url)
                    time.sleep(3)
                    
                    companies = extract_companies_from_page(driver, page_num, limit=50)
                    all_companies.extend(companies)
                    logger.info(f"📊 Page {page_num}: Found {len(companies)} companies")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error on page {page_num}: {e}")
                    break
        
        logger.info(f"✅ Total companies from main directory: {len(all_companies)}")
        return all_companies
        
    except Exception as e:
        logger.error(f"Error in scrape_main_directory: {e}")
        return []
        
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

# ============== TEST FUNCTION ==============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Clutch Scraper")
    print("=" * 60)
    
    # Test category scrape
    print("\n📊 Testing category scrape (artificial-intelligence):")
    companies = scrape_category("artificial-intelligence", max_pages=2)
    print(f"✅ Found {len(companies)} companies")
    
    if companies:
        print("\n📋 Sample company:")
        company = companies[0]
        for key, value in company.items():
            if key not in ['description', 'services']:
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)