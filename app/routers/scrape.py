from turtle import pd
import pandas as pd
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from app.scraper.clutch_scraper import scrape_category, scrape_main_directory
from app.scraper.master_scraper import ClutchMasterScraper, ALL_CATEGORIES, CATEGORY_NAMES
from app.scraper.master_scraper import ClutchMasterScraper, ALL_CATEGORIES, CATEGORY_NAMES, master_scraper
from app.services.db_service import db_service
from app.scraper.master_scraper import ALL_CATEGORIES
from app.services.exporter_fixed import fixed_exporter
from app.services.enrichment_service import enrichment_service
from app.services.email_finder import email_finder
from app.services.ai_analyzer import ai_analyzer
from app.models.lead import Lead
import logging
import json
from typing import Optional, List
from enum import Enum

# ⚠️ IMPORTANT: Create router FIRST before using it!
router = APIRouter()
logger = logging.getLogger(__name__)



from enum import Enum
from app.scraper.master_scraper import ALL_CATEGORIES

# Create an Enum for all categories (for Swagger dropdown)
class CategoryEnum(str, Enum):
    """All available categories on Clutch.co"""
    # Development
    ARTIFICIAL_INTELLIGENCE = "artificial-intelligence"
    BLOCKCHAIN = "blockchain"
    WEB_DEVELOPERS = "web-developers"
    SOFTWARE_DEVELOPMENT = "software-development"
    MOBILE_APP = "mobile-app-development"
    IPHONE_APP = "iphone-app-development"
    ANDROID_APP = "android-app-development"
    ECOMMERCE = "ecommerce"
    VIRTUAL_REALITY = "virtual-reality"
    IOT = "iot"
    RUBY_ON_RAILS = "ruby-on-rails"
    SHOPIFY = "shopify"
    WORDPRESS = "wordpress-developers"
    DRUPAL = "drupal"
    MAGENTO = "magento"
    DOTNET = "dotnet"
    PHP = "php"
    WEARABLES = "wearables"
    SOFTWARE_TESTING = "software-testing"
    REACT_NATIVE = "react-native"
    PYTHON_DJANGO = "python-django"
    FLUTTER = "flutter"
    LARAVEL = "laravel"
    GAMING_APPS = "gaming-apps"
    MICROSOFT_SHAREPOINT = "microsoft-sharepoint"
    BIGCOMMERCE = "bigcommerce"
    FINANCE_APPS = "finance-apps"
    WEBFLOW = "webflow"
    JAVA = "java"
    WOOCOMMERCE = "woocommerce"
    
    # Design
    WEB_DESIGN = "web-design"
    USER_EXPERIENCE = "user-experience"
    PRODUCT_DESIGN = "product-design"
    GRAPHIC_DESIGN = "graphic-design"
    LOGO_DESIGN = "logo-design"
    DIGITAL_DESIGN = "digital-design"
    PACKAGING_DESIGN = "packaging-design"
    DESIGN_AGENCIES = "design-agencies"
    DESIGN_CONCEPTS = "design-concepts"
    FULL_SERVICE_DESIGN = "full-service-design"
    
    # Marketing
    DIGITAL_MARKETING = "digital-marketing"
    SEO = "seo"
    PPC = "ppc"
    SOCIAL_MEDIA = "social-media-marketing"
    EMAIL_MARKETING = "email-marketing"
    CONTENT_MARKETING = "content-marketing"
    ADVERTISING = "advertising"
    MEDIA_BUYING = "media-buying-planning"
    BRANDING = "branding"
    CREATIVE = "creative"
    NAMING = "naming"
    PUBLIC_RELATIONS = "public-relations"
    MARKET_RESEARCH = "market-research"
    DIGITAL_STRATEGY = "digital-strategy"
    VIDEO_PRODUCTION = "video-production"
    EXPLAINER_VIDEOS = "explainer-videos"
    COMMERCIALS = "commercials"
    CORPORATE_VIDEOS = "corporate-videos"
    ANIMATION_2D = "2d-animation"
    ANIMATION_3D = "3d-animation"
    MOTION_GRAPHICS = "motion-graphics"
    
    # IT Services
    CYBERSECURITY = "cybersecurity"
    CLOUD_CONSULTING = "cloud-consulting"
    BI_BIG_DATA = "bi-and-big-data"
    IT_SUPPORT = "it-support"
    SYSTEMS_INTEGRATION = "systems-integration"
    ERP = "erp"
    AZURE = "azure"
    STAFF_AUGMENTATION = "staff-augmentation"
    PENETRATION_TESTING = "penetration-testing"
    SALESFORCE = "salesforce"
    AWS = "aws"
    MANAGED_SERVICE_PROVIDERS = "managed-service-providers"
    ACCOUNT_TAKEOVER_PREVENTION = "account-takeover-prevention"
    
    # Business Services
    HR_CONSULTING = "hr-consulting"
    ACCOUNTING = "accounting"
    LEGAL = "legal"
    SALES_OUTSOURCING = "sales-outsourcing"
    CUSTOMER_SUPPORT = "customer-support"
    LEAD_GENERATION = "lead-generation"
    LEAD_QUALIFICATION = "lead-qualification"
    BPO = "bpo"
    CALL_CENTERS = "call-centers"
    ANSWERING_SERVICES = "answering-services"
    OUTBOUND_CALL_CENTERS = "outbound-call-centers"
    PRIVATE_EQUITY = "private-equity"
    PAYROLL_PROCESSING = "payroll-processing"
    MERGERS_ACQUISITIONS = "mergers-acquisitions"
    WEALTH_ASSET_MANAGEMENT = "wealth-asset-management"
    APPOINTMENT_SETTING = "appointment-setting"
    VIRTUAL_RECEPTIONIST = "virtual-receptionist"
    VIRTUAL_ASSISTANT = "virtual-assistant"
    DATA_ENTRY = "data-entry"
    HR_RECRUITING = "hr-recruiting"
    HR_STAFFING = "hr-staffing"
    EXECUTIVE_SEARCH = "executive-search"

