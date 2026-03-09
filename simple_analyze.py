import sqlite3
import pandas as pd

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
print(f"🌐 Companies with Website: {df[df['website'] != 'Not available'].shape[0]}")
print(f"🔗 Companies with LinkedIn: {df[df['linkedin'] != 'Not available'].shape[0]}")

# Top categories
print("\n🏆 TOP CATEGORIES:")
category_counts = df['category'].value_counts()
for cat, count in category_counts.items():
    print(f"   {cat}: {count} companies")

# Top locations
print("\n🌍 TOP LOCATIONS:")
location_counts = df['location'].value_counts().head(15)
for loc, count in location_counts.items():
    print(f"   {loc}: {count} companies")

# Rating distribution
print("\n⭐ RATING DISTRIBUTION:")
rating_bins = [0, 3, 3.5, 4, 4.5, 4.8, 5.1]
rating_labels = ['<3.0', '3.0-3.5', '3.5-4.0', '4.0-4.5', '4.5-4.8', '4.8-5.0']
df['rating_clean'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
df['rating_group'] = pd.cut(df['rating_clean'], bins=rating_bins, labels=rating_labels, right=False)
rating_dist = df['rating_group'].value_counts().sort_index()
for rating, count in rating_dist.items():
    percentage = (count / len(df)) * 100
    print(f"   {rating}: {count} companies ({percentage:.1f}%)")

# Company size distribution
print("\n🏢 COMPANY SIZE:")
size_counts = df['size_category'].value_counts()
for size, count in size_counts.items():
    if size and size != 'Unknown':
        percentage = (count / len(df)) * 100
        print(f"   {size}: {count} companies ({percentage:.1f}%)")

# Hourly rate distribution
print("\n💰 HOURLY RATE:")
rate_counts = df['hourly_rate'].value_counts().head(10)
for rate, count in rate_counts.items():
    if rate and rate != 'Not specified':
        print(f"   {rate}: {count} companies")

# Export summaries to CSV
print("\n📁 Exporting summaries...")

# Category summary
category_summary = pd.DataFrame({
    'Category': category_counts.index,
    'Count': category_counts.values,
    'Percentage': (category_counts.values / len(df) * 100).round(1)
})
category_summary.to_csv('category_summary.csv', index=False)
print(f"   ✅ category_summary.csv saved")

# Location summary
location_summary = pd.DataFrame({
    'Location': location_counts.index,
    'Count': location_counts.values
})
location_summary.to_csv('location_summary.csv', index=False)
print(f"   ✅ location_summary.csv saved")

# Full data export with analysis
df['has_email'] = df['email'].notna()
df['has_phone'] = df['phone'] != 'Not available'
df['has_website'] = df['website'] != 'Not available'
df['has_linkedin'] = df['linkedin'] != 'Not available'

# Save enhanced dataset
df.to_csv('all_companies_with_analysis.csv', index=False)
print(f"   ✅ all_companies_with_analysis.csv saved")

print("\n" + "=" * 60)
print(f"✅ Analysis complete! Total companies: {len(df)}")
print("=" * 60)

conn.close()