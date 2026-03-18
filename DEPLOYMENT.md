# 🚀 Deployment Guide - From Demo to Live Data

This guide explains how to take this demo dashboard and deploy it with YOUR real Dutchie data.

## Current State: DEMO Mode

✅ What works now:
- All 8 tabs display properly
- All filters functional
- Uses realistic sample data from CSV/JSON files
- No database required
- Deploys to Streamlit Cloud in 5 minutes

❌ What's missing:
- Connection to your actual Dutchie API
- Real transaction data
- Automated daily updates

## Option 1: Quick Deploy (Demo as-is)

**Time: 5 minutes**  
**Cost: $0**  
**Purpose: Show stakeholders, get feedback**

### Steps:

1. **Upload to GitHub**
   ```bash
   cd dashboard-demo
   git init
   git add .
   git commit -m "BUDR Analytics Demo"
   git remote add origin https://github.com/yourusername/budr-analytics-demo.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repo: `budr-analytics-demo`
   - Main file: `app.py`
   - Click "Deploy"

3. **Share the URL**
   - Get public URL: `https://budr-analytics-demo.streamlit.app`
   - Share with team/stakeholders
   - No login required (demo data is safe to share)

**Result:** Working demo dashboard that anyone can view and interact with.

---

## Option 2: Deploy with Live Dutchie Data

**Time: 48-72 hours**  
**Cost: ~$50-100/month (database + hosting)**  
**Purpose: Production-ready dashboard with real data**

### Phase 1: Dutchie API Integration (24 hours)

#### 1.1 Get Dutchie API Credentials

Contact your Dutchie account manager or use the Dutchie Developer Portal:
- API Key
- API Secret
- Store IDs for each location

#### 1.2 Build Data Pipeline

Create `etl/dutchie_sync.py`:

```python
"""
Dutchie API Integration
Pulls data daily and loads into PostgreSQL
"""
import requests
from datetime import datetime, timedelta

DUTCHIE_API = "https://dutchie.com/api/v1"
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

def fetch_orders(store_id, start_date, end_date):
    """Fetch orders from Dutchie API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "store_id": store_id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.get(f"{DUTCHIE_API}/orders", headers=headers, params=params)
    return response.json()

def transform_orders(orders):
    """Transform Dutchie orders into dashboard format"""
    # Calculate KPIs from raw orders
    daily_kpis = []
    
    for order in orders:
        # Extract: revenue, items, customer type, channel, etc.
        pass
    
    return daily_kpis

def load_to_database(data, table_name):
    """Load data into PostgreSQL"""
    # Use SQLAlchemy or psycopg2
    pass

# Run daily via cron
if __name__ == "__main__":
    yesterday = datetime.now() - timedelta(days=1)
    for store in STORE_IDS:
        orders = fetch_orders(store, yesterday, yesterday)
        transformed = transform_orders(orders)
        load_to_database(transformed, "budr_daily_kpis")
```

#### 1.3 Test API Connection

```bash
python etl/dutchie_sync.py --test --store-id YOUR_STORE_ID
```

### Phase 2: Database Setup (4 hours)

#### 2.1 Choose Hosting

**Option A: Managed PostgreSQL (Recommended)**
- Heroku Postgres: $50/month (10M rows)
- Supabase: $25/month (8GB)
- Railway: $20/month (8GB)

**Option B: Self-Hosted**
- DigitalOcean Droplet: $24/month (4GB RAM)
- AWS RDS: $50-100/month

#### 2.2 Create Database Schema

Use the schema from the original dashboard:

```bash
# Connect to your PostgreSQL instance
psql postgresql://user:password@host:5432/budr_analytics

# Run schema creation
\i schema/create_tables.sql
```

Tables created:
- `budr_locations` - Your 7 locations
- `budr_products` - Product catalog
- `budr_daily_kpis` - Daily metrics per location
- `budr_category_kpis` - Category-level KPIs
- `budr_sku_kpis` - SKU-level performance
- `competitor_metrics` - Competitor data
- `budr_competitive_position` - BUDR vs market

#### 2.3 Initial Data Load

```bash
# Backfill historical data (last 90 days)
python etl/dutchie_sync.py --backfill --days 90
```

### Phase 3: Update Dashboard Code (2 hours)

#### 3.1 Replace Demo Data Loader

In `app.py`, change:

```python
# OLD (demo):
from utils.demo_data_loader import DemoDataLoader
db = DemoDataLoader()

# NEW (production):
from utils.db_connector import DatabaseConnector
db = DatabaseConnector()
```

#### 3.2 Update config.py

```python
# config/config.py
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'your-db-host.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'budr_analytics'),
    'user': os.getenv('DB_USER', 'budr_user'),
    'password': os.getenv('DB_PASSWORD', 'secure_password')
}
```

