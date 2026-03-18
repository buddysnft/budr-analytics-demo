"""
Tab 7: Time Analysis
Sales by hour heatmap, day of week patterns, category demand by time, peak/slow periods
"""
import streamlit as st
import pandas as pd
import numpy as np
from components.charts import create_heatmap, create_line_chart, create_bar_chart
from utils.demo_data_loader import load_demo_data
from config.config import COLORS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Time Analysis tab"""
    
    st.header("⏰ Time Analysis")
    
    # Get hourly sales data
    hourly_data = db.get_hourly_patterns(start_date, end_date, selected_locations)
    comp_kpis = db.get_comprehensive_kpis(start_date, end_date, selected_locations)
    
    # Sales by Hour Heatmap
    st.subheader("🔥 Sales by Hour Heatmap")
    
    if not hourly_data.empty:
        # Pivot for heatmap
        hourly_pivot = hourly_data.pivot_table(
            index='day_of_week',
            columns='hour_of_day',
            values='avg_revenue',
            aggfunc='mean'
        )
        
        # Map day numbers to names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hourly_pivot.index = [day_names[int(i)] if i < len(day_names) else f"Day {i}" for i in hourly_pivot.index]
        
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Heatmap(
            z=hourly_pivot.values,
            x=hourly_pivot.columns,
            y=hourly_pivot.index,
            colorscale='YlOrRd',
            colorbar=dict(title="Avg Revenue ($)"),
            text=np.round(hourly_pivot.values, 0),
            texttemplate='$%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Average Revenue by Hour and Day of Week",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak hours identification
        col1, col2, col3 = st.columns(3)
        
        # Find peak hour
        peak_hour_data = hourly_data.groupby('hour_of_day')['avg_revenue'].mean().idxmax()
        peak_revenue = hourly_data.groupby('hour_of_day')['avg_revenue'].mean().max()
        
        with col1:
            st.metric("Peak Hour", f"{int(peak_hour_data):02d}:00", delta=f"${peak_revenue:,.0f} avg")
        
        # Find peak day
        peak_day_data = hourly_data.groupby('day_of_week')['avg_revenue'].mean().idxmax()
        peak_day_revenue = hourly_data.groupby('day_of_week')['avg_revenue'].mean().max()
        
        with col2:
            st.metric("Peak Day", day_names[int(peak_day_data)], delta=f"${peak_day_revenue:,.0f} avg")
        
        # Find slowest time
        slow_hour = hourly_data.groupby('hour_of_day')['avg_revenue'].mean().idxmin()
        
        with col3:
            st.metric("Slowest Hour", f"{int(slow_hour):02d}:00")
    
    st.divider()
    
    # Day of Week Patterns
    st.subheader("📅 Day of Week Patterns")
    
    if not hourly_data.empty:
        # Aggregate by day of week
        daily_patterns = hourly_data.groupby('day_of_week').agg({
            'avg_transactions': 'sum',
            'avg_revenue': 'sum',
            'avg_ticket': 'mean'
        }).reset_index()
        
        daily_patterns['day_name'] = daily_patterns['day_of_week'].apply(lambda x: day_names[int(x)])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by day
            import plotly.graph_objects as go
            
            fig = go.Figure(go.Bar(
                x=daily_patterns['day_name'],
                y=daily_patterns['avg_revenue'],
                marker_color=COLORS['primary'],
                text=daily_patterns['avg_revenue'].apply(lambda x: f"${x:,.0f}"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Average Revenue by Day of Week",
                xaxis_title="Day",
                yaxis_title="Revenue ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Transactions by day
            fig = go.Figure(go.Bar(
                x=daily_patterns['day_name'],
                y=daily_patterns['avg_transactions'],
                marker_color=COLORS['secondary'],
                text=daily_patterns['avg_transactions'].apply(lambda x: f"{x:,.0f}"),
                textposition='outside'
            ))
            fig.update_layout(
                title="Average Transactions by Day of Week",
                xaxis_title="Day",
                yaxis_title="Transactions",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Weekend vs Weekday comparison
        st.caption("Weekend vs Weekday Performance")
        
        daily_patterns['is_weekend'] = daily_patterns['day_of_week'].isin([5, 6])
        weekend_summary = daily_patterns.groupby('is_weekend').agg({
            'avg_transactions': 'mean',
            'avg_revenue': 'mean',
            'avg_ticket': 'mean'
        })
        
        col1, col2, col3 = st.columns(3)
        
        weekday_data = weekend_summary.loc[False] if False in weekend_summary.index else None
        weekend_data = weekend_summary.loc[True] if True in weekend_summary.index else None
        
        if weekday_data is not None and weekend_data is not None:
            with col1:
                rev_diff = ((weekend_data['avg_revenue'] - weekday_data['avg_revenue']) / 
                           weekday_data['avg_revenue'] * 100)
                st.metric("Weekend Revenue", f"${weekend_data['avg_revenue']:,.0f}", 
                         delta=f"{rev_diff:+.1f}% vs weekday")
            
            with col2:
                txn_diff = ((weekend_data['avg_transactions'] - weekday_data['avg_transactions']) / 
                           weekday_data['avg_transactions'] * 100)
                st.metric("Weekend Transactions", f"{weekend_data['avg_transactions']:,.0f}", 
                         delta=f"{txn_diff:+.1f}% vs weekday")
            
            with col3:
                ticket_diff = ((weekend_data['avg_ticket'] - weekday_data['avg_ticket']) / 
                              weekday_data['avg_ticket'] * 100)
                st.metric("Weekend Avg Ticket", f"${weekend_data['avg_ticket']:.2f}", 
                         delta=f"{ticket_diff:+.1f}% vs weekday")
    
    st.divider()
    
    # Category Demand by Time
    st.subheader("🏷️ Category Demand by Time of Day")
    
    # Query for category sales by hour
    category_time_query = f"""
        SELECT 
            h.hour_of_day,
            ti.product_id,
            p.category,
            SUM(ti.quantity) as units_sold,
            SUM(ti.line_total) as revenue
        FROM budr_hourly_sales h
        JOIN budr_transactions t ON h.sale_date = t.transaction_date 
            AND EXTRACT(HOUR FROM t.transaction_timestamp) = h.hour_of_day
        JOIN budr_transaction_items ti ON t.id = ti.transaction_id
        JOIN budr_products p ON ti.product_id = p.id
        WHERE h.sale_date BETWEEN %s AND %s
        {'AND h.location_id IN (' + ','.join(map(str, selected_locations)) + ')' if selected_locations else ''}
        GROUP BY h.hour_of_day, ti.product_id, p.category
        ORDER BY h.hour_of_day, revenue DESC
    """
    
    try:
        category_time = db.execute_query(category_time_query, (start_date, end_date))
        
        if not category_time.empty:
            # Aggregate by category and hour
            category_hourly = category_time.groupby(['hour_of_day', 'category']).agg({
                'revenue': 'sum'
            }).reset_index()
            
            # Pivot for stacked area chart
            category_pivot = category_hourly.pivot(
                index='hour_of_day',
                columns='category',
                values='revenue'
            ).fillna(0)
            
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            for category in category_pivot.columns:
                fig.add_trace(go.Scatter(
                    x=category_pivot.index,
                    y=category_pivot[category],
                    name=category,
                    mode='lines',
                    stackgroup='one',
                    fill='tonexty'
                ))
            
            fig.update_layout(
                title="Revenue by Category and Hour of Day",
                xaxis_title="Hour of Day",
                yaxis_title="Revenue ($)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Morning, afternoon, evening analysis
            st.caption("Category Performance by Time Period")
            
            category_time['time_period'] = category_time['hour_of_day'].apply(
                lambda x: 'Morning (6-11)' if 6 <= x < 12 
                else 'Afternoon (12-17)' if 12 <= x < 18 
                else 'Evening (18-22)' if 18 <= x < 23 
                else 'Other'
            )
            
            period_summary = category_time.groupby(['time_period', 'category']).agg({
                'revenue': 'sum'
            }).reset_index()
            
            # Bar chart by period
            import plotly.express as px
            
            fig = px.bar(
                period_summary[period_summary['time_period'] != 'Other'],
                x='time_period',
                y='revenue',
                color='category',
                title="Revenue by Time Period and Category",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.info(f"Category time analysis not available: {str(e)}")
    
    st.divider()
    
    # Peak vs Slow Period Identification
    st.subheader("📊 Peak vs Slow Periods")
    
    if not comp_kpis.empty:
        # Add day of week
        comp_kpis['day_of_week'] = pd.to_datetime(comp_kpis['kpi_date']).dt.dayofweek
        comp_kpis['day_name'] = comp_kpis['day_of_week'].apply(lambda x: day_names[x] if x < len(day_names) else f"Day {x}")
        
        # Identify top/bottom performing days
        revenue_by_date = comp_kpis[['kpi_date', 'day_name', 'total_revenue', 'total_transactions']].copy()
        revenue_by_date = revenue_by_date.sort_values('total_revenue', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("🏆 Top 10 Days by Revenue")
            st.dataframe(
                revenue_by_date.head(10)[['kpi_date', 'day_name', 'total_revenue', 'total_transactions']].style.format({
                    'total_revenue': '${:,.0f}',
                    'total_transactions': '{:,}'
                }),
                use_container_width=True
            )
        
        with col2:
            st.caption("📉 Bottom 10 Days by Revenue")
            st.dataframe(
                revenue_by_date.tail(10)[['kpi_date', 'day_name', 'total_revenue', 'total_transactions']].style.format({
                    'total_revenue': '${:,.0f}',
                    'total_transactions': '{:,}'
                }),
                use_container_width=True
            )
