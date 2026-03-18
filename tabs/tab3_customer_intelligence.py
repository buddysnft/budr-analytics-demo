"""
Tab 3: Customer Intelligence
New vs returning, LTV, purchase frequency, retention, demographics
"""
import streamlit as st
import pandas as pd
from components.charts import (create_pie_chart, create_line_chart, create_retention_curve,
                               create_distribution_histogram, create_bar_chart)
from config.config import COLORS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Customer Intelligence tab"""
    
    st.header("👥 Customer Intelligence")
    
    # Get customer metrics
    customer_data = db.get_customer_metrics(start_date, end_date, selected_locations)
    comp_kpis = db.get_comprehensive_kpis(start_date, end_date, selected_locations)
    
    # New vs Returning
    st.subheader("🆕 New vs Returning Customers")
    
    if not comp_kpis.empty:
        # Calculate totals
        total_new = comp_kpis['new_customers'].sum()
        total_returning = comp_kpis['returning_customers'].sum()
        total_customers = total_new + total_returning
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Customers", f"{total_customers:,}")
        
        with col2:
            new_pct = (total_new / total_customers * 100) if total_customers > 0 else 0
            st.metric("New Customers", f"{total_new:,}", delta=f"{new_pct:.1f}%")
        
        with col3:
            returning_pct = (total_returning / total_customers * 100) if total_customers > 0 else 0
            st.metric("Returning Customers", f"{total_returning:,}", delta=f"{returning_pct:.1f}%")
        
        # Pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            pie_data = pd.DataFrame({
                'type': ['New', 'Returning'],
                'count': [total_new, total_returning]
            })
            fig = create_pie_chart(
                pie_data, 'type', 'count',
                title="Customer Split"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Trend over time
            fig = create_line_chart(
                comp_kpis, 'kpi_date', ['new_customers', 'returning_customers'],
                title="New vs Returning Trend",
                labels={'new_customers': 'New', 'returning_customers': 'Returning'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Customer Lifetime Value (LTV)
    st.subheader("💎 Customer Lifetime Value")
    
    if not customer_data['customers'].empty:
        customers_df = customer_data['customers']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overall_ltv = customers_df['avg_ltv'].mean()
            st.metric("Average LTV", f"${overall_ltv:,.2f}")
        
        with col2:
            overall_orders = customers_df['avg_orders'].mean()
            st.metric("Avg Orders per Customer", f"{overall_orders:.1f}")
        
        with col3:
            overall_aov = customers_df['avg_aov'].mean()
            st.metric("Avg Order Value", f"${overall_aov:.2f}")
        
        # LTV by segment
        st.caption("LTV by Customer Segment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: LTV by segment
            fig = create_bar_chart(
                customers_df.sort_values('avg_ltv', ascending=False),
                'customer_segment', 'avg_ltv',
                title="Average LTV by Segment",
                color=COLORS['success']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Customer count by segment
            fig = create_bar_chart(
                customers_df.sort_values('customer_count', ascending=False),
                'customer_segment', 'customer_count',
                title="Customer Count by Segment",
                color=COLORS['info']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Segment summary table
        st.caption("Segment Performance Summary")
        st.dataframe(
            customers_df.style.format({
                'customer_count': '{:,}',
                'avg_ltv': '${:,.2f}',
                'avg_orders': '{:.1f}',
                'avg_aov': '${:.2f}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # Purchase Frequency
    st.subheader("🔄 Purchase Frequency")
    
    if not customer_data['customers'].empty:
        customers_df = customer_data['customers']
        
        # Create distribution data
        # Assuming avg_orders represents purchase frequency
        fig = create_distribution_histogram(
            customers_df, 'avg_orders',
            title="Distribution of Purchase Frequency",
            bins=20
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Frequency by segment
        st.caption("Average Purchase Frequency by Segment")
        
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Bar(
            x=customers_df['customer_segment'],
            y=customers_df['avg_orders'],
            marker_color=COLORS['primary'],
            text=customers_df['avg_orders'].apply(lambda x: f"{x:.1f}"),
            textposition='outside'
        ))
        fig.update_layout(
            title="Orders per Customer by Segment",
            xaxis_title="Segment",
            yaxis_title="Avg Orders",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Retention Analysis
    st.subheader("📊 Customer Retention")
    
    if not customer_data['cohorts'].empty:
        cohorts_df = customer_data['cohorts']
        
        # Overall retention metrics
        latest_cohorts = cohorts_df[cohorts_df['months_since_first'] == 1]
        if not latest_cohorts.empty:
            avg_retention_1m = latest_cohorts['retention_rate'].mean()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("1-Month Retention", f"{avg_retention_1m:.1f}%")
            
            # 3-month and 6-month if available
            cohorts_3m = cohorts_df[cohorts_df['months_since_first'] == 3]
            if not cohorts_3m.empty:
                with col2:
                    avg_retention_3m = cohorts_3m['retention_rate'].mean()
                    st.metric("3-Month Retention", f"{avg_retention_3m:.1f}%")
            
            cohorts_6m = cohorts_df[cohorts_df['months_since_first'] == 6]
            if not cohorts_6m.empty:
                with col3:
                    avg_retention_6m = cohorts_6m['retention_rate'].mean()
                    st.metric("6-Month Retention", f"{avg_retention_6m:.1f}%")
        
        # Retention curve
        if len(cohorts_df['cohort_month'].unique()) > 1:
            fig = create_retention_curve(cohorts_df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Cohort heatmap
        st.caption("Cohort Retention Heatmap")
        
        # Pivot for heatmap
        pivot_cohort = cohorts_df.pivot(
            index='cohort_month',
            columns='months_since_first',
            values='retention_rate'
        )
        
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Heatmap(
            z=pivot_cohort.values,
            x=pivot_cohort.columns,
            y=pivot_cohort.index,
            colorscale='RdYlGn',
            text=pivot_cohort.values,
            texttemplate='%{text:.1f}%',
            textfont={"size": 10},
            colorbar=dict(title="Retention %")
        ))
        fig.update_layout(
            title="Cohort Retention Rate (%)",
            xaxis_title="Months Since First Purchase",
            yaxis_title="Cohort (First Purchase Month)",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cohort data not available - requires historical transaction data")
    
    st.divider()
    
    # Demographics (if available)
    st.subheader("📍 Customer Demographics")
    
    # Get customer data with demographics
    location_filter = ""
    if selected_locations:
        location_filter = f"AND location_id IN ({','.join(map(str, selected_locations))})"
    
    demo_query = f"""
        SELECT 
            zip_code,
            COUNT(*) as customer_count,
            AVG(total_revenue) as avg_ltv,
            AVG(distance_miles) as avg_distance
        FROM budr_customers
        WHERE last_purchase_date BETWEEN %s AND %s
        {location_filter}
        AND zip_code IS NOT NULL
        GROUP BY zip_code
        ORDER BY customer_count DESC
        LIMIT 20
    """
    
    try:
        demo_data = db.execute_query(demo_query, (start_date, end_date))
        
        if not demo_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Top ZIP Codes by Customer Count")
                fig = create_bar_chart(
                    demo_data.head(10),
                    'zip_code', 'customer_count',
                    title="Top 10 ZIP Codes",
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.caption("Average LTV by ZIP Code")
                fig = create_bar_chart(
                    demo_data.head(10),
                    'zip_code', 'avg_ltv',
                    title="Avg LTV by ZIP (Top 10)",
                    orientation='h',
                    color=COLORS['success']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Distance distribution
            if 'avg_distance' in demo_data.columns:
                st.caption("Customer Distance Distribution")
                fig = create_distribution_histogram(
                    demo_data, 'avg_distance',
                    title="Distance from Store (miles)",
                    bins=15
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # ZIP code table
            st.caption("ZIP Code Performance")
            st.dataframe(
                demo_data.style.format({
                    'customer_count': '{:,}',
                    'avg_ltv': '${:,.2f}',
                    'avg_distance': '{:.1f} mi'
                }),
                use_container_width=True
            )
        else:
            st.info("No demographic data available")
    
    except Exception as e:
        st.warning(f"Demographics data not available: {str(e)}")
    
    st.divider()
    
    # Customer Segment Details
    st.subheader("🎯 Top Customer Segments")
    
    if not customer_data['customers'].empty:
        customers_df = customer_data['customers']
        
        # Show top segments with key metrics
        for _, segment in customers_df.iterrows():
            with st.expander(f"{segment['customer_segment'].title()} - {segment['customer_count']:,} customers"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Avg LTV", f"${segment['avg_ltv']:,.2f}")
                
                with col2:
                    st.metric("Avg Orders", f"{segment['avg_orders']:.1f}")
                
                with col3:
                    st.metric("Avg AOV", f"${segment['avg_aov']:.2f}")
                
                with col4:
                    total_value = segment['customer_count'] * segment['avg_ltv']
                    st.metric("Total Segment Value", f"${total_value:,.0f}")
