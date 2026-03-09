import time
import logging
from .clutch_scraper import scrape_category, scrape_main_directory

logger = logging.getLogger(__name__)

# ============== COMPLETE CATEGORY LIST ==============

ALL_CATEGORIES = {
    # Development
    "artificial-intelligence": "Artificial Intelligence",
    "blockchain": "Blockchain",
    "web-developers": "Web Developers",
    "software-development": "Software Development",
    "mobile-app-development": "Mobile App Development",
    "iphone-app-development": "iPhone App Development",
    "android-app-development": "Android App Development",
    "ecommerce": "E-commerce Development",
    "ar-vr": "AR/VR Development",
    "iot": "IoT Development",
    "ruby-on-rails": "Ruby on Rails",
    "shopify": "Shopify Development",
    "wordpress-developers": "WordPress Developers",
    "drupal": "Drupal Development",
    "magento": "Magento Development",
    "dotnet": ".NET Development",
    "php": "PHP Development",
    "wearables": "Wearables Development",
    "software-testing": "Software Testing",
    "react-native": "React Native Development",
    "python-django": "Python & Django",
    "flutter": "Flutter Development",
    "laravel": "Laravel Development",
    "gaming-apps": "Gaming Apps Development",
    "microsoft-sharepoint": "Microsoft SharePoint",
    "bigcommerce": "BigCommerce Development",
    "finance-apps": "Finance Apps Development",
    "webflow": "Webflow Development",
    "java": "Java Development",
    "woocommerce": "WooCommerce Development",
    
    # Design
    "web-design": "Web Design",
    "user-experience": "User Experience Design",
    "product-design": "Product Design",
    "graphic-design": "Graphic Design",
    "logo-design": "Logo Design",
    "digital-design": "Digital Design",
    "packaging-design": "Packaging Design",
    "design-agencies": "Design Agencies",
    "design-concepts": "Design Concepts",
    "full-service-design": "Full Service Design",
    
    # Marketing
    "digital-marketing": "Digital Marketing",
    "seo": "SEO Services",
    "ppc": "PPC Advertising",
    "social-media-marketing": "Social Media Marketing",
    "email-marketing": "Email Marketing",
    "content-marketing": "Content Marketing",
    "advertising": "Advertising",
    "media-buying-planning": "Media Buying & Planning",
    "branding": "Branding",
    "creative": "Creative Services",
    "naming": "Naming Services",
    "public-relations": "Public Relations",
    "market-research": "Market Research",
    "digital-strategy": "Digital Strategy",
    "video-production": "Video Production",
    "explainer-videos": "Explainer Videos",
    "commercials": "Commercials",
    "corporate-videos": "Corporate Videos",
    "2d-animation": "2D Animation",
    "3d-animation": "3D Animation",
    "motion-graphics": "Motion Graphics",
    
    # IT Services
    "cybersecurity": "Cybersecurity",
    "cloud-consulting": "Cloud Consulting",
    "bi-and-big-data": "BI & Big Data",
    "it-support": "IT Support",
    "systems-integration": "Systems Integration",
    "erp": "ERP Consulting",
    "azure": "Azure Consulting",
    "staff-augmentation": "Staff Augmentation",
    "penetration-testing": "Penetration Testing",
    "salesforce": "Salesforce Consulting",
    "aws": "AWS Consulting",
    "managed-service-providers": "Managed Service Providers",
    "account-takeover-prevention": "Account Takeover Prevention",
    
    # Business Services
    "hr-consulting": "HR Consulting",
    "accounting": "Accounting",
    "legal": "Legal Services",
    "sales-outsourcing": "Sales Outsourcing",
    "customer-support": "Customer Support",
    "lead-generation": "Lead Generation",
    "lead-qualification": "Lead Qualification",
    "bpo": "BPO Services",
    "call-centers": "Call Centers",
    "answering-services": "Answering Services",
    "outbound-call-centers": "Outbound Call Centers",
    "private-equity": "Private Equity",
    "payroll-processing": "Payroll Processing",
    "mergers-acquisitions": "Mergers & Acquisitions",
    "wealth-asset-management": "Wealth & Asset Management",
    "appointment-setting": "Appointment Setting",
    "virtual-receptionist": "Virtual Receptionist",
    "virtual-assistant": "Virtual Assistant",
    "data-entry": "Data Entry",
    "hr-recruiting": "HR Recruiting",
    "hr-staffing": "HR Staffing",
    "executive-search": "Executive Search"
}

# Category display names (same as ALL_CATEGORIES for consistency)
CATEGORY_NAMES = ALL_CATEGORIES.copy()

class ClutchMasterScraper:
    """
    Master scraper for Clutch.co - can scrape multiple categories
    """
    
    def __init__(self):
        self.all_categories = ALL_CATEGORIES
        logger.info(f"🚀 Master Scraper initialized with {len(self.all_categories)} categories")
    
    def scrape_category(self, category, max_pages=3, scrape_profiles=False):
        """
        Scrape a single category
        """
        logger.info(f"📊 Scraping category: {category}")
        return scrape_category(category, max_pages, scrape_profiles)
    
    def scrape_main_directory(self, max_pages=5):
        """
        Scrape the main directory
        """
        logger.info(f"📚 Scraping main directory")
        return scrape_main_directory(max_pages)
    
    def scrape_all_categories(self, categories_to_scrape=None, pages_per_category=2, scrape_profiles=False):
        """
        Scrape multiple categories and return combined results

        Args:
            categories_to_scrape: List of category keys to scrape (None = all)
            pages_per_category: Number of pages to scrape per category
            scrape_profiles: Whether to scrape individual company profiles

        Returns:
            Dictionary with results
        """
        if categories_to_scrape is None:
            categories_to_scrape = list(self.all_categories.keys())

        results = {
            'companies': [],
            'companies_by_category': {},
            'categories_scraped': 0,
            'total_companies': 0,
            'errors': []
        }

        total_categories = len(categories_to_scrape)
        logger.info(f"🎯 Starting master scrape of {total_categories} categories (profile scraping: {scrape_profiles})")

        for idx, category in enumerate(categories_to_scrape, 1):
            try:
                category_name = self.all_categories.get(category, category)
                logger.info(f"[{idx}/{total_categories}] Scraping: {category_name}")

                # Pass scrape_profiles to scrape_category
                companies = self.scrape_category(category, max_pages=pages_per_category, scrape_profiles=scrape_profiles)

                results['companies'].extend(companies)
                results['companies_by_category'][category] = companies
                results['categories_scraped'] += 1
                results['total_companies'] += len(companies)

                logger.info(f"✅ Found {len(companies)} companies in {category}")

                # Be nice to the server
                time.sleep(2)

            except Exception as e:
                error_msg = f"Error scraping {category}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)

        logger.info(f"🎉 Master scrape complete! Total companies: {results['total_companies']}")
        return results

# Create a singleton instance
master_scraper = ClutchMasterScraper()