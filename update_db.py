from app.core.database import engine
from sqlalchemy import text

print("🚀 Updating database with new columns...")

with engine.connect() as conn:
    # List of columns to add
    columns_to_add = [
        "ADD COLUMN twitter VARCHAR(255)",
        "ADD COLUMN facebook VARCHAR(255)",
        "ADD COLUMN size_category VARCHAR(50)",
        "ADD COLUMN description TEXT",
        "ADD COLUMN ai_insights TEXT"
    ]
    
    for col in columns_to_add:
        try:
            conn.execute(text(f"ALTER TABLE leads {col}"))
            conn.commit()
            print(f"✅ Added column: {col}")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print(f"⚠️ Column already exists: {col}")
            else:
                print(f"❌ Error adding {col}: {e}")

print("🎉 Database update complete!")