@router.post("/master-scrape")
async def master_scrape(
    categories: Optional[List[CategoryEnum]] = Query(None, description="List of categories to scrape"),
    pages_per_category: int = Query(2, description="Pages per category", ge=1, le=5),
    scrape_profiles: bool = Query(False, description="Scrape individual company profiles for contact info"),
    save_to_db: bool = Query(True, description="Save results to database"),
    background_tasks: BackgroundTasks = None
):
   
    """
    🚀 ULTIMATE SCRAPER - Gets ALL companies from ALL Clutch categories!
    
    **Categories Available:**
    - **Development**: AI, Blockchain, Web, Mobile, Ecommerce, Shopify, etc.
    - **Design**: Web Design, UX, Product Design, Graphic Design, etc.
    - **Marketing**: SEO, PPC, Social Media, Email Marketing, etc.
    - **IT Services**: Cybersecurity, Cloud, BI, IT Support, etc.
    - **Business Services**: HR, Accounting, Legal, Lead Generation, etc.
    
    **How to use:**
    1. Click "Try it out"
    2. Click "Add item" to select categories from dropdown
    3. Leave empty to scrape ALL 96 categories
    4. Set pages_per_category (1-5)
    5. Execute!
    """
    
    # Convert Enum values to strings
    category_values = [cat.value for cat in categories] if categories else None
    
    # Initialize master scraper
    scraper = ClutchMasterScraper()
    
    # Determine which categories to scrape
    if not category_values or len(category_values) == 0:
        categories_to_scrape = list(ALL_CATEGORIES.keys())
        logger.info(f"🎯 Scraping ALL {len(categories_to_scrape)} categories")
    else:
        categories_to_scrape = [c for c in category_values if c in ALL_CATEGORIES]
        logger.info(f"🎯 Scraping {len(categories_to_scrape)} specified categories")
    
    if background_tasks:
        background_tasks.add_task(
            run_master_scrape_background,
            categories_to_scrape,
            pages_per_category,
            scrape_profiles,  # Add this parameter
            save_to_db
        )
        return {
            "success": True,
            "message": f"✅ Master scrape started in background for {len(categories_to_scrape)} categories",
            "categories": categories_to_scrape[:10],  # Show first 10
            "total_categories": len(categories_to_scrape)
        }
    else:
        # Run synchronously
        results = scraper.scrape_all_categories(
            categories_to_scrape=categories_to_scrape,
            pages_per_category=pages_per_category
        )
        
        # Save to database if requested
        saved_count = 0
        if save_to_db and results['companies']:
            for category, cat_companies in results['companies_by_category'].items():
                if cat_companies:
                    db_result = db_service.save_leads(cat_companies, category)
                    saved_count += db_result.get('saved', 0)
        
        return {
            "success": True,
            "total_companies": results['total_companies'],
            "categories_scraped": results['categories_scraped'],
            "companies_by_category": results['companies_by_category'],
            "saved_to_db": saved_count if save_to_db else 0,
            "message": f"✅ Scraped {results['total_companies']} companies from {results['categories_scraped']} categories"
        }



