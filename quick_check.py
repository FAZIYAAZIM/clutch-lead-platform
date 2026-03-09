# complete_check.py
import sqlite3
import pandas as pd

conn = sqlite3.connect('clutch.db')

# Get all artificial-intelligence companies
df = pd.read_sql("SELECT * FROM leads WHERE category='artificial-intelligence'", conn)

print("=" * 60)
print("📊 ARTIFICIAL INTELLIGENCE - COMPLETE DATA")
print("=" * 60)

print(f"\n📈 Total companies: {len(df)}")

print(f"\n📞 Companies with phone: {df[df['phone'] != 'Not available'].shape[0]}")
print(f"📧 Companies with email: {df['email'].notna().sum()}")
print(f"🔗 Companies with LinkedIn: {df[df['linkedin'] != 'Not available'].shape[0]}")
print(f"🐦 Companies with Twitter: {df[df['twitter'] != 'Not available'].shape[0]}")
print(f"📘 Companies with Facebook: {df[df['facebook'] != 'Not available'].shape[0]}")

print("\n📋 Sample companies with LinkedIn:")
linkedin_companies = df[df['linkedin'] != 'Not available'].head(10)
for idx, row in linkedin_companies.iterrows():
    print(f"   • {row['company_name']}: {row['linkedin']}")

print("\n📧 Companies with email:")
email_companies = df[df['email'].notna()]
for idx, row in email_companies.iterrows():
    print(f"   • {row['company_name']}: {row['email']}")

conn.close()