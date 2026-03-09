from app.core.database import engine
from sqlalchemy import text

print("🚀 Adding missing columns to database...")

with engine.connect() as conn:
    # List of columns to add
    columns_to_add = [
        ("ADD COLUMN ai_analysis_summary TEXT", "ai_analysis_summary"),
        ("ADD COLUMN ai_grade VARCHAR(10)", "ai_grade"),
        ("ADD COLUMN email_verified BOOLEAN DEFAULT FALSE", "email_verified"),
        ("ADD COLUMN last_enriched TIMESTAMP", "last_enriched"),
        ("ADD COLUMN founded_year VARCHAR(10)", "founded_year")
    ]
    
    for col_sql, col_name in columns_to_add:
        try:
            conn.execute(text(f"ALTER TABLE leads {col_sql}"))
            conn.commit()
            print(f"✅ Added column: {col_name}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                print(f"⚠️ Column already exists: {col_name}")
            else:
                print(f"❌ Error adding {col_name}: {e}")

print("🎉 Database update complete!")