# ============== CATEGORY ENUM FOR DROPDOWN ==============

class ClutchCategory(str, Enum):
    """All categories from Clutch.co sitemap"""
    # Development
    ARTIFICIAL_INTELLIGENCE = "artificial-intelligence"
    BLOCKCHAIN = "blockchain"
    WEB_DEVELOPERS = "web-developers"
    SOFTWARE_DEVELOPMENT = "software-development"
    MOBILE_APP = "mobile-app-development"
    IPHONE_APP = "iphone-app-development"
    ANDROID_APP = "android-app-development"
    ECOMMERCE = "ecommerce"
    VIRTUAL_REALITY = "virtual-reality"  # Alternative
    IOT = "iot"
    RUBY_ON_RAILS = "ruby-on-rails"
    SHOPIFY = "shopify"
    WORDPRESS = "wordpress-developers"
    DRUPAL = "drupal"
    MAGENTO = "magento"
    DOTNET = "dotnet"
    PHP = "php"
    WEARABLES = "wearables"
    SOFTWARE_TESTING = "software-testing"
    REACT_NATIVE = "react-native"
    PYTHON_DJANGO = "python-django"
    FLUTTER = "flutter"
    LARAVEL = "laravel"
    GAMING_APPS = "gaming-apps"
    MICROSOFT_SHAREPOINT = "microsoft-sharepoint"
    BIGCOMMERCE = "bigcommerce"
    FINANCE_APPS = "finance-apps"
    WEBFLOW = "webflow"
    JAVA = "java"
    WOOCOMMERCE = "woocommerce"
    
    # Design
    WEB_DESIGN = "web-design"
    USER_EXPERIENCE = "user-experience"
    PRODUCT_DESIGN = "product-design"
    GRAPHIC_DESIGN = "graphic-design"
    LOGO_DESIGN = "logo-design"
    DIGITAL_DESIGN = "digital-design"
    PACKAGING_DESIGN = "packaging-design"
    DESIGN_AGENCIES = "design-agencies"
    DESIGN_CONCEPTS = "design-concepts"
    FULL_SERVICE_DESIGN = "full-service-design"
    
    # Marketing
    DIGITAL_MARKETING = "digital-marketing"
    SEO = "seo"
    PPC = "ppc"
    SOCIAL_MEDIA = "social-media-marketing"
    EMAIL_MARKETING = "email-marketing"
    CONTENT_MARKETING = "content-marketing"
    ADVERTISING = "advertising"
    MEDIA_BUYING = "media-buying-planning"
    BRANDING = "branding"
    CREATIVE = "creative"
    NAMING = "naming"
    PUBLIC_RELATIONS = "public-relations"
    MARKET_RESEARCH = "market-research"
    DIGITAL_STRATEGY = "digital-strategy"
    VIDEO_PRODUCTION = "video-production"
    EXPLAINER_VIDEOS = "explainer-videos"
    COMMERCIALS = "commercials"
    CORPORATE_VIDEOS = "corporate-videos"
    ANIMATION_2D = "2d-animation"
    ANIMATION_3D = "3d-animation"
    MOTION_GRAPHICS = "motion-graphics"
    
    # IT Services
    CYBERSECURITY = "cybersecurity"
    CLOUD_CONSULTING = "cloud-consulting"
    BI_BIG_DATA = "bi-and-big-data"
    IT_SUPPORT = "it-support"
    SYSTEMS_INTEGRATION = "systems-integration"
    ERP = "erp"
    AZURE = "azure"
    STAFF_AUGMENTATION = "staff-augmentation"
    PENETRATION_TESTING = "penetration-testing"
    SALESFORCE = "salesforce"
    AWS = "aws"
    MANAGED_SERVICE_PROVIDERS = "managed-service-providers"
    ACCOUNT_TAKEOVER_PREVENTION = "account-takeover-prevention"
    
    # Business Services
    HR_CONSULTING = "hr-consulting"
    ACCOUNTING = "accounting"
    LEGAL = "legal"
    SALES_OUTSOURCING = "sales-outsourcing"
    CUSTOMER_SUPPORT = "customer-support"
    LEAD_GENERATION = "lead-generation"
    LEAD_QUALIFICATION = "lead-qualification"
    BPO = "bpo"
    CALL_CENTERS = "call-centers"
    ANSWERING_SERVICES = "answering-services"
    OUTBOUND_CALL_CENTERS = "outbound-call-centers"
    PRIVATE_EQUITY = "private-equity"
    PAYROLL_PROCESSING = "payroll-processing"
    MERGERS_ACQUISITIONS = "mergers-acquisitions"
    WEALTH_ASSET_MANAGEMENT = "wealth-asset-management"
    APPOINTMENT_SETTING = "appointment-setting"
    VIRTUAL_RECEPTIONIST = "virtual-receptionist"
    VIRTUAL_ASSISTANT = "virtual-assistant"
    DATA_ENTRY = "data-entry"
    HR_RECRUITING = "hr-recruiting"
    HR_STAFFING = "hr-staffing"
    EXECUTIVE_SEARCH = "executive-search"

