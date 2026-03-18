"""
Demo Data Loader - Replaces DatabaseConnector for Demo Mode
Loads data from CSV/JSON files instead of PostgreSQL
"""
import pandas as pd
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

class DemoDataLoader:
    """Loads demo data from files instead of database"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data files into memory"""
        print("Loading demo data...")
        
        # Load CSV files
        self.products_df = pd.read_csv(self.data_dir / "products.csv")
        self.daily_kpis_df = pd.read_csv(self.data_dir / "daily_kpis.csv")
        self.category_kpis_df = pd.read_csv(self.data_dir / "category_kpis.csv")
        self.sku_kpis_df = pd.read_csv(self.data_dir / "sku_kpis.csv")
        self.competitor_metrics_df = pd.read_csv(self.data_dir / "competitor_metrics.csv")
        self.budr_position_df = pd.read_csv(self.data_dir / "budr_position.csv")
        
        # Load JSON files
        with open(self.data_dir / "locations.json") as f:
            self.locations = json.load(f)
        
        with open(self.data_dir / "competitors.json") as f:
            self.competitors = json.load(f)
        
        print(f"✅ Loaded {len(self.daily_kpis_df)} daily KPI records")
        print(f"✅ Loaded {len(self.products_df)} products")
        print(f"✅ Loaded {len(self.locations)} locations")
    
    def get_locations(self) -> pd.DataFrame:
        """Get all BUDR locations"""
        return pd.DataFrame(self.locations)
    
    def get_date_range_data(self, start_date: str, end_date: str, 
                           location_ids: Optional[List[int]] = None) -> Dict[str, pd.DataFrame]:
        """Get data for a date range and locations"""
        
        # Filter by date range
        daily_kpis = self.daily_kpis_df[
            (self.daily_kpis_df['kpi_date'] >= start_date) & 
            (self.daily_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        category_kpis = self.category_kpis_df[
            (self.category_kpis_df['kpi_date'] >= start_date) & 
            (self.category_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        sku_kpis = self.sku_kpis_df[
            (self.sku_kpis_df['kpi_date'] >= start_date) & 
            (self.sku_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        # Filter by location if specified
        if location_ids:
            daily_kpis = daily_kpis[daily_kpis['location_id'].isin(location_ids)]
            category_kpis = category_kpis[category_kpis['location_id'].isin(location_ids)]
            sku_kpis = sku_kpis[sku_kpis['location_id'].isin(location_ids)]
        
        # Join product info to SKU KPIs
        sku_kpis = sku_kpis.merge(
            self.products_df[['id', 'name', 'category', 'brand']],
            left_on='product_id',
            right_on='id',
            how='left'
        )
        sku_kpis = sku_kpis.rename(columns={'name': 'product_name'})
        
        return {
            'daily_kpis': daily_kpis,
            'category_kpis': category_kpis,
            'sku_kpis': sku_kpis
        }
    
    def get_top_5_kpis(self, date: str, location_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get Top 5 KPIs for a specific date"""
        
        # Filter by date and location
        daily = self.daily_kpis_df[self.daily_kpis_df['kpi_date'] == date].copy()
        category = self.category_kpis_df[self.category_kpis_df['kpi_date'] == date].copy()
        
        if location_ids:
            daily = daily[daily['location_id'].isin(location_ids)]
            category = category[category['location_id'].isin(location_ids)]
        
        # KPI #1: Average Ticket
        avg_ticket = pd.DataFrame([{
            'avg_ticket': daily['avg_ticket'].mean(),
            'med_avg_ticket': daily['med_avg_ticket'].mean(),
            'rec_avg_ticket': daily['rec_avg_ticket'].mean(),
            'total_transactions': daily['total_transactions'].sum(),
            'total_revenue': daily['total_revenue'].sum()
        }])
        
        # KPI #2: Price per Unit by Category
        price_per_unit = category.groupby('category').agg({
            'avg_price_per_unit': 'mean',
            'units_sold': 'sum',
            'total_revenue': 'sum'
        }).reset_index()
        
        # KPI #3: Inventory Velocity
        velocity = category.groupby('category').agg({
            'days_to_sellthrough': 'mean',
            'units_per_day': 'mean'
        }).reset_index().rename(columns={
            'days_to_sellthrough': 'avg_days_to_sellthrough',
            'units_per_day': 'avg_units_per_day'
        })
        velocity = velocity.sort_values('avg_days_to_sellthrough')
        
        # KPI #4: Gross Margin
        margin = pd.DataFrame([{
            'overall_margin': category['gross_margin_pct'].mean(),
            'total_profit': category['gross_profit'].sum(),
            'total_revenue': category['total_revenue'].sum()
        }])
        
        margin_by_category = category.groupby('category').agg({
            'gross_margin_pct': 'mean',
            'gross_profit': 'sum'
        }).reset_index().sort_values('gross_margin_pct', ascending=False)
        
        # KPI #5: Pre-order vs Walk-in
        channel = pd.DataFrame([{
            'preorder_transactions': daily['preorder_transactions'].sum(),
            'preorder_revenue': daily['preorder_revenue'].sum(),
            'preorder_avg_ticket': daily['preorder_avg_ticket'].mean(),
            'walkin_transactions': daily['walkin_transactions'].sum(),
            'walkin_revenue': daily['walkin_revenue'].sum(),
            'walkin_avg_ticket': daily['walkin_avg_ticket'].mean()
        }])
        
        return {
            'avg_ticket': avg_ticket,
            'price_per_unit': price_per_unit,
            'velocity': velocity,
            'margin': margin,
            'margin_by_category': margin_by_category,
            'channel': channel
        }
    
    def get_comprehensive_kpis(self, start_date: str, end_date: str,
                              location_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get comprehensive daily KPIs"""
        
        daily = self.daily_kpis_df[
            (self.daily_kpis_df['kpi_date'] >= start_date) & 
            (self.daily_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        if location_ids:
            daily = daily[daily['location_id'].isin(location_ids)]
        
        # Group by date and aggregate
        comprehensive = daily.groupby('kpi_date').agg({
            'total_revenue': 'sum',
            'total_transactions': 'sum',
            'avg_ticket': 'mean',
            'unique_customers': 'sum',
            'rec_revenue': 'sum',
            'med_revenue': 'sum',
            'preorder_revenue': 'sum',
            'walkin_revenue': 'sum'
        }).reset_index()
        
        return comprehensive
    
    def get_customer_metrics(self, start_date: str, end_date: str,
                            location_ids: Optional[List[int]] = None) -> Dict[str, pd.DataFrame]:
        """Get customer intelligence data (simulated for demo)"""
        
        # Simulate customer segments
        segments = pd.DataFrame([
            {'customer_segment': 'VIP', 'customer_count': 450, 'avg_ltv': 2500, 'avg_orders': 25, 'avg_aov': 95},
            {'customer_segment': 'Loyal', 'customer_count': 1200, 'avg_ltv': 1200, 'avg_orders': 15, 'avg_aov': 75},
            {'customer_segment': 'Regular', 'customer_count': 3500, 'avg_ltv': 600, 'avg_orders': 8, 'avg_aov': 65},
            {'customer_segment': 'New', 'customer_count': 2800, 'avg_ltv': 180, 'avg_orders': 2, 'avg_aov': 85}
        ])
        
        # Simulate cohort retention (empty for now)
        cohorts = pd.DataFrame()
        
        return {
            'customers': segments,
            'cohorts': cohorts
        }
    
    def get_product_performance(self, start_date: str, end_date: str,
                               location_ids: Optional[List[int]] = None,
                               limit: int = 50) -> Dict[str, pd.DataFrame]:
        """Get product performance data"""
        
        sku = self.sku_kpis_df[
            (self.sku_kpis_df['kpi_date'] >= start_date) & 
            (self.sku_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        if location_ids:
            sku = sku[sku['location_id'].isin(location_ids)]
        
        # Join with products
        sku = sku.merge(
            self.products_df[['id', 'name', 'category', 'brand']],
            left_on='product_id',
            right_on='id',
            how='left'
        )
        
        # Top performers
        top_products = sku.groupby(['product_id', 'name', 'category', 'brand']).agg({
            'units_sold': 'sum',
            'revenue': 'sum',
            'gross_margin_pct': 'mean',
            'units_per_day': 'mean'
        }).reset_index()
        top_products.columns = ['product_id', 'product_name', 'category', 'brand', 
                               'total_units_sold', 'total_revenue', 'avg_margin', 'avg_velocity']
        top_products = top_products.sort_values('total_revenue', ascending=False).head(limit)
        
        # Bottom performers
        bottom_products = sku.groupby(['product_id', 'name', 'category', 'brand']).agg({
            'units_sold': 'sum',
            'revenue': 'sum',
            'gross_margin_pct': 'mean',
            'units_per_day': 'mean'
        }).reset_index()
        bottom_products.columns = ['product_id', 'product_name', 'category', 'brand', 
                                   'total_units_sold', 'total_revenue', 'avg_margin', 'avg_velocity']
        bottom_products = bottom_products.sort_values('total_revenue', ascending=True).head(limit)
        
        # Dead stock (simulated)
        dead_stock = pd.DataFrame([
            {'product_name': 'Old Product X', 'category': 'Edibles', 'days_since_last_sale': 45, 
             'current_quantity': 120, 'inventory_value': 1800, 'recommendation': 'Clear out - discount 50%'},
            {'product_name': 'Slow Mover Y', 'category': 'Topicals', 'days_since_last_sale': 35, 
             'current_quantity': 80, 'inventory_value': 1200, 'recommendation': 'Promote or bundle'},
        ])
        
        return {
            'top_products': top_products,
            'bottom_products': bottom_products,
            'dead_stock': dead_stock
        }
    
    def get_hourly_patterns(self, start_date: str, end_date: str,
                           location_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get hourly sales patterns (simulated)"""
        
        # Simulate hourly patterns
        hours = []
        for day in range(7):  # Days of week
            for hour in range(9, 21):  # 9am to 9pm
                # Peak hours: 11am-2pm, 5pm-8pm
                if hour in [11, 12, 13] or hour in [17, 18, 19, 20]:
                    multiplier = 1.5
                else:
                    multiplier = 1.0
                
                # Weekend boost
                if day in [5, 6]:
                    multiplier *= 1.3
                
                hours.append({
                    'hour_of_day': hour,
                    'day_of_week': day,
                    'avg_transactions': int(15 * multiplier),
                    'avg_revenue': round(1200 * multiplier, 2),
                    'avg_ticket': 80.0
                })
        
        return pd.DataFrame(hours)
    
    def get_competitor_benchmarks(self, date: str) -> Dict[str, pd.DataFrame]:
        """Get competitor benchmarking data"""
        
        # Join competitor metrics with competitor info
        competitors = self.competitor_metrics_df[
            self.competitor_metrics_df['metric_date'] == date
        ].copy()
        
        competitors = competitors.merge(
            pd.DataFrame(self.competitors),
            left_on='dispensary_id',
            right_on='id',
            how='left'
        )
        competitors = competitors.rename(columns={
            'name': 'dispensary_name',
            'location': 'dispensary_location'
        })
        
        # Competitive position
        position = self.budr_position_df[
            self.budr_position_df['analysis_date'] == date
        ].copy()
        
        return {
            'competitors': competitors,
            'position': position
        }
    
    def get_inventory_alerts(self, location_ids: Optional[List[int]] = None) -> Dict[str, pd.DataFrame]:
        """Get inventory alerts (simulated)"""
        
        stockouts = pd.DataFrame([
            {'product_name': 'Popular Flower A', 'category': 'Flower', 
             'stockout_start_date': '2026-03-15', 'days_out_of_stock': 2, 
             'estimated_lost_revenue': 1500},
            {'product_name': 'Best Vape B', 'category': 'Vapes', 
             'stockout_start_date': '2026-03-16', 'days_out_of_stock': 1, 
             'estimated_lost_revenue': 800}
        ])
        
        dead_stock = pd.DataFrame([
            {'product_name': 'Old Product X', 'category': 'Edibles', 
             'days_since_last_sale': 45, 'inventory_value': 1800, 
             'recommendation': 'Clear out - discount 50%'},
        ])
        
        return {
            'stockouts': stockouts,
            'dead_stock': dead_stock
        }
    
    def get_discount_analysis(self, start_date: str, end_date: str,
                             location_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get discount usage and ROI analysis (simulated)"""
        
        discounts = pd.DataFrame([
            {'analysis_date': '2026-03-17', 'discount_type': 'Happy Hour', 
             'times_used': 450, 'revenue_impact': 12500, 'roi': 2.1},
            {'analysis_date': '2026-03-17', 'discount_type': 'Loyalty Rewards', 
             'times_used': 280, 'revenue_impact': 8200, 'roi': 1.8},
            {'analysis_date': '2026-03-17', 'discount_type': 'First Time', 
             'times_used': 120, 'revenue_impact': 5600, 'roi': 3.2}
        ])
        
        return discounts
    
    def get_channel_performance(self, start_date: str, end_date: str,
                               location_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get channel-level performance"""
        
        daily = self.daily_kpis_df[
            (self.daily_kpis_df['kpi_date'] >= start_date) & 
            (self.daily_kpis_df['kpi_date'] <= end_date)
        ].copy()
        
        if location_ids:
            daily = daily[daily['location_id'].isin(location_ids)]
        
        # Create channel metrics
        channels = []
        for _, row in daily.iterrows():
            channels.append({
                'metric_date': row['kpi_date'],
                'channel': 'Pre-order',
                'transactions': row['preorder_transactions'],
                'revenue': row['preorder_revenue'],
                'avg_ticket': row['preorder_avg_ticket']
            })
            channels.append({
                'metric_date': row['kpi_date'],
                'channel': 'Walk-in',
                'transactions': row['walkin_transactions'],
                'revenue': row['walkin_revenue'],
                'avg_ticket': row['walkin_avg_ticket']
            })
        
        return pd.DataFrame(channels)
    
    def get_basket_analysis(self, date: str, location_ids: Optional[List[int]] = None,
                           limit: int = 20) -> pd.DataFrame:
        """Get market basket analysis (simulated)"""
        
        baskets = pd.DataFrame([
            {'product_a': 'Blue Dream Flower 3.5g', 'product_b': 'Pre-Roll 3-pack', 
             'times_purchased_together': 85, 'confidence': 0.68, 'lift': 2.3},
            {'product_a': 'Wedding Cake Vape 1g', 'product_b': 'Gummies 100mg', 
             'times_purchased_together': 72, 'confidence': 0.61, 'lift': 2.1},
            {'product_a': 'Gelato Flower 7g', 'product_b': 'Concentrate Wax 1g', 
             'times_purchased_together': 65, 'confidence': 0.55, 'lift': 1.9}
        ])
        
        return baskets.head(limit)
