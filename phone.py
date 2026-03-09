from app.core.database import engine
from sqlalchemy import text

print("🚀 Adding phone column if missing...")

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE leads ADD COLUMN phone VARCHAR(50)"))
        conn.commit()
        print("✅ Added phone column")
    except Exception as e:
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            print("⚠️ Phone column already exists")
        else:
            print(f"❌ Error: {e}")

print("🎉 Done!")