# Category display names - using the imported CATEGORY_NAMES from master_scraper
# This ensures consistency across files

# ============== MASTER SCRAPER ENDPOINT ==============

def run_master_scrape_background(categories, pages_per_category, save_to_db):
    """Background task for master scrape"""
    try:
        scraper = ClutchMasterScraper()
        results = scraper.scrape_all_categories(
            categories_to_scrape=categories,
            pages_per_category=pages_per_category
        )
        
        if save_to_db and results['companies']:
            for category, cat_companies in results['companies_by_category'].items():
                if cat_companies:
                    db_service.save_leads(cat_companies, category)
        
        logger.info(f"✅ Background master scrape complete: {results['total_companies']} companies")
    except Exception as e:
        logger.error(f"Background master scrape failed: {e}")

# ============== SINGLE CATEGORY SCRAPER ==============

@router.get("/clutch")
async def get_clutch_companies(
    category: ClutchCategory = Query(
        ClutchCategory.ARTIFICIAL_INTELLIGENCE, 
        description="Category to scrape from Clutch.co"
    ),
    pages: int = Query(3, description="Number of pages to scrape (1-10)", ge=1, le=10),
    scrape_profiles: bool = Query(False, description="Scrape individual company profiles for contact info (slower but gets phones, emails, etc.)"),
    save_to_db: bool = Query(True, description="Save results to database"),
    find_emails: bool = Query(False, description="Find emails for companies using email finder service"),
    analyze_ai: bool = Query(False, description="Run AI analysis")
):
    """
    Scrape companies from a specific Clutch.co category
    
    **Features:**
    - Scrape company listings from any category
    - Option to scrape individual profiles for contact info (phone, email, social links)
    - Save to database
    - Find emails using email finder service
    - Run AI analysis on companies
    
    **Note:** Setting `scrape_profiles=true` will take longer but gives you more complete data!
    """
    
    category_value = category.value
    category_name = CATEGORY_NAMES.get(category_value, category_value)
    
    logger.info(f"🎯 Scraping {category_name} ({category_value}), {pages} pages, profile scraping: {scrape_profiles}")
    
    # Use the category scraper function with profile scraping option
    # Make sure your scrape_category function accepts the scrape_profiles parameter
    companies = scrape_category(category_value, max_pages=pages, scrape_profiles=scrape_profiles)
    
    response_data = {
        "success": True,
        "category": category_value,
        "category_name": category_name,
        "pages_scraped": pages,
        "profiles_scraped": scrape_profiles,
        "total": len(companies),
        "data": companies[:20]  # Return first 20 as sample
    }
    
    # Add contact info statistics if profiles were scraped
    if scrape_profiles and companies:
        companies_with_phone = sum(1 for c in companies if c.get('phone') and c['phone'] != 'Not available')
        companies_with_email = sum(1 for c in companies if c.get('email') and c['email'] != 'Not available')
        companies_with_linkedin = sum(1 for c in companies if c.get('linkedin') and c['linkedin'] != 'Not available')
        companies_with_twitter = sum(1 for c in companies if c.get('twitter') and c['twitter'] != 'Not available')
        companies_with_facebook = sum(1 for c in companies if c.get('facebook') and c['facebook'] != 'Not available')
        
        response_data["contact_stats"] = {
            "with_phone": companies_with_phone,
            "with_email": companies_with_email,
            "with_linkedin": companies_with_linkedin,
            "with_twitter": companies_with_twitter,
            "with_facebook": companies_with_facebook,
            "total_companies": len(companies)
        }
        
        logger.info(f"📊 Contact stats: {companies_with_phone} phones, {companies_with_email} emails, {companies_with_linkedin} LinkedIn")
    
    # Save to database if requested
    if save_to_db and companies:
        db_result = db_service.save_leads(companies, category_value)
        logger.info(f"💾 Database: {db_result}")
        response_data["db_result"] = db_result
    
    # Optional: Find emails using email finder service
    if find_emails and companies:
        logger.info("🔍 Finding emails for companies...")
        emails_found = 0
        for i, company in enumerate(companies[:10]):  # Limit to 10 for performance
            if company.get('website') and company['website'] != 'Not available':
                try:
                    domain = company['website'].replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
                    logger.info(f"   [{i+1}/10] Searching emails for {company.get('name')} ({domain})")
                    emails = email_finder.find_emails_sync(company.get('name', ''), domain)
                    if emails:
                        company['found_emails'] = emails
                        emails_found += len(emails)
                        logger.info(f"      ✅ Found {len(emails)} emails")
                except Exception as e:
                    logger.error(f"      ❌ Error finding emails: {e}")
            time.sleep(1)  # Be nice to the email finder service
        response_data["emails_found"] = emails_found
    
    # Optional: AI analysis
    if analyze_ai and companies:
        logger.info("🤖 Running AI analysis on companies...")
        for i, company in enumerate(companies[:5]):  # Limit to 5 for performance
            try:
                logger.info(f"   [{i+1}/5] Analyzing {company.get('name')}")
                analysis = ai_analyzer.analyze_company(company)
                company['ai_analysis'] = analysis
            except Exception as e:
                logger.error(f"      ❌ Error in AI analysis: {e}")
        response_data["ai_analysis_completed"] = min(5, len(companies))
    
    # Add summary of data quality
    if companies:
        has_website = sum(1 for c in companies if c.get('website') and c['website'] != 'Not available')
        has_location = sum(1 for c in companies if c.get('location') and c['location'] != 'Unknown')
        has_rating = sum(1 for c in companies if c.get('rating') and c['rating'] != 'Not rated')
        
        response_data["data_quality"] = {
            "with_website": has_website,
            "with_location": has_location,
            "with_rating": has_rating,
            "with_reviews": sum(1 for c in companies if c.get('reviews') and c['reviews'] != '0')
        }
    
    return response_data