#### 3.3 Set Environment Variables

```bash
# .env (DO NOT commit to GitHub)
DB_HOST=your-postgres-host.com
DB_PORT=5432
DB_NAME=budr_analytics
DB_USER=budr_user
DB_PASSWORD=your_secure_password
```

### Phase 4: Deploy Production Dashboard (2 hours)

#### Option A: Streamlit Cloud

```bash
# Update requirements.txt
echo "psycopg2-binary>=2.9.0" >> requirements.txt

# Push to GitHub
git add .
git commit -m "Production deployment with live data"
git push

# In Streamlit Cloud settings:
# - Add secrets (DB credentials)
# - Redeploy app
```

#### Option B: Self-Hosted (Docker)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Deploy:

```bash
# Build and run
docker build -t budr-analytics .
docker run -p 8501:8501 --env-file .env budr-analytics

# Or use docker-compose.yml for database + dashboard
```

### Phase 5: Automation (1 hour)

#### 5.1 Schedule Daily Updates

**Using cron (Linux/Mac):**

```bash
# crontab -e
0 2 * * * cd /path/to/dashboard && python etl/dutchie_sync.py >> logs/sync.log 2>&1
```

**Using GitHub Actions:**

```yaml
# .github/workflows/daily-sync.yml
name: Daily Dutchie Sync
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python etl/dutchie_sync.py
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DUTCHIE_API_KEY: ${{ secrets.DUTCHIE_API_KEY }}
```

#### 5.2 Set Up Monitoring

- Uptime monitoring (UptimeRobot, free)
- Error alerts (Sentry, free tier)
- Data freshness check (custom script)

---

## Cost Breakdown (Production)

### Hosting
- **Streamlit Cloud Community**: $0 (public repos, basic features)
- **Streamlit Cloud Teams**: $250/month (private, custom domain, auth)
- **Self-hosted (DigitalOcean)**: $24/month (4GB droplet)

### Database
- **Supabase**: $25/month (8GB)
- **Heroku Postgres**: $50/month (10M rows)
- **Railway**: $20/month (8GB)

### Total Monthly Cost
- **Budget**: ~$45-50/month (Supabase + DigitalOcean)
- **Recommended**: ~$75-100/month (Heroku + Streamlit)
- **Enterprise**: $250+/month (Streamlit Teams + RDS)

---

## Security Checklist

Before going live:

- [ ] Enable database SSL/TLS
- [ ] Use environment variables for credentials (never hardcode)
- [ ] Add password protection to dashboard
- [ ] Enable HTTPS (included with Streamlit Cloud)
- [ ] Set up database backups (daily)
- [ ] Limit database user permissions (read-only for dashboard)
- [ ] Add IP whitelisting (optional)
- [ ] Review data retention policies

---

## Competitor Data Integration

The demo includes 8 CT competitors. For live competitor pricing:

### Option 1: Manual Updates (Simple)
Update `data/competitor_metrics.csv` weekly via web scraping or manual entry.

### Option 2: Automated Scraping (Advanced)
Build scrapers for competitor websites:
```python
# etl/competitor_scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_zen_leaf():
    """Scrape ZEN LEAF menu"""
    # Parse their public menu
    pass
```

**Legal note:** Check robots.txt and terms of service before scraping.

### Option 3: Third-Party API
Services like Headset or LeafLink may provide competitor data (additional cost).

---

## Testing Checklist

Before launching:

- [ ] Test with small date range (1 day)
- [ ] Test with full date range (90 days)
- [ ] Test all 8 tabs load correctly
- [ ] Test all filters work
- [ ] Test with single location
- [ ] Test with all locations
- [ ] Verify KPI calculations match Dutchie
- [ ] Test export functionality
- [ ] Load test (simulate 10+ concurrent users)
- [ ] Test on mobile/tablet

---

## Support & Maintenance

### Daily
- Monitor ETL job success
- Check data freshness

### Weekly
- Review error logs
- Update competitor data (if manual)

### Monthly
- Database backup verification
- Performance optimization
- Cost review

### Quarterly
- Add new features based on user feedback
- Update Dutchie API integration (if API changes)
- Security audit

---

## Next Steps

1. **Decide on timeline** - How fast do you need live data?
2. **Get Dutchie API access** - Contact your account manager
3. **Choose hosting** - Budget vs enterprise
4. **Set up database** - Managed or self-hosted
5. **Build ETL pipeline** - Transform Dutchie data
6. **Deploy** - Go live!

**Estimated total time: 48-72 hours** (including testing)

Questions? Want us to handle deployment?

Contact: [your contact info]

---

**BUDR Analytics Dashboard**  
From demo to production in 72 hours.
