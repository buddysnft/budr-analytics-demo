"""
BUDR Analytics Dashboard - Configuration
"""
import os

# Database Configuration (not used in demo - loads from CSV)
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'budr_analytics'),
    'user': os.getenv('POSTGRES_USER', 'budr'),
    'password': os.getenv('POSTGRES_PASSWORD', 'changeme')
}

# Dashboard Configuration
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 8501))
PAGE_TITLE = "BUDR Analytics Dashboard"
PAGE_ICON = "📊"
LAYOUT = "wide"

# BUDR Locations
LOCATIONS = [
    'Montville',
    'Danbury Mill Plain',
    'Budr Holding 6',
    'Tolland',
    'Vernon',
    'Danbury',
    'West Hartford'
]

# Product Categories
CATEGORIES = [
    'flower',
    'edibles',
    'vapes',
    'concentrates',
    'topicals',
    'pre-rolls'
]

# Customer Segments
CUSTOMER_SEGMENTS = [
    'new',
    'occasional',
    'regular',
    'vip'
]

# Order Channels
CHANNELS = [
    'pre-order',
    'walk-in',
    'delivery'
]

# Customer Types
CUSTOMER_TYPES = [
    'medical',
    'recreational'
]

# Date Range Presets
DATE_RANGES = {
    'Last 7 Days': 7,
    'Last 30 Days': 30,
    'Last 90 Days': 90,
    'MTD': 'mtd',
    'QTD': 'qtd',
    'YTD': 'ytd'
}

# KPI Thresholds (for alerts)
THRESHOLDS = {
    'avg_ticket_min': 30.0,
    'gross_margin_min': 0.20,
    'inventory_turnover_min': 7.0,  # days
    'dead_stock_days': 30,
    'stockout_alert_days': 1
}

# Chart Colors
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Export Settings
EXPORT_DIR = 'exports'
PDF_LOGO_PATH = None  # Set to logo path if available
