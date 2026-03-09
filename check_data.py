import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('clutch.db')

# Check what's in the database
df = pd.read_sql("SELECT category, COUNT(*) as count FROM leads GROUP BY category", conn)
print("📊 Companies by category:")
print(df)

# Show total
total = pd.read_sql("SELECT COUNT(*) as total FROM leads", conn)
print(f"\n✅ Total companies: {total['total'][0]}")

# Show sample
sample = pd.read_sql("SELECT company_name, category, rating FROM leads LIMIT 5", conn)
print("\n📋 Sample companies:")
print(sample)

conn.close()