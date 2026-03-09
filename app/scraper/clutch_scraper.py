import time
import logging
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Try to import webdriver-manager, but don't fail if not available
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("webdriver-manager not installed. Using system ChromeDriver only.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# In the scrape_category function, replace the Cloudflare handling section:


# ============== HELPER FUNCTIONS ==============

def setup_driver():
    """Setup Chrome driver with options for production (works on Render and local)"""
    options = Options()
    
    # Basic options
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Critical for server environments (Render, Docker, etc.)
    options.add_argument('--headless=new')  # Use new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--remote-debugging-port=9222')  # Helpful for debugging
    
    # Additional stability options
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    
    # Performance options
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')  # Fatal only
    options.add_argument('--silent')
    
    # Exclude switches that might trigger detection
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Try multiple methods to create driver
    driver = None
    errors = []
    
    # Method 1: Let Selenium manage the driver automatically (Selenium 4.6+)
    try:
        logger.info("Attempting to create driver with automatic Selenium Manager...")
        driver = webdriver.Chrome(options=options)
        logger.info("✅ Driver created successfully with Selenium Manager")
        return driver
    except WebDriverException as e:
        errors.append(f"Selenium Manager failed: {str(e)[:100]}")
        logger.warning(f"Selenium Manager failed: {e}")
    
    # Method 2: Try with webdriver-manager if available
    if WEBDRIVER_MANAGER_AVAILABLE:
        try:
            logger.info("Attempting to create driver with webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ Driver created successfully with webdriver-manager")
            return driver
        except Exception as e:
            errors.append(f"webdriver-manager failed: {str(e)[:100]}")
            logger.warning(f"webdriver-manager failed: {e}")
    
    # Method 3: Try common ChromeDriver paths
    common_paths = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
        './chromedriver',
        'chromedriver.exe',
        r'C:\chromedriver.exe',
        r'C:\Windows\chromedriver.exe',
    ]
    
    for chromedriver_path in common_paths:
        if os.path.exists(chromedriver_path):
            try:
                logger.info(f"Attempting to create driver with ChromeDriver at: {chromedriver_path}")
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
                logger.info(f"✅ Driver created successfully with ChromeDriver at {chromedriver_path}")
                return driver
            except Exception as e:
                errors.append(f"Path {chromedriver_path} failed: {str(e)[:100]}")
                continue
    
    # If all methods fail, raise detailed error
    error_msg = "\n".join(errors)
    raise Exception(f"All ChromeDriver creation methods failed:\n{error_msg}")

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
                all_text = element.text
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
                result['size_category'] = 'Unknown'
        except:
            result['employees'] = 'Unknown'
            result['size_category'] = 'Unknown'
        
        # ========== SERVICES ==========
        try:
            service_elem = element.find_element(By.XPATH, './/*[contains(@class, "services") or contains(@class, "focus-areas") or contains(@class, "specialties")]')
            service_text = service_elem.text.strip()
            services = []
            for s in service_text.split('\n'):
                if s.strip():
                    services.append(s.strip())
            if not services:
                services = ['Not specified']
            result['services'] = services[:10]
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
        contact_info = []
        if result.get('phone') and result['phone'] != 'Not available':
            contact_info.append(f"Phone: {result['phone']}")
        if result.get('email') and result['email'] != 'Not available':
            contact_info.append(f"Email: {result['email']}")
        if result.get('linkedin') and result['linkedin'] != 'Not available':
            contact_info.append("LinkedIn available")
        
        result['contact_summary'] = ' | '.join(contact_info) if contact_info else 'No contact info'
        result['source'] = 'Clutch.co'
        
    except Exception as e:
        logger.error(f"Error in extract_company_data: {e}")
        return None
    
    return result

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
        'website': 'Not available',
        'founded_year': 'Unknown',
        'headquarters': 'Unknown'
    }
    
    try:
        logger.info(f"🔍 Scraping profile: {profile_url}")
        driver.get(profile_url)
        time.sleep(3)
        
        # ========== PHONE NUMBER ==========
        phone_selectors = [
            '//a[starts-with(@href, "tel:")]',
            '//span[contains(@class, "phone")]',
            '//div[contains(@class, "phone")]',
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
        
        if company_details['phone'] == 'Not available':
            try:
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                phone_patterns = [
                    r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
                    r'\+\d{1,2}\s*\(\d{3}\)\s*\d{3}[-.]?\d{4}',
                    r'\d{3}[-.]\d{3}[-.]\d{4}',
                    r'\+\d{1,2}\s*\d{3}\s*\d{3}\s*\d{4}'
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
        email_selectors = [
            '//a[starts-with(@href, "mailto:")]',
            '//span[contains(@class, "email")]',
            '//div[contains(@class, "email")]',
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
        
        if company_details['email'] == 'Not available':
            try:
                page_text = driver.find_element(By.TAG_NAME, 'body').text
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                email_match = re.search(email_pattern, page_text)
                if email_match:
                    company_details['email'] = email_match.group()
                    logger.info(f"📧 Found email from text: {company_details['email']}")
            except:
                pass
        
        # ========== SOCIAL MEDIA ==========
        social_patterns = {
            'linkedin': 'linkedin.com/company',
            'twitter': ['twitter.com', 'x.com'],
            'facebook': 'facebook.com'
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
        'a[href*="/profile/"]'
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
            break
    
    if not elements:
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
    """
    all_companies = []
    driver = None
    
    try:
        driver = setup_driver()
        
        # URL MAPPINGS
        url_mappings = {
            # Development
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
            "cybersecurity": "it-services",
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
            
            # Design
            "web-design": "design",
            "user-experience": "design",
            "product-design": "design",
            "graphic-design": "design",
            "logo-design": "design",
            "digital-design": "design",
            "packaging-design": "design",
            "design-agencies": "design",
            "design-concepts": "design",
            "full-service-design": "design",
            
            # Marketing
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
            
            # Business Services
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
        
        # Get the correct path from mapping
        path = url_mappings.get(category, "developers")
        base_url = f"https://clutch.co/{path}/{category}"
        
        logger.info(f"🎯 Scraping category: {category}")
        logger.info(f"📄 URL: {base_url}")
        logger.info(f"🔍 Profile scraping: {'ON' if scrape_profiles else 'OFF'}")
        
        driver.get(base_url)
        time.sleep(5)
        
        # ========== ENHANCED CLOUDFLARE HANDLING ==========
        max_retries = 3
        cloudflare_bypassed = False
        
        for attempt in range(max_retries):
            page_source = driver.page_source.lower()
            
            # Check if we're past Cloudflare
            if "just a moment" not in page_source and "cloudflare" not in page_source and "checking your browser" not in page_source:
                cloudflare_bypassed = True
                logger.info(f"✅ Cloudflare bypassed on attempt {attempt+1}")
                break
            
            logger.info(f"⏳ Cloudflare detected (attempt {attempt+1}/{max_retries}), waiting {15 + attempt*5} seconds...")
            time.sleep(15 + attempt*5)  # Progressive wait: 15s, 20s, 25s
            
            # Try refreshing the page
            logger.info(f"🔄 Refreshing page...")
            driver.refresh()
            time.sleep(10)
        
        if not cloudflare_bypassed:
            logger.warning("⚠️ Still blocked by Cloudflare after multiple attempts.")
            # Try one more approach - navigate to a different page and come back
            logger.info("🔄 Trying alternate approach: visiting homepage first...")
            driver.get("https://clutch.co")
            time.sleep(10)
            driver.get(base_url)
            time.sleep(10)
            
            # Final check
            if "just a moment" in driver.page_source.lower():
                logger.error("❌ Cannot bypass Cloudflare. Skipping this category.")
                return []
        
        # Check if page exists
        if "page not found" in driver.page_source.lower() or "404" in driver.title:
            logger.warning(f"⚠️ Category {category} not found at {base_url}")
            return []
        
        # Page 1
        companies = extract_companies_from_page(driver, 1)
        
        # Scrape profiles if enabled
        if scrape_profiles and companies:
            logger.info(f"🔍 Scraping profiles for {len(companies)} companies on page 1...")
            for i, company in enumerate(companies):
                if company.get('profile_url'):
                    logger.info(f"   [{i+1}/{len(companies)}] Scraping profile for {company.get('name', 'Unknown')}")
                    profile_details = scrape_company_profile(company['profile_url'], driver)
                    company.update(profile_details)
                    time.sleep(2)
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

# Alias for backward compatibility
scrape_clutch = scrape_category

# ============== TEST FUNCTION ==============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Clutch Scraper")
    print("=" * 60)
    
    # Test category scrape
    print("\n📊 Testing category scrape (artificial-intelligence):")
    companies = scrape_category("artificial-intelligence", max_pages=1, scrape_profiles=False)
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