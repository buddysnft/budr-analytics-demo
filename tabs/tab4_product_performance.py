"""
Tab 4: Product Performance
Top/bottom SKUs, category ranking, turnover, dead stock, velocity, market basket
"""
import streamlit as st
import pandas as pd
from components.charts import create_bar_chart, create_heatmap, create_scatter
from config.config import COLORS, THRESHOLDS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Product Performance tab"""
    
    st.header("📦 Product Performance")
    
    # Get product performance data
    product_data = db.get_product_performance(start_date, end_date, selected_locations, limit=50)
    date_range_data = db.get_date_range_data(start_date, end_date, selected_locations)
    category_kpis = date_range_data['category_kpis']
    
    # Top/Bottom SKUs
    st.subheader("🏆 Top & Bottom Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("💚 Top 20 Products by Revenue")
        if not product_data['top_products'].empty:
            top_df = product_data['top_products'].head(20)
            
            # Display table
            st.dataframe(
                top_df[['product_name', 'category', 'total_revenue', 'total_units_sold', 'avg_margin']].style.format({
                    'total_revenue': '${:,.0f}',
                    'total_units_sold': '{:,}',
                    'avg_margin': '{:.1f}%'
                }),
                use_container_width=True,
                height=400
            )
    
    with col2:
        st.caption("🔴 Bottom 20 Products by Revenue")
        if not product_data['bottom_products'].empty:
            bottom_df = product_data['bottom_products'].head(20)
            
            st.dataframe(
                bottom_df[['product_name', 'category', 'total_revenue', 'total_units_sold', 'avg_margin']].style.format({
                    'total_revenue': '${:,.0f}',
                    'total_units_sold': '{:,}',
                    'avg_margin': '{:.1f}%'
                }),
                use_container_width=True,
                height=400
            )
    
    # Top 10 visualization
    if not product_data['top_products'].empty:
        st.caption("Top 10 Products - Revenue vs Margin")
        top10 = product_data['top_products'].head(10)
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Revenue',
            x=top10['product_name'],
            y=top10['total_revenue'],
            yaxis='y',
            marker_color=COLORS['primary']
        ))
        
        fig.add_trace(go.Scatter(
            name='Margin %',
            x=top10['product_name'],
            y=top10['avg_margin'],
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=10, color=COLORS['success']),
            line=dict(width=3)
        ))
        
        fig.update_layout(
            yaxis=dict(title='Revenue ($)'),
            yaxis2=dict(title='Margin (%)', overlaying='y', side='right'),
            xaxis=dict(tickangle=-45),
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Category Performance Ranking
    st.subheader("📊 Category Performance Ranking")
    
    if not category_kpis.empty:
        # Aggregate by category
        category_summary = category_kpis.groupby('category').agg({
            'total_revenue': 'sum',
            'units_sold': 'sum',
            'gross_margin_pct': 'mean',
            'days_to_sellthrough': 'mean',
            'units_per_day': 'mean'
        }).reset_index()
        
        category_summary = category_summary.sort_values('total_revenue', ascending=False)
        
        # Display table with conditional formatting
        st.dataframe(
            category_summary.style.format({
                'total_revenue': '${:,.0f}',
                'units_sold': '{:,}',
                'gross_margin_pct': '{:.1f}%',
                'days_to_sellthrough': '{:.1f}',
                'units_per_day': '{:.1f}'
            }).background_gradient(subset=['total_revenue'], cmap='Greens')
              .background_gradient(subset=['gross_margin_pct'], cmap='Blues'),
            use_container_width=True
        )
        
        # Scatter: Revenue vs Margin by category
        st.caption("Category Positioning: Revenue vs Margin")
        
        fig = create_scatter(
            category_summary, 'total_revenue', 'gross_margin_pct',
            size_col='units_sold', color_col='category',
            title="Revenue vs Margin by Category",
            hover_data=['category', 'units_sold']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Inventory Turnover Heatmap
    st.subheader("🔥 Inventory Turnover Heatmap")
    
    if not date_range_data['sku_kpis'].empty:
        sku_kpis = date_range_data['sku_kpis']
        
        # Filter to recent data and aggregate
        velocity_df = sku_kpis.groupby(['category', 'product_name']).agg({
            'units_per_day': 'mean',
            'days_to_sellthrough': 'mean'
        }).reset_index()
        
        # Top 30 products by velocity
        velocity_df = velocity_df.nlargest(30, 'units_per_day')
        
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Heatmap(
            x=velocity_df['product_name'],
            y=velocity_df['category'],
            z=velocity_df['units_per_day'],
            colorscale='Reds',
            colorbar=dict(title="Units/Day")
        ))
        
        fig.update_layout(
            title="Velocity Heatmap (Top 30 Products)",
            xaxis=dict(tickangle=-45),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Dead Stock Alerts
    st.subheader("⚠️ Dead Stock Alerts")
    
    if not product_data['dead_stock'].empty:
        dead_stock = product_data['dead_stock']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.caption(f"Products with no sales in {THRESHOLDS['dead_stock_days']}+ days")
            
            st.dataframe(
                dead_stock[['product_name', 'category', 'days_since_last_sale', 'inventory_value', 'recommendation']].style.format({
                    'days_since_last_sale': '{:,.0f} days',
                    'inventory_value': '${:,.2f}'
                }),
                use_container_width=True,
                height=400
            )
        
        with col2:
            # Summary metrics
            total_dead_value = dead_stock['inventory_value'].sum()
            avg_days_dead = dead_stock['days_since_last_sale'].mean()
            
            st.metric("Total Dead Stock Value", f"${total_dead_value:,.0f}")
            st.metric("Avg Days Since Last Sale", f"{avg_days_dead:.0f}")
            
            # Recommendations breakdown
            st.caption("Recommended Actions")
            if 'recommendation' in dead_stock.columns:
                rec_counts = dead_stock['recommendation'].value_counts()
                for rec, count in rec_counts.items():
                    st.write(f"**{rec}**: {count} items")
    else:
        st.success("✅ No dead stock identified")
    
    st.divider()
    
    # Velocity Analysis
    st.subheader("⚡ SKU Velocity Analysis")
    
    if not date_range_data['sku_kpis'].empty:
        sku_kpis = date_range_data['sku_kpis']
        
        # Aggregate SKU performance
        sku_summary = sku_kpis.groupby(['product_name', 'category']).agg({
            'units_sold': 'sum',
            'revenue': 'sum',
            'units_per_day': 'mean',
            'gross_margin_pct': 'mean'
        }).reset_index()
        
        # Categorize velocity
        sku_summary['velocity_tier'] = pd.cut(
            sku_summary['units_per_day'],
            bins=[0, 1, 5, 10, float('inf')],
            labels=['Slow', 'Medium', 'Fast', 'Very Fast']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Velocity distribution
            velocity_counts = sku_summary['velocity_tier'].value_counts()
            
            import plotly.graph_objects as go
            
            colors_map = {'Slow': COLORS['danger'], 'Medium': COLORS['warning'], 
                         'Fast': COLORS['success'], 'Very Fast': COLORS['info']}
            
            fig = go.Figure(go.Pie(
                labels=velocity_counts.index,
                values=velocity_counts.values,
                marker_colors=[colors_map.get(tier, COLORS['primary']) for tier in velocity_counts.index],
                hole=0.4
            ))
            fig.update_layout(title="SKU Velocity Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top velocity SKUs
            st.caption("Fastest Moving SKUs")
            top_velocity = sku_summary.nlargest(10, 'units_per_day')
            
            st.dataframe(
                top_velocity[['product_name', 'units_per_day', 'revenue']].style.format({
                    'units_per_day': '{:.1f}',
                    'revenue': '${:,.0f}'
                }),
                use_container_width=True
            )
    
    st.divider()
    
    # Market Basket Analysis
    st.subheader("🛒 Market Basket Analysis")
    
    basket_data = db.get_basket_analysis(selected_date, selected_locations, limit=20)
    
    if not basket_data.empty:
        st.caption("Frequently Bought Together (Top 20 Pairs)")
        
        # Format for display
        basket_display = basket_data.copy()
        basket_display['pair'] = basket_display['product_a'] + ' + ' + basket_display['product_b']
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(
                basket_display[['pair', 'times_purchased_together', 'confidence', 'lift']].style.format({
                    'times_purchased_together': '{:,.0f}',
                    'confidence': '{:.1%}',
                    'lift': '{:.2f}x'
                }),
                use_container_width=True,
                height=400
            )
        
        with col2:
            st.caption("Lift Explanation")
            st.write("**Lift > 1.0**: Customers who buy Product A are more likely to buy Product B than average")
            st.write("**Confidence**: % of Product A buyers who also buy Product B")
            
            # Highlight high-lift pairs
            high_lift = basket_data[basket_data['lift'] > 2.0]
            if not high_lift.empty:
                st.success(f"🎯 {len(high_lift)} high-lift pairs (>2.0x) found!")
    else:
        st.info("Market basket data not available for selected date")
