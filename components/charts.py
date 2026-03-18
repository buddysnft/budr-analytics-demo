"""
Chart Components Library
Reusable Plotly chart components for the dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List, Dict
from config.config import COLORS


def create_metric_card(value: float, title: str, delta: Optional[float] = None,
                       prefix: str = "", suffix: str = "", format_str: str = ",.2f") -> go.Figure:
    """Create a big number metric card with optional delta"""
    
    formatted_value = f"{prefix}{value:{format_str}}{suffix}"
    
    # Determine color based on delta
    color = COLORS['dark']
    if delta is not None:
        if delta > 0:
            color = COLORS['success']
        elif delta < 0:
            color = COLORS['danger']
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="number+delta" if delta is not None else "number",
        value=value,
        title={'text': title, 'font': {'size': 18}},
        number={'prefix': prefix, 'suffix': suffix, 'valueformat': format_str},
        delta={'reference': value - delta if delta else 0, 'relative': False} if delta else None,
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_sparkline(df: pd.DataFrame, x_col: str, y_col: str, 
                     color: str = COLORS['primary']) -> go.Figure:
    """Create a simple sparkline chart"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
    ))
    
    fig.update_layout(
        height=100,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig


def create_line_chart(df: pd.DataFrame, x_col: str, y_cols: List[str],
                     title: str = "", labels: Optional[Dict[str, str]] = None) -> go.Figure:
    """Create a multi-line trend chart"""
    
    fig = go.Figure()
    
    for i, y_col in enumerate(y_cols):
        label = labels.get(y_col, y_col) if labels else y_col
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            name=label,
            mode='lines+markers',
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title="Value",
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str,
                    title: str = "", orientation: str = 'v',
                    color: Optional[str] = None) -> go.Figure:
    """Create a bar chart"""
    
    if orientation == 'h':
        fig = go.Figure(go.Bar(
            y=df[x_col],
            x=df[y_col],
            orientation='h',
            marker_color=color or COLORS['primary']
        ))
    else:
        fig = go.Figure(go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color=color or COLORS['primary']
        ))
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=False
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str,
                    title: str = "", hole: float = 0.4) -> go.Figure:
    """Create a pie/donut chart"""
    
    fig = go.Figure(go.Pie(
        labels=df[names_col],
        values=df[values_col],
        hole=hole,
        textinfo='label+percent',
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
    )
    
    return fig


def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, z_col: str,
                  title: str = "", colorscale: str = "Blues") -> go.Figure:
    """Create a heatmap"""
    
    # Pivot data for heatmap
    pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col)
    
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=colorscale,
        hoverongaps=False,
        colorbar=dict(title=z_col)
    ))
    
    fig.update_layout(
        title=title,
        height=500,
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig


def create_stacked_bar(df: pd.DataFrame, x_col: str, y_cols: List[str],
                      title: str = "", labels: Optional[Dict[str, str]] = None) -> go.Figure:
    """Create a stacked bar chart"""
    
    fig = go.Figure()
    
    for y_col in y_cols:
        label = labels.get(y_col, y_col) if labels else y_col
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=label
        ))
    
    fig.update_layout(
        title=title,
        barmode='stack',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_scatter(df: pd.DataFrame, x_col: str, y_col: str,
                  size_col: Optional[str] = None, color_col: Optional[str] = None,
                  title: str = "", hover_data: Optional[List[str]] = None) -> go.Figure:
    """Create a scatter plot"""
    
    fig = px.scatter(
        df, x=x_col, y=y_col,
        size=size_col, color=color_col,
        hover_data=hover_data,
        title=title
    )
    
    fig.update_layout(height=500)
    
    return fig


def create_funnel(df: pd.DataFrame, stage_col: str, value_col: str,
                 title: str = "") -> go.Figure:
    """Create a funnel chart"""
    
    fig = go.Figure(go.Funnel(
        y=df[stage_col],
        x=df[value_col],
        textinfo="value+percent initial"
    ))
    
    fig.update_layout(
        title=title,
        height=400
    )
    
    return fig


def create_waterfall(categories: List[str], values: List[float],
                    title: str = "") -> go.Figure:
    """Create a waterfall chart"""
    
    fig = go.Figure(go.Waterfall(
        x=categories,
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=False
    )
    
    return fig


def create_gauge(value: float, max_value: float, title: str = "",
                threshold_yellow: float = 0.5, threshold_green: float = 0.75) -> go.Figure:
    """Create a gauge chart"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': COLORS['primary']},
            'steps': [
                {'range': [0, max_value * threshold_yellow], 'color': COLORS['danger']},
                {'range': [max_value * threshold_yellow, max_value * threshold_green], 'color': COLORS['warning']},
                {'range': [max_value * threshold_green, max_value], 'color': COLORS['success']}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * threshold_green
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig


def create_comparison_chart(df: pd.DataFrame, categories: List[str],
                           budr_col: str, market_col: str, title: str = "") -> go.Figure:
    """Create a grouped bar chart comparing BUDR vs Market"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='BUDR',
        x=categories,
        y=df[budr_col],
        marker_color=COLORS['primary']
    ))
    
    fig.add_trace(go.Bar(
        name='CT Market Avg',
        x=categories,
        y=df[market_col],
        marker_color=COLORS['secondary']
    ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_retention_curve(df: pd.DataFrame, title: str = "Customer Retention Curve") -> go.Figure:
    """Create a retention cohort curve"""
    
    fig = go.Figure()
    
    # Assuming df has columns: cohort_month, months_since_first, retention_rate
    for cohort in df['cohort_month'].unique():
        cohort_data = df[df['cohort_month'] == cohort]
        fig.add_trace(go.Scatter(
            x=cohort_data['months_since_first'],
            y=cohort_data['retention_rate'],
            mode='lines+markers',
            name=str(cohort)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Months Since First Purchase",
        yaxis_title="Retention Rate (%)",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_distribution_histogram(df: pd.DataFrame, column: str,
                                  title: str = "", bins: int = 30) -> go.Figure:
    """Create a distribution histogram"""
    
    fig = px.histogram(
        df, x=column,
        nbins=bins,
        title=title,
        marginal="box"  # Add box plot on top
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    return fig
