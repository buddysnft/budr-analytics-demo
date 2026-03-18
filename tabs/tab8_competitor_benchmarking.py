"""
Tab 8: Competitor Benchmarking
BUDR vs CT market pricing, product gaps, deal frequency, out-of-stock opportunities
"""
import streamlit as st
import pandas as pd
from components.charts import create_comparison_chart, create_bar_chart, create_line_chart
from config.config import COLORS


def render(db: DatabaseConnector, selected_date: str, selected_locations: list,
          start_date: str, end_date: str):
    """Render Competitor Benchmarking tab"""
    
    st.header("🏁 Competitor Benchmarking")
    
    # Get competitor data
    competitor_benchmarks = db.get_competitor_benchmarks(selected_date)
    
    # BUDR vs CT Market Pricing
    st.subheader("💵 BUDR Pricing vs CT Market")
    
    if not competitor_benchmarks['position'].empty:
        position_df = competitor_benchmarks['position']
        
        # Price comparison chart
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='BUDR',
            x=position_df['category'],
            y=position_df['budr_avg_price'],
            marker_color=COLORS['primary'],
            text=position_df['budr_avg_price'].apply(lambda x: f"${x:.2f}"),
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='CT Market Avg',
            x=position_df['category'],
            y=position_df['market_avg_price'],
            marker_color=COLORS['secondary'],
            text=position_df['market_avg_price'].apply(lambda x: f"${x:.2f}"),
            textposition='outside'
        ))
        
        # Add market min/max as error bars
        fig.add_trace(go.Scatter(
            name='Market Range',
            x=position_df['category'],
            y=position_df['market_avg_price'],
            error_y=dict(
                type='data',
                symmetric=False,
                array=position_df['market_max_price'] - position_df['market_avg_price'],
                arrayminus=position_df['market_avg_price'] - position_df['market_min_price']
            ),
            mode='markers',
            marker=dict(size=10, color='rgba(0,0,0,0)'),
            showlegend=True
        ))
        
        fig.update_layout(
            title="BUDR vs CT Market Pricing by Category",
            barmode='group',
            yaxis_title="Price ($)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Price variance analysis
        st.caption("Price Positioning Analysis")
        
        position_df['price_variance_pct'] = ((position_df['budr_avg_price'] - position_df['market_avg_price']) / 
                                              position_df['market_avg_price'] * 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cheaper = len(position_df[position_df['price_variance_pct'] < -5])
            st.metric("Cheaper than Market", f"{cheaper} categories", 
                     help="Categories priced >5% below market average")
        
        with col2:
            at_market = len(position_df[position_df['price_variance_pct'].between(-5, 5)])
            st.metric("At Market Price", f"{at_market} categories",
                     help="Categories priced within ±5% of market")
        
        with col3:
            premium = len(position_df[position_df['price_variance_pct'] > 5])
            st.metric("Premium Priced", f"{premium} categories",
                     help="Categories priced >5% above market")
        
        # Detailed positioning table
        st.dataframe(
            position_df[['category', 'budr_avg_price', 'market_avg_price', 'market_min_price', 
                        'market_max_price', 'price_variance_pct']].style.format({
                'budr_avg_price': '${:.2f}',
                'market_avg_price': '${:.2f}',
                'market_min_price': '${:.2f}',
                'market_max_price': '${:.2f}',
                'price_variance_pct': '{:+.1f}%'
            }).applymap(
                lambda x: 'background-color: lightgreen' if isinstance(x, (int, float)) and x < -5 
                else ('background-color: lightcoral' if isinstance(x, (int, float)) and x > 5 else ''),
                subset=['price_variance_pct']
            ),
            use_container_width=True
        )
    
    st.divider()
    
    # Product Availability Gaps
    st.subheader("🔍 Product Availability Gaps")
    
    if not competitor_benchmarks['competitors'].empty and not competitor_benchmarks['position'].empty:
        competitors_df = competitor_benchmarks['competitors']
        position_df = competitor_benchmarks['position']
        
        # Calculate average competitor product count vs BUDR
        col1, col2 = st.columns(2)
        
        with col1:
            # Product count comparison
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='BUDR',
                x=position_df['category'],
                y=position_df['budr_product_count'],
                marker_color=COLORS['primary']
            ))
            
            fig.add_trace(go.Bar(
                name='CT Market Avg',
                x=position_df['category'],
                y=position_df['market_avg_product_count'],
                marker_color=COLORS['secondary']
            ))
            
            fig.update_layout(
                title="Product Count: BUDR vs Market Average",
                barmode='group',
                yaxis_title="Number of Products",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Assortment gap percentage
            position_df['assortment_gap_pct'] = ((position_df['market_avg_product_count'] - position_df['budr_product_count']) / 
                                                  position_df['market_avg_product_count'] * 100)
            
            fig = create_bar_chart(
                position_df.sort_values('assortment_gap_pct', ascending=False),
                'category', 'assortment_gap_pct',
                title="Assortment Gap vs Market (%)",
                color=COLORS['warning']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Opportunities table
        st.caption("Product Gap Opportunities")
        
        gaps_df = position_df[position_df['assortment_gap_pct'] > 10].copy()
        
        if not gaps_df.empty:
            st.dataframe(
                gaps_df[['category', 'budr_product_count', 'market_avg_product_count', 
                        'assortment_gap_pct', 'revenue_opportunity_assortment']].style.format({
                    'budr_product_count': '{:.0f}',
                    'market_avg_product_count': '{:.0f}',
                    'assortment_gap_pct': '{:.1f}%',
                    'revenue_opportunity_assortment': '${:,.0f}'
                }),
                use_container_width=True
            )
        else:
            st.success("✅ BUDR has competitive product assortment across all categories")
    
    st.divider()
    
    # Deal Frequency Comparison
    st.subheader("🎁 Deal Frequency Comparison")
    
    if not competitor_benchmarks['competitors'].empty:
        competitors_df = competitor_benchmarks['competitors']
        
        # Bar chart: Active deals by competitor
        fig = create_bar_chart(
            competitors_df.sort_values('active_deals_count', ascending=False),
            'dispensary_name', 'active_deals_count',
            title="Active Deals by Competitor",
            orientation='h',
            color=COLORS['success']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Average deals
        avg_deals = competitors_df['active_deals_count'].mean()
        budr_deals_query = f"""
            SELECT COUNT(*) as budr_deals
            FROM budr_discount_analysis
            WHERE analysis_date = %s
            {'AND location_id IN (' + ','.join(map(str, selected_locations)) + ')' if selected_locations else ''}
        """
        
        try:
            budr_deals_result = db.execute_query(budr_deals_query, (selected_date,))
            budr_deals = budr_deals_result['budr_deals'].iloc[0] if not budr_deals_result.empty else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("BUDR Active Deals", f"{budr_deals}")
            
            with col2:
                st.metric("Market Avg Active Deals", f"{avg_deals:.1f}")
            
            with col3:
                variance = ((budr_deals - avg_deals) / avg_deals * 100) if avg_deals > 0 else 0
                st.metric("vs Market", f"{variance:+.1f}%")
        
        except:
            st.info("BUDR deal data not available for comparison")
    
    st.divider()
    
    # Out-of-Stock Opportunities
    st.subheader("🎯 Out-of-Stock Opportunities")
    
    # Query for competitor out-of-stock products
    competitor_oos_query = """
        SELECT 
            d.name as dispensary_name,
            d.location as dispensary_location,
            p.name as product_name,
            p.category,
            pp.scrape_date,
            pp.in_stock
        FROM product_pricing pp
        JOIN products p ON pp.product_id = p.id
        JOIN dispensaries d ON p.dispensary_id = d.id
        WHERE pp.scrape_date BETWEEN %s AND %s
        AND pp.in_stock = false
        ORDER BY pp.scrape_date DESC, d.name
        LIMIT 100
    """
    
    try:
        competitor_oos = db.execute_query(competitor_oos_query, (start_date, end_date))
        
        if not competitor_oos.empty:
            # Count out-of-stock by category
            oos_by_category = competitor_oos.groupby('category').size().reset_index(name='oos_count')
            oos_by_category = oos_by_category.sort_values('oos_count', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Competitor Stockouts by Category")
                fig = create_bar_chart(
                    oos_by_category,
                    'category', 'oos_count',
                    title="Out-of-Stock Count by Category",
                    color=COLORS['danger']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.caption("Top Out-of-Stock Items")
                oos_products = competitor_oos.groupby(['product_name', 'category']).size().reset_index(name='times_oos')
                oos_products = oos_products.sort_values('times_oos', ascending=False).head(10)
                
                st.dataframe(
                    oos_products.style.format({'times_oos': '{:,}'}),
                    use_container_width=True
                )
            
            # Opportunity: What BUDR has that competitors don't
            st.caption("💡 Opportunity: Items BUDR has in stock that competitors are missing")
            
            # This would require a cross-reference between BUDR inventory and competitor OOS
            # Placeholder for now
            st.info("Cross-reference analysis requires BUDR product catalog mapping to competitor products")
        
        else:
            st.success("✅ No competitor out-of-stock data found")
    
    except Exception as e:
        st.warning(f"Out-of-stock analysis not available: {str(e)}")
    
    st.divider()
    
    # Competitive Summary
    st.subheader("📊 Competitive Summary")
    
    if not competitor_benchmarks['competitors'].empty:
        competitors_df = competitor_benchmarks['competitors']
        
        # Overall market summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_competitors = len(competitors_df)
            st.metric("Total Competitors Tracked", total_competitors)
        
        with col2:
            avg_products = competitors_df['total_products'].mean()
            st.metric("Avg Competitor Product Count", f"{avg_products:.0f}")
        
        with col3:
            avg_oos_pct = competitors_df['out_of_stock_pct'].mean()
            st.metric("Market Avg Out-of-Stock %", f"{avg_oos_pct:.1f}%")
        
        # Detailed competitor table
        st.caption("Competitor Details")
        st.dataframe(
            competitors_df[['dispensary_name', 'dispensary_location', 'total_products', 
                           'avg_flower_price_per_gram', 'avg_edible_price', 'avg_vape_price',
                           'active_deals_count', 'out_of_stock_pct']].style.format({
                'total_products': '{:,}',
                'avg_flower_price_per_gram': '${:.2f}',
                'avg_edible_price': '${:.2f}',
                'avg_vape_price': '${:.2f}',
                'active_deals_count': '{:,}',
                'out_of_stock_pct': '{:.1f}%'
            }),
            use_container_width=True
        )