# ============== MAIN DIRECTORY SCRAPER ==============

@router.get("/all-companies")
async def get_all_companies(
    pages: int = Query(5, description="Number of pages to scrape (1-20)", ge=1, le=20),
    save_to_db: bool = Query(True, description="Save to database")
):
    """Scrape ALL companies from Clutch.co main directory (single source)"""
    
    logger.info(f"📚 Scraping main directory, {pages} pages...")
    
    companies = scrape_main_directory(max_pages=pages)
    
    # Auto-detect categories
    for company in companies:
        services_text = ' '.join(company.get('services', [])).lower()
        if 'ai' in services_text or 'artificial intelligence' in services_text:
            company['detected_category'] = 'artificial-intelligence'
        elif 'blockchain' in services_text:
            company['detected_category'] = 'blockchain'
        elif 'mobile' in services_text or 'ios' in services_text or 'android' in services_text:
            company['detected_category'] = 'mobile-app-development'
        elif 'web' in services_text:
            company['detected_category'] = 'web-development'
        else:
            company['detected_category'] = 'other'
    
    # Group by category
    categories = {}
    for company in companies:
        cat = company.get('detected_category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(company)
    
    # Save to database if requested
    saved_count = 0
    if save_to_db and companies:
        for cat, cat_companies in categories.items():
            if cat_companies:
                result = db_service.save_leads(cat_companies, cat)
                saved_count += result.get('saved', 0)
    
    return {
        "success": True,
        "pages_scraped": pages,
        "total_companies": len(companies),
        "categories_found": list(categories.keys()),
        "category_breakdown": {cat: len(companies) for cat, companies in categories.items()},
        "saved_to_db": saved_count,
        "sample_data": companies[:10]  # First 10 as sample
    }

# ============== DATABASE ENDPOINTS ==============

@router.get("/leads")
async def get_leads(
    category: Optional[str] = Query(None, description="Filter by category name"),
    min_score: int = Query(None, ge=0, le=100, description="Minimum lead score"),
    limit: int = Query(100, ge=1, le=1000, description="Number of leads to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get leads from database"""
    leads = db_service.get_leads(category, min_score)
    
    # Apply pagination
    paginated_leads = leads[offset:offset + limit]
    
    return {
        "success": True,
        "total": len(leads),
        "returned": len(paginated_leads),
        "offset": offset,
        "limit": limit,
        "category_filter": category,
        "data": [
            {
                "id": l.id,
                "company_name": l.company_name,
                "location": l.location,
                "rating": l.rating,
                "reviews": l.reviews,
                "email": l.email,
                "email_verified": getattr(l, 'email_verified', False),
                "phone": getattr(l, 'phone', ''),
                "website": l.website,
                "linkedin": getattr(l, 'linkedin', ''),
                "employees": getattr(l, 'employees', ''),
                "size_category": getattr(l, 'size_category', ''),
                "hourly_rate": getattr(l, 'hourly_rate', ''),
                "services": json.loads(l.services) if l.services else [],
                "category": l.category,
                "lead_score": l.lead_score,
                "created_at": l.created_at
            }
            for l in paginated_leads
        ]
    }


@router.get("/categories-list")
async def get_categories_list(
    search: Optional[str] = Query(None, description="Search categories"),
    limit: int = Query(100, description="Number of categories to return")
):
    """
    Get list of all available categories with search functionality
    """
    from app.scraper.master_scraper import ALL_CATEGORIES, CATEGORY_NAMES
    
    categories_list = []
    for cat_id, cat_name in CATEGORY_NAMES.items():
        categories_list.append({
            "id": cat_id,
            "name": cat_name,
            "url": f"https://clutch.co/developers/{cat_id}"
        })
    
    # Filter by search if provided
    if search:
        search_lower = search.lower()
        categories_list = [
            c for c in categories_list 
            if search_lower in c['name'].lower() or search_lower in c['id'].lower()
        ]
    
    # Group by prefix for organization
    development = [c for c in categories_list if c['id'] in [
        "artificial-intelligence", "blockchain", "web-developers", "software-development",
        "mobile-app-development", "iphone-app-development", "android-app-development",
        "ecommerce", "ar-vr", "iot", "ruby-on-rails", "shopify", "wordpress-developers",
        "drupal", "magento", "dotnet", "php", "wearables", "software-testing",
        "react-native", "python-django", "flutter", "laravel", "gaming-apps",
        "microsoft-sharepoint", "bigcommerce", "finance-apps", "webflow", "java", "woocommerce"
    ]]
    
    design = [c for c in categories_list if c['id'] in [
        "web-design", "user-experience", "product-design", "graphic-design",
        "logo-design", "digital-design", "packaging-design", "design-agencies",
        "design-concepts", "full-service-design"
    ]]
    
    marketing = [c for c in categories_list if c['id'] in [
        "digital-marketing", "seo", "ppc", "social-media-marketing", "email-marketing",
        "content-marketing", "advertising", "media-buying-planning", "branding",
        "creative", "naming", "public-relations", "market-research", "digital-strategy",
        "video-production", "explainer-videos", "commercials", "corporate-videos",
        "2d-animation", "3d-animation", "motion-graphics"
    ]]
    
    it_services = [c for c in categories_list if c['id'] in [
        "cybersecurity", "cloud-consulting", "bi-and-big-data", "it-support",
        "systems-integration", "erp", "azure", "staff-augmentation",
        "penetration-testing", "salesforce", "aws", "managed-service-providers",
        "account-takeover-prevention"
    ]]
    
    business = [c for c in categories_list if c['id'] in [
        "hr-consulting", "accounting", "legal", "sales-outsourcing", "customer-support",
        "lead-generation", "lead-qualification", "bpo", "call-centers",
        "answering-services", "outbound-call-centers", "private-equity",
        "payroll-processing", "mergers-acquisitions", "wealth-asset-management",
        "appointment-setting", "virtual-receptionist", "virtual-assistant",
        "data-entry", "hr-recruiting", "hr-staffing", "executive-search"
    ]]
    
    return {
        "success": True,
        "total": len(categories_list),
        "filtered": len(categories_list),
        "search": search,
        "categories": categories_list[:limit],
        "grouped": {
            "development": development[:limit//5],
            "design": design[:limit//5],
            "marketing": marketing[:limit//5],
            "it_services": it_services[:limit//5],
            "business": business[:limit//5]
        }
    }




@router.get("/leads/{lead_id}")
async def get_lead_by_id(lead_id: int):
    """Get a single lead by ID"""
    lead = db_service.db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "success": True,
        "data": {
            "id": lead.id,
            "company_name": lead.company_name,
            "location": lead.location,
            "rating": lead.rating,
            "reviews": lead.reviews,
            "email": lead.email,
            "phone": getattr(lead, 'phone', ''),
            "website": lead.website,
            "linkedin": getattr(lead, 'linkedin', ''),
            "employees": getattr(lead, 'employees', ''),
            "hourly_rate": getattr(lead, 'hourly_rate', ''),
            "services": json.loads(lead.services) if lead.services else [],
            "category": lead.category,
            "lead_score": lead.lead_score,
            "created_at": lead.created_at
        }
    }

# ============== EXPORT ENDPOINTS ==============


@router.get("/export/all-csv")
async def export_all_csv():
    """Export ALL leads to CSV without filters"""
    try:
        leads = db_service.get_leads()
        df = pd.DataFrame([{
            'id': l.id,
            'company_name': l.company_name,
            'website': l.website,
            'location': l.location,
            'rating': l.rating,
            'reviews': l.reviews,
            'email': l.email,
            'phone': l.phone,
            'employees': l.employees,
            'hourly_rate': l.hourly_rate,
            'category': l.category,
            'lead_score': l.lead_score,
            'created_at': l.created_at
        } for l in leads])
        
        csv_data = df.to_csv(index=False)
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=all_leads.csv"}
        )
    except Exception as e:
        return {"error": str(e)}



@router.get("/export/csv")
async def export_csv(
    category: Optional[CategoryEnum] = Query(
        None, 
        description="Filter by category (select from dropdown)"
    )
):
    """Export leads as CSV"""
    try:
        category_value = category.value if category else None
        leads = db_service.get_leads(category_value)
        csv_data = fixed_exporter.to_csv(leads)
        
        filename = f"leads_{category_value or 'all'}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_service.close()

@router.get("/export/excel")
async def export_excel(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Export leads as Excel"""
    try:
        leads = db_service.get_leads(category)
        excel_data = fixed_exporter.to_excel(leads)
        
        filename = f"leads_{category or 'all'}.xlsx"
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_service.close()

# ============== ENRICHMENT ENDPOINTS ==============

@router.post("/enrich/{lead_id}")
async def enrich_lead(
    lead_id: int,
    find_email: bool = Query(True, description="Find email addresses"),
    analyze: bool = Query(True, description="Run AI analysis"),
    background_tasks: BackgroundTasks = None
):
    """Enrich a single lead with email and AI analysis"""
    try:
        if background_tasks:
            background_tasks.add_task(enrichment_service.enrich_lead_sync, lead_id, find_email, analyze)
            return {"success": True, "message": f"Enrichment started for lead {lead_id}"}
        else:
            result = await enrichment_service.enrich_lead(lead_id, find_email, analyze)
            return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/enrich/batch")
async def enrich_batch(
    lead_ids: List[int] = Query(..., description="List of lead IDs to enrich"),
    find_email: bool = Query(True, description="Find email addresses"),
    analyze: bool = Query(True, description="Run AI analysis"),
    background_tasks: BackgroundTasks = None
):
    """Enrich multiple leads in batch"""
    try:
        if background_tasks:
            background_tasks.add_task(enrichment_service.enrich_batch_sync, lead_ids[:20], find_email, analyze)
            return {"success": True, "message": f"Batch enrichment started for {len(lead_ids[:20])} leads"}
        else:
            results = await enrichment_service.enrich_batch(lead_ids[:10], find_email, analyze)
            return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Batch enrichment error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/enrich-all")
async def enrich_all_leads(
    find_email: bool = Query(True, description="Find emails"),
    analyze: bool = Query(True, description="Run AI analysis"),
    limit: int = Query(50, description="Number of leads to enrich", ge=1, le=100),
    background_tasks: BackgroundTasks = None
):
    """Enrich all leads with emails and AI analysis"""
    try:
        leads = db_service.get_leads()
        lead_ids = [lead.id for lead in leads[:limit]]
        
        if background_tasks:
            background_tasks.add_task(enrichment_service.enrich_batch_sync, lead_ids, find_email, analyze)
            return {"success": True, "message": f"Enrichment started for {len(lead_ids)} leads"}
        else:
            results = await enrichment_service.enrich_batch(lead_ids, find_email, analyze)
            return {
                "success": True,
                "total_processed": len(results),
                "results": results
            }
    except Exception as e:
        logger.error(f"Enrich all error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_service.close()

# ============== UTILITY ENDPOINTS ==============

@router.get("/categories")
async def get_categories():
    """Get list of all available categories"""
    return {
        "success": True,
        "total_categories": len(CATEGORY_NAMES),
        "categories": [
            {"id": k, "name": v} 
            for k, v in sorted(CATEGORY_NAMES.items())
        ]
    }

@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        leads = db_service.get_leads()
        
        if not leads:
            return {"success": True, "total_leads": 0, "leads_with_email": 0, "avg_lead_score": 0, "categories": []}
        
        # Count by category
        category_counts = {}
        for lead in leads:
            cat = lead.category or 'unknown'
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        leads_with_email = sum(1 for l in leads if l.email and l.email.strip())
        leads_with_phone = sum(1 for l in leads if getattr(l, 'phone', None) and l.phone != 'Not available')
        leads_with_website = sum(1 for l in leads if l.website and l.website != 'Not available')
        leads_with_linkedin = sum(1 for l in leads if getattr(l, 'linkedin', None) and l.linkedin != 'Not available')
        
        avg_score = sum(l.lead_score or 0 for l in leads) / len(leads) if leads else 0
        
        return {
            "success": True,
            "total_leads": len(leads),
            "leads_with_email": leads_with_email,
            "leads_with_phone": leads_with_phone,
            "leads_with_website": leads_with_website,
            "leads_with_linkedin": leads_with_linkedin,
            "avg_lead_score": round(avg_score, 2),
            "categories": [{"category": k, "count": v} for k, v in category_counts.items()]
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_service.close()

@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: int):
    """Delete a lead from database"""
    try:
        lead = db_service.db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        db_service.db.delete(lead)
        db_service.db.commit()
        
        return {"success": True, "message": f"Lead {lead_id} deleted"}
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db_service.close()