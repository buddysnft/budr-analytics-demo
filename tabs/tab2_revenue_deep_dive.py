"""
Tab 2: Revenue Deep Dive
Revenue trends, category breakdown, channel analysis, AOV/UPT, discount impact
"""
import streamlit as st
import pandas as pd
from components.charts import (create_line_chart, create_pie_chart, create_stacked_bar,
                               create_bar_chart, create_waterfall)
from config.config import COLORS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Revenue Deep Dive tab"""
    
    st.header("💰 Revenue Deep Dive")
    
    # Get comprehensive KPIs
    comp_kpis = db.get_comprehensive_kpis(start_date, end_date, selected_locations)
    
    # Get category data
    date_range_data = db.get_date_range_data(start_date, end_date, selected_locations)
    category_kpis = date_range_data['category_kpis']
    
    # Get channel data
    channel_data = db.get_channel_performance(start_date, end_date, selected_locations)
    
    # Revenue Trends
    st.subheader("📈 Revenue Trends")
    
    if not comp_kpis.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_revenue = comp_kpis['total_revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        
        with col2:
            avg_daily = comp_kpis['total_revenue'].mean()
            st.metric("Avg Daily Revenue", f"${avg_daily:,.0f}")
        
        with col3:
            if len(comp_kpis) > 1:
                growth = comp_kpis['revenue_wow_growth'].iloc[-1]
                st.metric("WoW Growth", f"{growth:.1f}%", delta=f"{growth:.1f}%")
        
        # Line chart: Daily revenue
        fig = create_line_chart(
            comp_kpis, 'kpi_date', ['total_revenue'],
            title="Daily Revenue Trend",
            labels={'total_revenue': 'Revenue'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Line chart: Growth rates
        growth_cols = ['revenue_wow_growth', 'revenue_mom_growth']
        available_cols = [col for col in growth_cols if col in comp_kpis.columns and not comp_kpis[col].isna().all()]
        
        if available_cols:
            fig = create_line_chart(
                comp_kpis, 'kpi_date', available_cols,
                title="Revenue Growth Rates",
                labels={'revenue_wow_growth': 'Week-over-Week %', 'revenue_mom_growth': 'Month-over-Month %'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Revenue by Category
    st.subheader("🏷️ Revenue by Category")
    
    if not category_kpis.empty:
        # Aggregate by category
        category_summary = category_kpis.groupby('category').agg({
            'total_revenue': 'sum',
            'units_sold': 'sum',
            'avg_price_per_unit': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig = create_pie_chart(
                category_summary, 'category', 'total_revenue',
                title="Revenue by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart
            fig = create_bar_chart(
                category_summary.sort_values('total_revenue', ascending=False),
                'category', 'total_revenue',
                title="Category Revenue (Total)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Stacked area chart over time
        if len(category_kpis['kpi_date'].unique()) > 1:
            # Pivot for stacked chart
            pivot_df = category_kpis.pivot_table(
                index='kpi_date',
                columns='category',
                values='total_revenue',
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            categories = [col for col in pivot_df.columns if col != 'kpi_date']
            
            fig = create_stacked_bar(
                pivot_df, 'kpi_date', categories,
                title="Revenue Trend by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Revenue by Channel
    st.subheader("🚪 Revenue by Channel")
    
    if not channel_data.empty:
        # Aggregate by channel
        channel_summary = channel_data.groupby('channel').agg({
            'revenue': 'sum',
            'transaction_count': 'sum',
            'avg_ticket': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig = create_pie_chart(
                channel_summary, 'channel', 'revenue',
                title="Revenue by Channel"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Comparison bar chart
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Revenue',
                x=channel_summary['channel'],
                y=channel_summary['revenue'],
                yaxis='y',
                marker_color=COLORS['primary']
            ))
            
            fig.add_trace(go.Bar(
                name='Transactions',
                x=channel_summary['channel'],
                y=channel_summary['transaction_count'],
                yaxis='y2',
                marker_color=COLORS['secondary']
            ))
            
            fig.update_layout(
                title='Revenue & Transactions by Channel',
                yaxis=dict(title='Revenue ($)'),
                yaxis2=dict(title='Transactions', overlaying='y', side='right'),
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Channel performance table
        st.caption("Channel Performance Metrics")
        st.dataframe(
            channel_summary.style.format({
                'revenue': '${:,.0f}',
                'transaction_count': '{:,}',
                'avg_ticket': '${:.2f}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # AOV and UPT Trends
    st.subheader("📊 AOV & UPT Trends")
    
    if not comp_kpis.empty and 'avg_ticket' in comp_kpis.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # AOV trend
            fig = create_line_chart(
                comp_kpis, 'kpi_date', ['avg_ticket'],
                title="Average Order Value (AOV) Trend",
                labels={'avg_ticket': 'AOV ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # UPT trend
            if 'units_per_transaction' in comp_kpis.columns:
                fig = create_line_chart(
                    comp_kpis, 'kpi_date', ['units_per_transaction'],
                    title="Units Per Transaction (UPT) Trend",
                    labels={'units_per_transaction': 'UPT'}
                )
                st.plotly_chart(fig, use_container_width=True)
            elif 'items_per_basket' in comp_kpis.columns:
                fig = create_line_chart(
                    comp_kpis, 'kpi_date', ['items_per_basket'],
                    title="Items Per Basket Trend",
                    labels={'items_per_basket': 'Items/Basket'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Discount Impact Analysis
    st.subheader("🎁 Discount Impact Analysis")
    
    discount_data = db.get_discount_analysis(start_date, end_date, selected_locations)
    
    if not discount_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_discounts = discount_data['total_discount_amount'].sum()
            st.metric("Total Discounts Given", f"${total_discounts:,.0f}")
        
        with col2:
            avg_discount_pct = discount_data['avg_discount_pct'].mean()
            st.metric("Avg Discount %", f"{avg_discount_pct:.1f}%")
        
        with col3:
            if 'discount_roi' in discount_data.columns:
                avg_roi = discount_data['discount_roi'].mean()
                st.metric("Avg Discount ROI", f"{avg_roi:.2f}x")
        
        # Discount by type
        discount_summary = discount_data.groupby('discount_type').agg({
            'total_discount_amount': 'sum',
            'transactions_with_discount': 'sum',
            'discount_usage_rate': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Discount amount by type
            fig = create_bar_chart(
                discount_summary.sort_values('total_discount_amount', ascending=False),
                'discount_type', 'total_discount_amount',
                title="Total Discount Amount by Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Usage rate by type
            fig = create_bar_chart(
                discount_summary.sort_values('discount_usage_rate', ascending=False),
                'discount_type', 'discount_usage_rate',
                title="Discount Usage Rate by Type (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Margin comparison (with vs without discounts)
        if 'margin_with_discount' in discount_data.columns and 'margin_without_discount' in discount_data.columns:
            st.caption("Margin Impact: With vs Without Discounts")
            
            margin_comp = discount_data.groupby('discount_type').agg({
                'margin_with_discount': 'mean',
                'margin_without_discount': 'mean'
            }).reset_index()
            
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='With Discount',
                x=margin_comp['discount_type'],
                y=margin_comp['margin_with_discount'],
                marker_color=COLORS['danger']
            ))
            fig.add_trace(go.Bar(
                name='Without Discount',
                x=margin_comp['discount_type'],
                y=margin_comp['margin_without_discount'],
                marker_color=COLORS['success']
            ))
            fig.update_layout(
                title='Gross Margin: With vs Without Discount',
                yaxis_title='Margin (%)',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No discount data available for selected period")
    
    st.divider()
    
    # Revenue Waterfall (if showing single date)
    if start_date == end_date and not comp_kpis.empty:
        st.subheader("💧 Revenue Waterfall")
        
        row = comp_kpis.iloc[0]
        
        if 'full_price_revenue' in row and 'discounted_revenue' in row:
            categories = ['Full Price Revenue', 'Discounted Revenue', 'Total Revenue']
            values = [
                row.get('full_price_revenue', 0),
                row.get('discounted_revenue', 0),
                row.get('total_revenue', 0)
            ]
            
            fig = create_waterfall(categories, values, title="Revenue Breakdown")
            st.plotly_chart(fig, use_container_width=True)
