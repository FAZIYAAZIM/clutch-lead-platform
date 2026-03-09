import sqlite3
import pandas as pd
import time

def check_progress():
    conn = sqlite3.connect('clutch.db')
    
    # Get counts by category
    df = pd.read_sql("""
        SELECT 
            category, 
            COUNT(*) as total,
            SUM(CASE WHEN phone != 'Not available' THEN 1 ELSE 0 END) as with_phone,
            SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as with_email,
            SUM(CASE WHEN linkedin != 'Not available' THEN 1 ELSE 0 END) as with_linkedin
        FROM leads 
        GROUP BY category
    """, conn)
    
    print("\n" + "=" * 70)
    print("📊 CURRENT SCRAPING PROGRESS")
    print("=" * 70)
    
    total_companies = 0
    for _, row in df.iterrows():
        print(f"\n📌 {row['category']}:")
        print(f"   Total: {row['total']} companies")
        print(f"   📞 Phone: {row['with_phone']}")
        print(f"   📧 Email: {row['with_email']}")
        print(f"   🔗 LinkedIn: {row['with_linkedin']}")
        total_companies += row['total']
    
    print(f"\n✅ GRAND TOTAL: {total_companies} companies")
    print("=" * 70)
    
    conn.close()
    
    return total_companies

# Run it
check_progress()