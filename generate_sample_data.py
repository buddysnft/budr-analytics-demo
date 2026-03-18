"""
Generate Realistic Sample Data for BUDR Analytics Demo
Creates 30 days of transaction data for 7 BUDR locations + 8 CT competitors
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# BUDR Locations
BUDR_LOCATIONS = [
    {"id": 1, "name": "Montville", "is_active": True},
    {"id": 2, "name": "Danbury Mill Plain", "is_active": True},
    {"id": 3, "name": "Budr Holding 6", "is_active": True},
    {"id": 4, "name": "Tolland", "is_active": True},
    {"id": 5, "name": "Vernon", "is_active": True},
    {"id": 6, "name": "Danbury", "is_active": True},
    {"id": 7, "name": "West Hartford", "is_active": True}
]

# CT Competitors
COMPETITORS = [
    {"id": 101, "name": "ZEN LEAF", "location": "West Hartford, CT"},
    {"id": 102, "name": "BLUEPOINT", "location": "Westport, CT"},
    {"id": 103, "name": "FINE FETTLE", "location": "Stamford, CT"},
    {"id": 104, "name": "STILL RIVER", "location": "Newtown, CT"},
    {"id": 105, "name": "CURALEAF", "location": "Milford, CT"},
    {"id": 106, "name": "THE BOTANIST", "location": "Danbury, CT"},
    {"id": 107, "name": "AHLOT", "location": "Rocky Hill, CT"},
    {"id": 108, "name": "AFFINITY", "location": "New Haven, CT"}
]

# Product Categories
CATEGORIES = ["Flower", "Pre-Rolls", "Edibles", "Vapes", "Concentrates", "Topicals", "Tinctures"]

# Brands (realistic CT cannabis brands)
BRANDS = [
    "BUDR House", "Cresco", "Verano", "Rhythm", "Good News", 
    "Curaleaf", "Select", "The Botanist", "Matter", "AGL",
    "Incredibles", "Wana", "Smokiez", "STIIIZY", "Heavy Hitters"
]

def generate_product_name(category, brand):
    """Generate realistic product names"""
    strain_names = ["Blue Dream", "Wedding Cake", "Gelato", "Zkittlez", "Runtz", 
                    "Sour Diesel", "OG Kush", "Girl Scout Cookies", "Purple Haze", "Jack Herer",
                    "Trainwreck", "Northern Lights", "Pineapple Express", "White Widow", "Granddaddy Purple"]
    
    if category == "Flower":
        return f"{brand} {random.choice(strain_names)} {random.choice(['3.5g', '7g', '14g', '28g'])}"
    elif category == "Pre-Rolls":
        return f"{brand} {random.choice(strain_names)} {random.choice(['1g', '3-pack', '5-pack'])}"
    elif category == "Edibles":
        return f"{brand} {random.choice(['Gummies', 'Chocolates', 'Mints', 'Cookies'])} {random.choice(['10mg', '100mg', '200mg'])}"
    elif category == "Vapes":
        return f"{brand} {random.choice(strain_names)} {random.choice(['0.5g', '1g'])} Cart"
    elif category == "Concentrates":
        return f"{brand} {random.choice(strain_names)} {random.choice(['Wax', 'Shatter', 'Live Resin'])} 1g"
    elif category == "Topicals":
        return f"{brand} {random.choice(['Relief', 'Recovery', 'Sleep'])} {random.choice(['Lotion', 'Balm', 'Patch'])}"
    else:  # Tinctures
        return f"{brand} {random.choice(['CBD', 'THC', 'CBN'])} Tincture {random.choice(['500mg', '1000mg'])}"

# Generate Products (50+ per location, but many overlap)
products = []
product_id = 1

for location in BUDR_LOCATIONS:
    for _ in range(random.randint(50, 80)):
        category = random.choice(CATEGORIES)
        brand = random.choice(BRANDS)
        
        products.append({
            "id": product_id,
            "location_id": location["id"],
            "name": generate_product_name(category, brand),
            "category": category,
            "brand": brand,
            "is_active": random.random() > 0.05  # 5% inactive
        })
        product_id += 1

products_df = pd.DataFrame(products)

# Generate 30 days of daily KPIs
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

daily_kpis = []

for location in BUDR_LOCATIONS:
    # Each location has different baseline metrics
    base_revenue = random.randint(15000, 45000)  # Daily revenue
    base_transactions = random.randint(100, 400)
    
    for date in date_range:
        # Add weekly seasonality (weekends are busier)
        day_of_week = date.dayofweek
        weekend_multiplier = 1.3 if day_of_week in [5, 6] else 1.0
        
        # Add some random variation
        revenue_mult = weekend_multiplier * random.uniform(0.85, 1.15)
        transactions = int(base_transactions * revenue_mult)
        total_revenue = base_revenue * revenue_mult
        
        # Calculate other metrics
        avg_ticket = total_revenue / transactions if transactions > 0 else 0
        
        # Medical vs Recreational split (70% rec, 30% med)
        rec_transactions = int(transactions * 0.7)
        med_transactions = transactions - rec_transactions
        rec_revenue = total_revenue * 0.75
        med_revenue = total_revenue - rec_revenue
        
        rec_avg_ticket = rec_revenue / rec_transactions if rec_transactions > 0 else 0
        med_avg_ticket = med_revenue / med_transactions if med_transactions > 0 else 0
        
        # Pre-order vs Walk-in (60% preorder)
        preorder_transactions = int(transactions * 0.6)
        walkin_transactions = transactions - preorder_transactions
        preorder_revenue = total_revenue * 0.65
        walkin_revenue = total_revenue - preorder_revenue
        
        preorder_avg_ticket = preorder_revenue / preorder_transactions if preorder_transactions > 0 else 0
        walkin_avg_ticket = walkin_revenue / walkin_transactions if walkin_transactions > 0 else 0
        
        # Unique customers (roughly 70% of transactions)
        unique_customers = int(transactions * 0.7)
        
        daily_kpis.append({
            "location_id": location["id"],
            "kpi_date": date.strftime('%Y-%m-%d'),
            "total_revenue": round(total_revenue, 2),
            "total_transactions": transactions,
            "avg_ticket": round(avg_ticket, 2),
            "unique_customers": unique_customers,
            "rec_transactions": rec_transactions,
            "rec_revenue": round(rec_revenue, 2),
            "rec_avg_ticket": round(rec_avg_ticket, 2),
            "med_transactions": med_transactions,
            "med_revenue": round(med_revenue, 2),
            "med_avg_ticket": round(med_avg_ticket, 2),
            "preorder_transactions": preorder_transactions,
            "preorder_revenue": round(preorder_revenue, 2),
            "preorder_avg_ticket": round(preorder_avg_ticket, 2),
            "walkin_transactions": walkin_transactions,
            "walkin_revenue": round(walkin_revenue, 2),
            "walkin_avg_ticket": round(walkin_avg_ticket, 2)
        })

daily_kpis_df = pd.DataFrame(daily_kpis)

# Generate Category KPIs
category_kpis = []

for location in BUDR_LOCATIONS:
    for date in date_range:
        for category in CATEGORIES:
            # Revenue distribution by category
            category_weights = {
                "Flower": 0.35,
                "Pre-Rolls": 0.15,
                "Edibles": 0.20,
                "Vapes": 0.18,
                "Concentrates": 0.07,
                "Topicals": 0.03,
                "Tinctures": 0.02
            }
            
            # Get base revenue for this location/date
            base_row = daily_kpis_df[
                (daily_kpis_df['location_id'] == location['id']) & 
                (daily_kpis_df['kpi_date'] == date.strftime('%Y-%m-%d'))
            ]
            
            if base_row.empty:
                continue
                
            total_rev = base_row['total_revenue'].iloc[0]
            category_revenue = total_rev * category_weights.get(category, 0.1) * random.uniform(0.9, 1.1)
            
            # Units sold (depends on category)
            if category == "Flower":
                units = int(category_revenue / random.uniform(30, 60))
                avg_price_per_unit = category_revenue / units if units > 0 else 0
                units_per_day = units
            elif category == "Pre-Rolls":
                units = int(category_revenue / random.uniform(8, 15))
                avg_price_per_unit = category_revenue / units if units > 0 else 0
                units_per_day = units
            elif category == "Edibles":
                units = int(category_revenue / random.uniform(15, 30))
                avg_price_per_unit = category_revenue / units if units > 0 else 0
                units_per_day = units
            elif category == "Vapes":
                units = int(category_revenue / random.uniform(25, 50))
                avg_price_per_unit = category_revenue / units if units > 0 else 0
                units_per_day = units
            else:
                units = int(category_revenue / random.uniform(20, 40))
                avg_price_per_unit = category_revenue / units if units > 0 else 0
                units_per_day = units
            
            # Margin varies by category
            margin_ranges = {
                "Flower": (0.35, 0.45),
                "Pre-Rolls": (0.40, 0.50),
                "Edibles": (0.30, 0.40),
                "Vapes": (0.25, 0.35),
                "Concentrates": (0.30, 0.40),
                "Topicals": (0.35, 0.45),
                "Tinctures": (0.40, 0.50)
            }
            
            margin_pct = random.uniform(*margin_ranges.get(category, (0.30, 0.40)))
            gross_profit = category_revenue * margin_pct
            
            # Inventory velocity (days to sellthrough)
            days_to_sellthrough = random.uniform(5, 30) if category != "Flower" else random.uniform(7, 21)
            
            category_kpis.append({
                "location_id": location["id"],
                "kpi_date": date.strftime('%Y-%m-%d'),
                "category": category,
                "total_revenue": round(category_revenue, 2),
                "units_sold": units,
                "avg_price_per_unit": round(avg_price_per_unit, 2),
                "gross_margin_pct": round(margin_pct * 100, 2),
                "gross_profit": round(gross_profit, 2),
                "units_per_day": round(units_per_day, 2),
                "days_to_sellthrough": round(days_to_sellthrough, 2)
            })

category_kpis_df = pd.DataFrame(category_kpis)

# Generate SKU-level KPIs (sample for top products)
sku_kpis = []

# Top 20 products per location
for location in BUDR_LOCATIONS:
    location_products = products_df[products_df['location_id'] == location['id']].sample(min(20, len(products_df)))
    
    for _, product in location_products.iterrows():
        for date in date_range:
            # Get category revenue for this date
            cat_row = category_kpis_df[
                (category_kpis_df['location_id'] == location['id']) & 
                (category_kpis_df['kpi_date'] == date.strftime('%Y-%m-%d')) &
                (category_kpis_df['category'] == product['category'])
            ]
            
            if cat_row.empty:
                continue
            
            # This SKU gets a fraction of category revenue
            sku_revenue = cat_row['total_revenue'].iloc[0] * random.uniform(0.01, 0.15)
            units = int(sku_revenue / random.uniform(10, 50))
            
            sku_kpis.append({
                "location_id": location["id"],
                "product_id": product["id"],
                "kpi_date": date.strftime('%Y-%m-%d'),
                "revenue": round(sku_revenue, 2),
                "units_sold": units,
                "avg_price": round(sku_revenue / units if units > 0 else 0, 2),
                "gross_margin_pct": round(random.uniform(25, 50), 2),
                "units_per_day": round(units, 2)
            })

sku_kpis_df = pd.DataFrame(sku_kpis)

# Generate Competitor Data (current snapshot)
competitor_metrics = []

for comp in COMPETITORS:
    competitor_metrics.append({
        "dispensary_id": comp["id"],
        "metric_date": end_date.strftime('%Y-%m-%d'),
        "total_products": random.randint(150, 400),
        "avg_flower_price_per_gram": round(random.uniform(8, 18), 2),
        "avg_edible_price": round(random.uniform(15, 35), 2),
        "avg_vape_price": round(random.uniform(30, 60), 2),
        "active_deals_count": random.randint(5, 25),
        "out_of_stock_pct": round(random.uniform(5, 25), 2)
    })

competitor_metrics_df = pd.DataFrame(competitor_metrics)

# BUDR Competitive Position
budr_position = []

# Calculate BUDR averages
budr_avg_flower = category_kpis_df[category_kpis_df['category'] == 'Flower']['avg_price_per_unit'].mean()
budr_avg_edible = category_kpis_df[category_kpis_df['category'] == 'Edibles']['avg_price_per_unit'].mean()
budr_avg_vape = category_kpis_df[category_kpis_df['category'] == 'Vapes']['avg_price_per_unit'].mean()

market_avg_flower = competitor_metrics_df['avg_flower_price_per_gram'].mean()
market_avg_edible = competitor_metrics_df['avg_edible_price'].mean()
market_avg_vape = competitor_metrics_df['avg_vape_price'].mean()

for category in CATEGORIES:
    if category == "Flower":
        budr_price = budr_avg_flower
        market_price = market_avg_flower
    elif category == "Edibles":
        budr_price = budr_avg_edible
        market_price = market_avg_edible
    elif category == "Vapes":
        budr_price = budr_avg_vape
        market_price = market_avg_vape
    else:
        budr_price = category_kpis_df[category_kpis_df['category'] == category]['avg_price_per_unit'].mean()
        market_price = budr_price * random.uniform(0.9, 1.1)
    
    price_vs_market = ((budr_price - market_price) / market_price * 100) if market_price > 0 else 0
    
    budr_product_count = len(products_df[products_df['category'] == category])
    market_avg_count = competitor_metrics_df['total_products'].mean() / len(CATEGORIES)
    assortment_vs_market = ((budr_product_count - market_avg_count) / market_avg_count * 100) if market_avg_count > 0 else 0
    
    budr_position.append({
        "category": category,
        "analysis_date": end_date.strftime('%Y-%m-%d'),
        "budr_avg_price": round(budr_price, 2),
        "market_avg_price": round(market_price, 2),
        "price_vs_market_pct": round(price_vs_market, 2),
        "budr_product_count": int(budr_product_count),
        "market_avg_product_count": int(market_avg_count),
        "assortment_vs_market_pct": round(assortment_vs_market, 2)
    })

budr_position_df = pd.DataFrame(budr_position)

# Save all data files
print("Saving sample data files...")

products_df.to_csv('data/products.csv', index=False)
daily_kpis_df.to_csv('data/daily_kpis.csv', index=False)
category_kpis_df.to_csv('data/category_kpis.csv', index=False)
sku_kpis_df.to_csv('data/sku_kpis.csv', index=False)
competitor_metrics_df.to_csv('data/competitor_metrics.csv', index=False)
budr_position_df.to_csv('data/budr_position.csv', index=False)

# Save locations and competitors as JSON
with open('data/locations.json', 'w') as f:
    json.dump(BUDR_LOCATIONS, f, indent=2)

with open('data/competitors.json', 'w') as f:
    json.dump(COMPETITORS, f, indent=2)

print(f"""
✅ Sample data generated successfully!

Files created:
- products.csv ({len(products_df)} products)
- daily_kpis.csv ({len(daily_kpis_df)} records)
- category_kpis.csv ({len(category_kpis_df)} records)
- sku_kpis.csv ({len(sku_kpis_df)} records)
- competitor_metrics.csv ({len(competitor_metrics_df)} records)
- budr_position.csv ({len(budr_position_df)} records)
- locations.json (7 BUDR locations)
- competitors.json (8 CT competitors)

Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} (30 days)
Total revenue generated: ${daily_kpis_df['total_revenue'].sum():,.2f}
""")
