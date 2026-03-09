from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, scrape, outreach, dashboard
from app.core.database import Base, engine
from app.models import user, lead  # Import lead model

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clutch Lead Platform",
    description="🚀 Ultimate B2B Lead Generation Platform - AI-powered lead generation from Clutch.co",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraper"])
app.include_router(outreach.router, prefix="/outreach", tags=["Outreach"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {
        "message": "🚀 Clutch Lead Platform API",
        "version": "2.0.0",
        "description": "AI-powered B2B lead generation from Clutch.co",
        "documentation": "/docs",
        "authentication": {
            "/auth/register": "📝 User registration",
            "/auth/login": "🔑 User login",
            "/auth/profile": "👤 User profile",
            "/auth/logout": "🚪 User logout"
        },
        "scraper": {
            # Single Category Scraper
            "/scrape/clutch?category=X&pages=Y": "🕷️ Scrape companies from specific category",
            
            # Master Scraper (ALL categories)
            "/scrape/master-scrape": "⚡ Scrape ALL categories (background job)",
            
            # Database Endpoints
            "/scrape/leads": "📋 View all scraped leads (with pagination)",
            "/scrape/leads/{id}": "🔍 Get lead by ID",
            "/scrape/categories": "📂 List all available categories",
            "/scrape/stats": "📊 Database statistics",
            "/scrape/leads/{id} (DELETE)": "🗑️ Delete a lead",
            
            # Export Endpoints
            "/scrape/export/csv?category=X": "📥 Export leads as CSV",
            "/scrape/export/excel?category=X": "📥 Export leads as Excel",
            "/scrape/export/all-csv": "📥 Export ALL leads as CSV",
            
            # CRM Integration
            "/scrape/crm/sync": "🔄 Sync leads to CRM",
            
            # Enrichment Endpoints
            "/scrape/enrich/{id}": "✨ Enrich a single lead (find emails, AI analysis)",
            "/scrape/enrich/batch": "✨ Enrich multiple leads",
            "/scrape/enrich-all": "✨ Enrich all leads",
            
            # Main Directory Scraper
            "/scrape/all-companies": "🌐 Scrape from main directory"
        },
        "outreach": {
            "/outreach/create-list": "🎯 Create targeted outreach list",
            "/outreach/templates": "📧 Get email templates",
            "/outreach/stats": "📈 Outreach statistics"
        },
        "dashboard": {
            "/dashboard": "📊 Interactive analytics dashboard",
            "/dashboard/stats": "📉 Raw dashboard data"
        },
        "features": [
            "✅ Scrape 96+ categories from Clutch.co",
            "✅ Profile scraping for phones, emails, LinkedIn",
            "✅ AI-powered lead enrichment",
            "✅ CSV/Excel export",
            "✅ CRM synchronization",
            "✅ Outreach list generator",
            "✅ Interactive dashboard",
            "✅ Background job processing"
        ],
        "quick_start": {
            "scrape_all": {
                "method": "POST",
                "url": "/scrape/master-scrape?pages_per_category=2&save_to_db=true",
                "description": "Start scraping ALL categories in background"
            },
            "export_csv": {
                "method": "GET",
                "url": "/scrape/export/all-csv",
                "description": "Export all leads as CSV"
            },
            "view_dashboard": {
                "method": "GET",
                "url": "/dashboard",
                "description": "View interactive analytics dashboard"
            },
            "create_outreach": {
                "method": "POST",
                "url": "/outreach/create-list?categories=artificial-intelligence&min_rating=4.5&include_with_email=true",
                "description": "Create targeted outreach list"
            },
            "enrich_lead": {
                "method": "POST",
                "url": "/scrape/enrich/1?find_email=true&analyze=true",
                "description": "Enrich a specific lead"
            }
        },
        "note": "📌 For complete API documentation with interactive testing, visit /docs"
    }