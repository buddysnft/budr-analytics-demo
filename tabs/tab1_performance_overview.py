"""
Tab 1: Performance Overview (Top 5 KPIs)
Displays big number cards, sparklines, benchmarks, and alerts
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from components.charts import create_metric_card, create_sparkline, create_gauge
from config.config import THRESHOLDS, COLORS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Performance Overview tab"""
    
    st.header("🎯 Performance Overview - Top 5 KPIs")
    
    # Get Top 5 KPIs for selected date
    kpis = db.get_top_5_kpis(selected_date, selected_locations)
    
    # Get trend data (last 30 days)
    trend_data = db.get_date_range_data(
        (datetime.strptime(selected_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'),
        selected_date,
        selected_locations
    )
    
    # KPI #1: Average Ticket
    st.subheader("1️⃣ Average Ticket")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not kpis['avg_ticket'].empty:
            avg_ticket = kpis['avg_ticket']['avg_ticket'].iloc[0]
            
            # Calculate delta (compare to previous day)
            prev_date = (datetime.strptime(selected_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            prev_kpis = db.get_top_5_kpis(prev_date, selected_locations)
            delta = None
            if not prev_kpis['avg_ticket'].empty:
                prev_avg = prev_kpis['avg_ticket']['avg_ticket'].iloc[0]
                delta = avg_ticket - prev_avg
            
            st.plotly_chart(
                create_metric_card(avg_ticket, "Average Ticket", delta, prefix="$"),
                use_container_width=True
            )
            
            # Alert if below threshold
            if avg_ticket < THRESHOLDS['avg_ticket_min']:
                st.warning(f"⚠️ Below minimum threshold (${THRESHOLDS['avg_ticket_min']:.2f})")
    
    with col2:
        if not kpis['avg_ticket'].empty:
            med_ticket = kpis['avg_ticket']['med_avg_ticket'].iloc[0]
            st.plotly_chart(
                create_metric_card(med_ticket, "Medical Avg Ticket", prefix="$"),
                use_container_width=True
            )
    
    with col3:
        if not kpis['avg_ticket'].empty:
            rec_ticket = kpis['avg_ticket']['rec_avg_ticket'].iloc[0]
            st.plotly_chart(
                create_metric_card(rec_ticket, "Recreational Avg Ticket", prefix="$"),
                use_container_width=True
            )
    
    # Trend sparkline
    if not trend_data['daily_kpis'].empty:
        st.caption("30-Day Trend")
        st.plotly_chart(
            create_sparkline(trend_data['daily_kpis'], 'kpi_date', 'avg_ticket'),
            use_container_width=True
        )
    
    st.divider()
    
    # KPI #2: Price per Unit by Category
    st.subheader("2️⃣ Price per Unit by Category")
    
    if not kpis['price_per_unit'].empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart
            import plotly.graph_objects as go
            fig = go.Figure(go.Bar(
                x=kpis['price_per_unit']['category'],
                y=kpis['price_per_unit']['avg_price_per_unit'],
                marker_color=COLORS['primary'],
                text=kpis['price_per_unit']['avg_price_per_unit'].apply(lambda x: f"${x:.2f}"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Average Price per Unit",
                xaxis_title="Category",
                yaxis_title="Price ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.caption("Category Breakdown")
            for _, row in kpis['price_per_unit'].iterrows():
                st.metric(
                    label=row['category'].title(),
                    value=f"${row['avg_price_per_unit']:.2f}",
                    delta=f"{row['units_sold']} units"
                )
    
    st.divider()
    
    # KPI #3: Inventory Velocity
    st.subheader("3️⃣ Inventory Velocity")
    
    if not kpis['velocity'].empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Days to sell through by category
            import plotly.graph_objects as go
            fig = go.Figure(go.Bar(
                y=kpis['velocity']['category'],
                x=kpis['velocity']['avg_days_to_sellthrough'],
                orientation='h',
                marker_color=COLORS['success'],
                text=kpis['velocity']['avg_days_to_sellthrough'].apply(lambda x: f"{x:.1f} days"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Days to Sell Through Inventory",
                xaxis_title="Days",
                yaxis_title="Category",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Units per day
            import plotly.graph_objects as go
            fig = go.Figure(go.Bar(
                y=kpis['velocity']['category'],
                x=kpis['velocity']['avg_units_per_day'],
                orientation='h',
                marker_color=COLORS['info'],
                text=kpis['velocity']['avg_units_per_day'].apply(lambda x: f"{x:.1f} u/d"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Units Sold per Day",
                xaxis_title="Units/Day",
                yaxis_title="Category",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Alert for slow movers
        slow_categories = kpis['velocity'][kpis['velocity']['avg_days_to_sellthrough'] > THRESHOLDS['inventory_turnover_min']]
        if not slow_categories.empty:
            st.warning(f"⚠️ Slow-moving categories: {', '.join(slow_categories['category'].tolist())}")
    
    st.divider()
    
    # KPI #4: Gross Margin
    st.subheader("4️⃣ Gross Margin")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not kpis['margin'].empty:
            overall_margin = kpis['margin']['overall_margin'].iloc[0]
            total_profit = kpis['margin']['total_profit'].iloc[0]
            
            st.plotly_chart(
                create_metric_card(overall_margin, "Overall Gross Margin", suffix="%", format_str=".1f"),
                use_container_width=True
            )
            
            # Alert if below threshold
            if overall_margin < (THRESHOLDS['gross_margin_min'] * 100):
                st.error(f"🚨 Below minimum margin ({THRESHOLDS['gross_margin_min']*100:.0f}%)")
    
    with col2:
        if not kpis['margin'].empty:
            st.plotly_chart(
                create_metric_card(total_profit, "Total Gross Profit", prefix="$", format_str=",.0f"),
                use_container_width=True
            )
    
    with col3:
        if not kpis['margin'].empty:
            total_revenue = kpis['margin']['total_revenue'].iloc[0]
            st.plotly_chart(
                create_metric_card(total_revenue, "Total Revenue", prefix="$", format_str=",.0f"),
                use_container_width=True
            )
    
    # Margin by category
    if not kpis['margin_by_category'].empty:
        st.caption("Margin by Category")
        import plotly.graph_objects as go
        
        # Color code: green if above threshold, red if below
        colors = [COLORS['success'] if m >= (THRESHOLDS['gross_margin_min']*100) 
                 else COLORS['danger'] 
                 for m in kpis['margin_by_category']['gross_margin_pct']]
        
        fig = go.Figure(go.Bar(
            x=kpis['margin_by_category']['category'],
            y=kpis['margin_by_category']['gross_margin_pct'],
            marker_color=colors,
            text=kpis['margin_by_category']['gross_margin_pct'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        fig.update_layout(
            title="Gross Margin by Category",
            xaxis_title="Category",
            yaxis_title="Margin (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # KPI #5: Pre-order vs Walk-in
    st.subheader("5️⃣ Pre-order vs Walk-in")
    
    if not kpis['channel'].empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue split pie chart
            import plotly.graph_objects as go
            
            preorder_rev = kpis['channel']['preorder_revenue'].iloc[0]
            walkin_rev = kpis['channel']['walkin_revenue'].iloc[0]
            
            fig = go.Figure(go.Pie(
                labels=['Pre-order', 'Walk-in'],
                values=[preorder_rev, walkin_rev],
                hole=0.4,
                marker_colors=[COLORS['primary'], COLORS['secondary']],
                textinfo='label+percent',
                textposition='outside'
            ))
            fig.update_layout(
                title="Revenue Split",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Transaction split pie chart
            preorder_txn = kpis['channel']['preorder_transactions'].iloc[0]
            walkin_txn = kpis['channel']['walkin_transactions'].iloc[0]
            
            fig = go.Figure(go.Pie(
                labels=['Pre-order', 'Walk-in'],
                values=[preorder_txn, walkin_txn],
                hole=0.4,
                marker_colors=[COLORS['primary'], COLORS['secondary']],
                textinfo='label+percent',
                textposition='outside'
            ))
            fig.update_layout(
                title="Transaction Split",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Avg ticket comparison
        st.caption("Average Ticket Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            preorder_ticket = kpis['channel']['preorder_avg_ticket'].iloc[0]
            st.metric("Pre-order Avg Ticket", f"${preorder_ticket:.2f}")
        
        with col2:
            walkin_ticket = kpis['channel']['walkin_avg_ticket'].iloc[0]
            delta = walkin_ticket - preorder_ticket
            st.metric("Walk-in Avg Ticket", f"${walkin_ticket:.2f}", 
                     delta=f"${delta:.2f} vs pre-order")
    
    st.divider()
    
    # Alerts Section
    st.subheader("🚨 Active Alerts")
    
    alerts = db.get_inventory_alerts(selected_locations)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Stockouts")
        if not alerts['stockouts'].empty:
            for _, row in alerts['stockouts'].head(5).iterrows():
                st.error(f"📦 {row['product_name']} - {row['days_out_of_stock']} days out (${row['estimated_lost_revenue']:.0f} lost)")
        else:
            st.success("✅ No active stockouts")
    
    with col2:
        st.caption("Dead Stock")
        if not alerts['dead_stock'].empty:
            for _, row in alerts['dead_stock'].head(5).iterrows():
                st.warning(f"⚠️ {row['product_name']} - {row['days_since_last_sale']} days (${row['inventory_value']:.0f})")
        else:
            st.success("✅ No dead stock")
