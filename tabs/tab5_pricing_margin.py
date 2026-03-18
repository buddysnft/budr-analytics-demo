"""
Tab 5: Pricing & Margin
Gross margin by category, BUDR vs CT pricing, discount trends, promo impact
"""
import streamlit as st
import pandas as pd
from components.charts import create_bar_chart, create_line_chart, create_comparison_chart
from config.config import COLORS


def render(db, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Pricing & Margin tab"""
    
    st.header("💵 Pricing & Margin Analysis")
    
    # Get data
    date_range_data = db.get_date_range_data(start_date, end_date, selected_locations)
    category_kpis = date_range_data['category_kpis']
    competitor_data = db.get_competitor_benchmarks(selected_date)
    discount_data = db.get_discount_analysis(start_date, end_date, selected_locations)
    
    # Gross Margin by Category
    st.subheader("📊 Gross Margin by Category")
    
    if not category_kpis.empty:
        margin_summary = category_kpis.groupby('category').agg({
            'gross_margin_pct': 'mean',
            'gross_profit': 'sum',
            'total_revenue': 'sum',
            'total_cogs': 'sum'
        }).reset_index()
        
        margin_summary = margin_summary.sort_values('gross_margin_pct', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_bar_chart(
                margin_summary, 'category', 'gross_margin_pct',
                title="Gross Margin % by Category",
                color=COLORS['success']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_bar_chart(
                margin_summary, 'category', 'gross_profit',
                title="Total Gross Profit by Category",
                color=COLORS['primary']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Margin table
        st.dataframe(
            margin_summary.style.format({
                'gross_margin_pct': '{:.1f}%',
                'gross_profit': '${:,.0f}',
                'total_revenue': '${:,.0f}',
                'total_cogs': '${:,.0f}'
            }).background_gradient(subset=['gross_margin_pct'], cmap='RdYlGn'),
            use_container_width=True
        )
    
    st.divider()
    
    # BUDR vs Market Pricing
    st.subheader("🏷️ Price Comparison: BUDR vs CT Market")
    
    if not competitor_data['position'].empty:
        position_df = competitor_data['position']
        
        # Comparison chart
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='BUDR',
            x=position_df['category'],
            y=position_df['budr_avg_price'],
            marker_color=COLORS['primary']
        ))
        
        fig.add_trace(go.Bar(
            name='CT Market Avg',
            x=position_df['category'],
            y=position_df['market_avg_price'],
            marker_color=COLORS['secondary']
        ))
        
        fig.update_layout(
            title="BUDR vs Market Average Price by Category",
            barmode='group',
            yaxis_title="Price ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Price variance analysis
        st.caption("Price Positioning")
        
        position_df['price_variance'] = ((position_df['budr_avg_price'] - position_df['market_avg_price']) / 
                                         position_df['market_avg_price'] * 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cheaper_count = len(position_df[position_df['price_variance'] < 0])
            st.metric("Categories Below Market", cheaper_count)
        
        with col2:
            at_market = len(position_df[position_df['price_variance'].between(-5, 5)])
            st.metric("Categories At Market (±5%)", at_market)
        
        with col3:
            premium_count = len(position_df[position_df['price_variance'] > 0])
            st.metric("Categories Above Market", premium_count)
        
        # Detailed positioning table
        st.dataframe(
            position_df[['category', 'budr_avg_price', 'market_avg_price', 'price_variance']].style.format({
                'budr_avg_price': '${:.2f}',
                'market_avg_price': '${:.2f}',
                'price_variance': '{:+.1f}%'
            }).applymap(lambda x: 'background-color: lightgreen' if isinstance(x, (int, float)) and x < 0 
                       else ('background-color: lightcoral' if isinstance(x, (int, float)) and x > 5 else ''),
                       subset=['price_variance']),
            use_container_width=True
        )
    else:
        st.info("Competitor pricing data not available")
    
    st.divider()
    
    # Discount Usage Trends
    st.subheader("🎁 Discount Usage Trends")
    
    if not discount_data.empty:
        # Aggregate discount metrics over time
        discount_trend = discount_data.groupby('analysis_date').agg({
            'total_discount_amount': 'sum',
            'discount_usage_rate': 'mean',
            'avg_discount_pct': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_line_chart(
                discount_trend, 'analysis_date', ['total_discount_amount'],
                title="Total Discount Amount Over Time",
                labels={'total_discount_amount': 'Discount $ '}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_line_chart(
                discount_trend, 'analysis_date', ['discount_usage_rate', 'avg_discount_pct'],
                title="Discount Metrics Over Time",
                labels={'discount_usage_rate': 'Usage Rate %', 'avg_discount_pct': 'Avg Discount %'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Discount by type
        discount_by_type = discount_data.groupby('discount_type').agg({
            'total_discount_amount': 'sum',
            'transactions_with_discount': 'sum',
            'discount_usage_rate': 'mean'
        }).reset_index()
        
        st.caption("Discount Performance by Type")
        st.dataframe(
            discount_by_type.style.format({
                'total_discount_amount': '${:,.0f}',
                'transactions_with_discount': '{:,}',
                'discount_usage_rate': '{:.1f}%'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # Margin Impact of Promotions
    st.subheader("📉 Promotion Impact on Margin")
    
    if not discount_data.empty and 'margin_with_discount' in discount_data.columns:
        # Calculate margin impact
        discount_data['margin_impact'] = discount_data['margin_without_discount'] - discount_data['margin_with_discount']
        
        margin_impact = discount_data.groupby('discount_type').agg({
            'margin_with_discount': 'mean',
            'margin_without_discount': 'mean',
            'margin_impact': 'mean',
            'discount_roi': 'mean' if 'discount_roi' in discount_data.columns else lambda x: None
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Margin comparison
            import plotly.graph_objects as go
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='With Discount',
                x=margin_impact['discount_type'],
                y=margin_impact['margin_with_discount'],
                marker_color=COLORS['danger']
            ))
            fig.add_trace(go.Bar(
                name='Without Discount',
                x=margin_impact['discount_type'],
                y=margin_impact['margin_without_discount'],
                marker_color=COLORS['success']
            ))
            fig.update_layout(
                title='Margin: With vs Without Discount',
                yaxis_title='Margin (%)',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ROI chart
            if 'discount_roi' in margin_impact.columns and margin_impact['discount_roi'].notna().any():
                fig = create_bar_chart(
                    margin_impact.sort_values('discount_roi', ascending=False),
                    'discount_type', 'discount_roi',
                    title="Discount ROI by Type",
                    color=COLORS['info']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ROI data not available")
        
        # Impact summary
        st.caption("Promotion Impact Summary")
        st.dataframe(
            margin_impact.style.format({
                'margin_with_discount': '{:.1f}%',
                'margin_without_discount': '{:.1f}%',
                'margin_impact': '{:.1f}pp',
                'discount_roi': '{:.2f}x'
            }),
            use_container_width=True
        )
    else:
        st.info("Margin impact data not available")
