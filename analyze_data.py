import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect('clutch.db')

# Load all data
df = pd.read_sql("SELECT * FROM leads", conn)

print("=" * 60)
print("📊 CLUTCH.CO DATA ANALYSIS")
print("=" * 60)

# Basic stats
print(f"\n📈 Total Companies: {len(df)}")
print(f"📊 Categories: {df['category'].nunique()}")
print(f"⭐ Average Rating: {df['rating'].astype(float).mean():.2f}")
print(f"📧 Companies with Email: {df['email'].notna().sum()}")
print(f"📞 Companies with Phone: {df[df['phone'] != 'Not available'].shape[0]}")

# Top categories
print("\n🏆 TOP 10 CATEGORIES:")
category_counts = df['category'].value_counts().head(10)
for cat, count in category_counts.items():
    print(f"   {cat}: {count} companies")

# Top locations
print("\n🌍 TOP 10 LOCATIONS:")
location_counts = df['location'].value_counts().head(10)
for loc, count in location_counts.items():
    print(f"   {loc}: {count} companies")

# Rating distribution
print("\n⭐ RATING DISTRIBUTION:")
rating_bins = [0, 3, 3.5, 4, 4.5, 4.8, 5]
rating_labels = ['<3', '3-3.5', '3.5-4', '4-4.5', '4.5-4.8', '4.8-5']
df['rating_group'] = pd.cut(df['rating'].astype(float), bins=rating_bins, labels=rating_labels)
rating_dist = df['rating_group'].value_counts().sort_index()
for rating, count in rating_dist.items():
    print(f"   {rating}: {count} companies")

# Export summary to CSV
summary = pd.DataFrame({
    'Category': category_counts.index,
    'Count': category_counts.values
})
summary.to_csv('category_summary.csv', index=False)
print(f"\n✅ Summary exported to category_summary.csv")

conn.close()