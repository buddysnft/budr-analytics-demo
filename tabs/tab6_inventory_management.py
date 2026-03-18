"""
Tab 6: Inventory Management
Days on hand, sell-through rates, stockouts, overstock, new product performance
"""
import streamlit as st
import pandas as pd
from components.charts import create_bar_chart, create_line_chart, create_gauge
from utils.demo_data_loader import load_demo_data
from config.config import COLORS, THRESHOLDS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Inventory Management tab"""
    
    st.header("📦 Inventory Management")
    
    # Get data
    date_range_data = db.get_date_range_data(start_date, end_date, selected_locations)
    category_kpis = date_range_data['category_kpis']
    sku_kpis = date_range_data['sku_kpis']
    alerts = db.get_inventory_alerts(selected_locations)
    comp_kpis = db.get_comprehensive_kpis(start_date, end_date, selected_locations)
    
    # Overview Metrics
    st.subheader("📊 Inventory Overview")
    
    if not comp_kpis.empty:
        latest = comp_kpis.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'total_inventory_value' in latest:
                st.metric("Total Inventory Value", f"${latest['total_inventory_value']:,.0f}")
        
        with col2:
            if 'days_of_inventory' in latest:
                st.metric("Days of Inventory", f"{latest['days_of_inventory']:.1f}")
                if latest['days_of_inventory'] > 30:
                    st.warning("⚠️ High inventory levels")
        
        with col3:
            if 'inventory_turnover_rate' in latest:
                st.metric("Turnover Rate", f"{latest['inventory_turnover_rate']:.2f}x")
        
        with col4:
            if 'stockout_count' in latest:
                st.metric("Active Stockouts", f"{int(latest['stockout_count'])}")
                if latest['stockout_count'] > 0:
                    st.error("🚨 Stockouts detected")
    
    st.divider()
    
    # Days on Hand by Category
    st.subheader("⏱️ Days on Hand by Category")
    
    if not category_kpis.empty:
        doh_summary = category_kpis.groupby('category').agg({
            'days_to_sellthrough': 'mean',
            'avg_inventory_on_hand': 'mean',
            'units_sold': 'sum'
        }).reset_index()
        
        doh_summary = doh_summary.sort_values('days_to_sellthrough')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            import plotly.graph_objects as go
            
            colors = [COLORS['success'] if days < 14 else COLORS['warning'] if days < 30 
                     else COLORS['danger'] for days in doh_summary['days_to_sellthrough']]
            
            fig = go.Figure(go.Bar(
                y=doh_summary['category'],
                x=doh_summary['days_to_sellthrough'],
                orientation='h',
                marker_color=colors,
                text=doh_summary['days_to_sellthrough'].apply(lambda x: f"{x:.1f}"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Days to Sell Through by Category",
                xaxis_title="Days",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gauge for overall DOH
            overall_doh = doh_summary['days_to_sellthrough'].mean()
            fig = create_gauge(
                overall_doh, 60,
                title="Overall Days on Hand",
                threshold_yellow=0.33, threshold_green=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # DOH table
        st.dataframe(
            doh_summary.style.format({
                'days_to_sellthrough': '{:.1f} days',
                'avg_inventory_on_hand': '{:,.0f} units',
                'units_sold': '{:,}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # Sell-Through Rates
    st.subheader("📈 Sell-Through Rates")
    
    if not sku_kpis.empty:
        # Calculate sell-through rate: units sold / avg inventory
        sku_kpis['sell_through_rate'] = (sku_kpis['units_sold'] / sku_kpis['avg_inventory'] * 100).fillna(0)
        
        sellthrough_by_category = sku_kpis.groupby('category').agg({
            'sell_through_rate': 'mean',
            'units_sold': 'sum',
            'avg_inventory': 'mean'
        }).reset_index()
        
        sellthrough_by_category = sellthrough_by_category.sort_values('sell_through_rate', ascending=False)
        
        fig = create_bar_chart(
            sellthrough_by_category, 'category', 'sell_through_rate',
            title="Average Sell-Through Rate by Category (%)",
            color=COLORS['info']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top/bottom sell-through SKUs
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("Best Sell-Through (Top 10)")
            top_sellthrough = sku_kpis.nlargest(10, 'sell_through_rate')
            st.dataframe(
                top_sellthrough[['product_name', 'category', 'sell_through_rate', 'units_sold']].style.format({
                    'sell_through_rate': '{:.1f}%',
                    'units_sold': '{:,}'
                }),
                use_container_width=True
            )
        
        with col2:
            st.caption("Worst Sell-Through (Bottom 10)")
            bottom_sellthrough = sku_kpis.nsmallest(10, 'sell_through_rate')
            st.dataframe(
                bottom_sellthrough[['product_name', 'category', 'sell_through_rate', 'units_sold']].style.format({
                    'sell_through_rate': '{:.1f}%',
                    'units_sold': '{:,}'
                }),
                use_container_width=True
            )
    
    st.divider()
    
    # Stockout Tracker
    st.subheader("🚨 Stockout Tracker")
    
    if not alerts['stockouts'].empty:
        stockouts = alerts['stockouts']
        
        st.error(f"⚠️ {len(stockouts)} active stockouts")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(
                stockouts[['product_name', 'category', 'stockout_start_date', 
                          'days_out_of_stock', 'estimated_lost_revenue']].style.format({
                    'days_out_of_stock': '{:.0f}',
                    'estimated_lost_revenue': '${:,.0f}'
                }),
                use_container_width=True
            )
        
        with col2:
            total_lost = stockouts['estimated_lost_revenue'].sum()
            avg_days_out = stockouts['days_out_of_stock'].mean()
            
            st.metric("Est. Lost Revenue", f"${total_lost:,.0f}")
            st.metric("Avg Days Out", f"{avg_days_out:.1f}")
    else:
        st.success("✅ No active stockouts")
    
    st.divider()
    
    # Overstock Warnings
    st.subheader("⚠️ Overstock & Dead Stock")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Dead Stock (30+ days no sales)")
        
        if not alerts['dead_stock'].empty:
            dead_stock = alerts['dead_stock']
            
            total_dead_value = dead_stock['inventory_value'].sum()
            st.error(f"💀 {len(dead_stock)} items - ${total_dead_value:,.0f} value")
            
            st.dataframe(
                dead_stock[['product_name', 'category', 'days_since_last_sale', 'inventory_value']].style.format({
                    'days_since_last_sale': '{:.0f}',
                    'inventory_value': '${:,.2f}'
                }),
                use_container_width=True,
                height=300
            )
        else:
            st.success("✅ No dead stock")
    
    with col2:
        st.caption("Slow Movers (>30 days to sell through)")
        
        if not category_kpis.empty:
            slow_categories = doh_summary[doh_summary['days_to_sellthrough'] > 30]
            
            if not slow_categories.empty:
                st.warning(f"⚠️ {len(slow_categories)} slow categories")
                
                st.dataframe(
                    slow_categories[['category', 'days_to_sellthrough', 'avg_inventory_on_hand']].style.format({
                        'days_to_sellthrough': '{:.1f} days',
                        'avg_inventory_on_hand': '{:,.0f} units'
                    }),
                    use_container_width=True
                )
            else:
                st.success("✅ All categories moving well")
    
    st.divider()
    
    # New Product Performance
    st.subheader("🆕 New Product Performance (First 30 Days)")
    
    # Query for products launched in the last 90 days
    new_products_query = f"""
        SELECT 
            p.name as product_name,
            p.category,
            pl.days_since_launch,
            pl.cumulative_revenue,
            pl.last_30_days_revenue,
            pl.last_30_days_units,
            pl.growth_rate
        FROM budr_product_lifecycle pl
        JOIN budr_products p ON pl.product_id = p.id
        WHERE pl.days_since_launch <= 30
        AND pl.lifecycle_date BETWEEN %s AND %s
        {'AND p.location_id IN (' + ','.join(map(str, selected_locations)) + ')' if selected_locations else ''}
        ORDER BY pl.last_30_days_revenue DESC
        LIMIT 20
    """
    
    try:
        new_products = db.execute_query(new_products_query, (start_date, end_date))
        
        if not new_products.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(
                    new_products[['product_name', 'category', 'days_since_launch', 
                                 'cumulative_revenue', 'last_30_days_units', 'growth_rate']].style.format({
                        'days_since_launch': '{:.0f}',
                        'cumulative_revenue': '${:,.0f}',
                        'last_30_days_units': '{:,}',
                        'growth_rate': '{:+.1f}%'
                    }),
                    use_container_width=True
                )
            
            with col2:
                total_new_revenue = new_products['cumulative_revenue'].sum()
                avg_growth = new_products['growth_rate'].mean()
                
                st.metric("Total New Product Revenue", f"${total_new_revenue:,.0f}")
                st.metric("Avg Growth Rate", f"{avg_growth:+.1f}%")
        else:
            st.info("No new products launched in the last 30 days")
    
    except Exception as e:
        st.info("New product performance data not available")
