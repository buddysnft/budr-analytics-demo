# 🎯 BUDR Analytics Dashboard - DEMO

**This is a fully functional demo** showing what your analytics dashboard will look like with YOUR real data from Dutchie.

## What You're Looking At

This demo dashboard includes:

✅ **30 days of realistic sample data**
- 7 BUDR locations (Montville, Danbury Mill Plain, Budr Holding 6, Tolland, Vernon, Danbury, West Hartford)
- 8 CT competitor dispensaries (ZEN LEAF, BLUEPOINT, FINE FETTLE, etc.)
- $7.3M in total transactions
- 446 unique products
- All 5 priority KPIs calculated

✅ **All 8 tabs fully functional**
1. 🎯 Performance Overview - Top 5 KPIs at a glance
2. 💰 Revenue Deep Dive - Revenue trends and breakdowns
3. 👥 Customer Intelligence - Customer segments and behavior
4. 📦 Product Performance - Top sellers, slow movers, dead stock
5. 💵 Pricing & Margin - Pricing analysis and margin optimization
6. 📦 Inventory Management - Stock levels and velocity
7. ⏰ Time Analysis - Hourly/daily patterns
8. 🏁 Competitor Benchmarking - BUDR vs CT market

✅ **Interactive filters**
- Date ranges (Last 7/30/60/90 days, MTD, QTD, YTD, Custom)
- Location selection
- Category filtering
- Customer type (Med/Rec)
- Channel (Pre-order/Walk-in)

## 🚀 Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### Deploy to Streamlit Cloud (Recommended)

1. Fork/upload this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repo
5. Set main file path: `app.py`
6. Click "Deploy"

You'll get a public URL like: `https://budr-analytics-demo.streamlit.app`

**No database setup required!** All data is pre-generated and included.

## 📊 What This Proves

This demo shows you:

1. **The dashboard works** - Not a mockup, not a pitch deck. This is the real thing.
2. **The insights are valuable** - See BUDR vs competitors, margins by category, customer segments, etc.
3. **It's ready for YOUR data** - Just plug in your Dutchie API and this runs with live data.

## 🔌 Ready for Live Data?

When you're ready to connect to your actual Dutchie data:

1. **Dutchie API Integration** (48 hours)
   - Connect to your Dutchie account
   - Pull orders, products, customers, inventory
   - Automated daily sync

2. **Database Setup** (included)
   - PostgreSQL database (cloud-hosted)
   - Secure data storage
   - Fast query performance

3. **Custom Domain & Security**
   - Deploy to your own domain
   - Password protection
   - SSL/HTTPS enabled

See `DEPLOYMENT.md` for technical details.

## 🎯 Key Metrics Shown

### KPI #1: Average Ticket
- Overall average ticket
- Medical vs Recreational breakdown
- 30-day trend with alerts

### KPI #2: Price per Unit by Category
- Flower, Pre-Rolls, Edibles, Vapes, etc.
- Compare across categories
- Spot pricing opportunities

### KPI #3: Inventory Velocity
- Days to sellthrough by category
- Units per day
- Identify slow movers

### KPI #4: Gross Margin
- Overall margin percentage
- Margin by category
- Profit optimization insights

### KPI #5: Pre-order vs Walk-in
- Transaction counts
- Revenue split
- Average ticket comparison

Plus: Revenue trends, customer segments, top/bottom products, competitor pricing, hourly patterns, and more!

## 📁 Project Structure

```
dashboard-demo/
├── app.py                      # Main Streamlit app (DEMO VERSION)
├── generate_sample_data.py     # Data generation script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── DEPLOYMENT.md               # How to deploy with real data
├── data/                       # Pre-generated sample data
│   ├── products.csv
│   ├── daily_kpis.csv
│   ├── category_kpis.csv
│   ├── sku_kpis.csv
│   ├── competitor_metrics.csv
│   ├── budr_position.csv
│   ├── locations.json
│   └── competitors.json
├── utils/
│   └── demo_data_loader.py     # Loads CSV/JSON instead of database
├── tabs/                       # 8 dashboard tabs
├── components/                 # Reusable chart components
├── config/                     # Configuration
└── .streamlit/                 # Streamlit theme
```

## 💡 What Makes This Different

Most analytics pitches show you:
- ❌ Static screenshots
- ❌ PowerPoint mockups
- ❌ "Trust us, we can build it"

We're showing you:
- ✅ A working dashboard RIGHT NOW
- ✅ Real insights from realistic data
- ✅ "Here it is, click around, use it"

**This is what you get.** No surprises.

## 🤝 Next Steps

1. **Explore the demo** - Click through all 8 tabs, try the filters
2. **Share with your team** - Get feedback on what metrics matter most
3. **Contact us** - Ready to connect your Dutchie API and go live

Questions? Want to customize? Ready to deploy with live data?

Let's talk: [your contact info]

---

**BUDR Analytics Dashboard Demo v1.0**  
Built for BUDR by [Your Company]  
Powered by Streamlit | Data from Dutchie API (coming soon)
