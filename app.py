"""
BUDR Analytics Dashboard - DEMO VERSION
🎯 Works WITHOUT database - uses realistic sample data

This is a fully functional demo showing what your dashboard will look like
with YOUR real data. All features work, all 8 tabs display properly.

Ready to deploy with live data? See DEPLOYMENT.md
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import PAGE_TITLE, PAGE_ICON, LAYOUT, LOCATIONS, CATEGORIES, CHANNELS, CUSTOMER_TYPES, DATE_RANGES
from utils.demo_data_loader import DemoDataLoader
from exports.export_utils import create_export_buttons, prepare_export_data

# Import tab modules
from tabs import (
    tab1_performance_overview,
    tab2_revenue_deep_dive,
    tab3_customer_intelligence,
    tab4_product_performance,
    tab5_pricing_margin,
    tab6_inventory_management,
    tab7_time_analysis,
    tab8_competitor_benchmarking
)

# Page config
st.set_page_config(
    page_title=f"{PAGE_TITLE} - DEMO",
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
    }
    .demo-banner {
        background: linear-gradient(90deg, #ff6b6b, #ff8c42);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# DEMO BANNER
st.markdown("""
<div class="demo-banner">
    🎯 DEMO MODE - This dashboard uses realistic sample data. 
    Connect to your Dutchie API for live data in 48 hours!
</div>
""", unsafe_allow_html=True)

# Initialize demo data loader
@st.cache_resource
def init_data():
    """Initialize demo data loader"""
    return DemoDataLoader()

db = init_data()

# Sidebar - Global Filters
st.sidebar.title("🎛️ Filters")

# Demo info in sidebar
st.sidebar.info("""
**DEMO Mode Active**

Using 30 days of realistic sample data:
- 7 BUDR locations
- 8 CT competitors
- $7.3M total revenue
- All KPIs calculated

Ready to connect to your Dutchie API? Contact us!
""")

st.sidebar.divider()

# Date range selector
st.sidebar.subheader("📅 Date Range")

date_preset = st.sidebar.selectbox(
    "Preset",
    options=list(DATE_RANGES.keys()),
    index=1  # Default to Last 30 Days
)

# Calculate date range
end_date = datetime.now().date()
if DATE_RANGES[date_preset] == 'mtd':
    start_date = end_date.replace(day=1)
elif DATE_RANGES[date_preset] == 'qtd':
    quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
    start_date = end_date.replace(month=quarter_start_month, day=1)
elif DATE_RANGES[date_preset] == 'ytd':
    start_date = end_date.replace(month=1, day=1)
else:
    start_date = end_date - timedelta(days=DATE_RANGES[date_preset])

# Custom date range
use_custom = st.sidebar.checkbox("Use Custom Range")
if use_custom:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start", start_date)
    with col2:
        end_date = st.date_input("End", end_date)

# Location filter
st.sidebar.subheader("📍 Locations")

locations_df = db.get_locations()
available_locations = locations_df['name'].tolist()
location_ids_map = dict(zip(locations_df['name'], locations_df['id']))

all_locations = st.sidebar.checkbox("All Locations", value=True)

if all_locations:
    selected_location_names = available_locations
else:
    selected_location_names = st.sidebar.multiselect(
        "Select Locations",
        options=available_locations,
        default=available_locations[:1] if available_locations else []
    )

# Map location names to IDs
selected_locations = [location_ids_map.get(name) for name in selected_location_names if name in location_ids_map]

# Category filter
st.sidebar.subheader("🏷️ Categories")
all_categories = st.sidebar.checkbox("All Categories", value=True)

if not all_categories:
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=CATEGORIES,
        default=CATEGORIES
    )
else:
    selected_categories = CATEGORIES

# Customer type filter
st.sidebar.subheader("👥 Customer Type")
customer_type_filter = st.sidebar.radio(
    "Type",
    options=["All", "Medical", "Recreational"],
    index=0
)

# Channel filter
st.sidebar.subheader("🚪 Channel")
all_channels = st.sidebar.checkbox("All Channels", value=True)

if not all_channels:
    selected_channels = st.sidebar.multiselect(
        "Select Channels",
        options=CHANNELS,
        default=CHANNELS
    )
else:
    selected_channels = CHANNELS

# Data refresh
st.sidebar.divider()
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# Main content
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption("Demo Version - All data is simulated for demonstration purposes")

# Summary bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Date Range", f"{(end_date - start_date).days} days")

with col2:
    location_count = len(selected_location_names)
    st.metric("Locations", f"{location_count} selected")

with col3:
    st.metric("From", start_date.strftime('%Y-%m-%d'))

with col4:
    st.metric("To", end_date.strftime('%Y-%m-%d'))

st.divider()

# Tab navigation
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Performance Overview",
    "💰 Revenue Deep Dive",
    "👥 Customer Intelligence",
    "📦 Product Performance",
    "💵 Pricing & Margin",
    "📦 Inventory Management",
    "⏰ Time Analysis",
    "🏁 Competitor Benchmarking"
])

# Convert dates to strings for queries
start_date_str = str(start_date)
end_date_str = str(end_date)
selected_date_str = str(end_date)  # Use end date as "current" date for point-in-time metrics

# Render tabs
with tab1:
    try:
        tab1_performance_overview.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Performance Overview: {str(e)}")
        st.exception(e)

with tab2:
    try:
        tab2_revenue_deep_dive.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Revenue Deep Dive: {str(e)}")
        st.exception(e)

with tab3:
    try:
        tab3_customer_intelligence.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Customer Intelligence: {str(e)}")
        st.exception(e)

with tab4:
    try:
        tab4_product_performance.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Product Performance: {str(e)}")
        st.exception(e)

with tab5:
    try:
        tab5_pricing_margin.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Pricing & Margin: {str(e)}")
        st.exception(e)

with tab6:
    try:
        tab6_inventory_management.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Inventory Management: {str(e)}")
        st.exception(e)

with tab7:
    try:
        tab7_time_analysis.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Time Analysis: {str(e)}")
        st.exception(e)

with tab8:
    try:
        tab8_competitor_benchmarking.render(db, selected_date_str, selected_locations, start_date_str, end_date_str)
    except Exception as e:
        st.error(f"Error loading Competitor Benchmarking: {str(e)}")
        st.exception(e)

# Footer
st.divider()

# Call to action
st.success("""
### 🎯 Ready to Connect Your Live Data?

This is what your dashboard looks like with YOUR real Dutchie data:
- ✅ All 8 tabs fully functional
- ✅ Real-time insights across all locations
- ✅ Competitor benchmarking
- ✅ Automated daily updates

**Next Steps:**
1. Connect to your Dutchie API (48-hour setup)
2. Deploy to your own secure cloud instance
3. Start making data-driven decisions

Contact us to get started!
""")

st.caption(f"BUDR Analytics Dashboard v1.0 (DEMO) | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(selected_location_names)} location(s) selected")
