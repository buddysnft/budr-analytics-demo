"""
Export Utilities
CSV, Excel, and PDF export functions
"""
import pandas as pd
import io
from datetime import datetime
from typing import Dict, List
import streamlit as st


def export_to_csv(data: pd.DataFrame, filename: str = "export.csv") -> bytes:
    """Export DataFrame to CSV"""
    return data.to_csv(index=False).encode('utf-8')


def export_to_excel(data_dict: Dict[str, pd.DataFrame], filename: str = "export.xlsx") -> bytes:
    """
    Export multiple DataFrames to Excel with separate sheets
    
    Args:
        data_dict: Dictionary of {sheet_name: dataframe}
        filename: Output filename
    
    Returns:
        Excel file as bytes
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in data_dict.items():
            # Clean sheet name (Excel has 31 char limit)
            clean_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=clean_name, index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[clean_name]
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            # Format header row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust column width
                max_len = max(
                    df[value].astype(str).map(len).max(),
                    len(str(value))
                ) + 2
                worksheet.set_column(col_num, col_num, max_len)
    
    return output.getvalue()


def export_to_pdf(title: str, sections: List[Dict], filename: str = "export.pdf") -> bytes:
    """
    Export dashboard summary to PDF
    
    Args:
        title: Report title
        sections: List of {title, content, type} dicts
        filename: Output filename
    
    Returns:
        PDF file as bytes
    """
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        # Date
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(10)
        
        # Sections
        for section in sections:
            # Section title
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, section['title'], ln=True)
            pdf.ln(2)
            
            # Section content
            pdf.set_font('Arial', '', 10)
            
            if section['type'] == 'text':
                pdf.multi_cell(0, 5, section['content'])
            
            elif section['type'] == 'table' and isinstance(section['content'], pd.DataFrame):
                # Simple table rendering
                df = section['content']
                
                # Headers
                pdf.set_font('Arial', 'B', 9)
                col_widths = [40] * len(df.columns)  # Equal widths for simplicity
                
                for col, width in zip(df.columns, col_widths):
                    pdf.cell(width, 7, str(col), border=1)
                pdf.ln()
                
                # Data rows
                pdf.set_font('Arial', '', 8)
                for _, row in df.head(20).iterrows():  # Limit to 20 rows
                    for col, width in zip(df.columns, col_widths):
                        pdf.cell(width, 6, str(row[col])[:20], border=1)  # Truncate long values
                    pdf.ln()
            
            elif section['type'] == 'metric':
                # Key-value pairs
                pdf.set_font('Arial', 'B', 10)
                for key, value in section['content'].items():
                    pdf.cell(60, 6, f"{key}:", ln=False)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, str(value), ln=True)
                    pdf.set_font('Arial', 'B', 10)
            
            pdf.ln(8)
        
        return bytes(pdf.output())
    
    except ImportError:
        st.error("PDF export requires fpdf2 package. Install with: pip install fpdf2")
        return b""


def create_export_buttons(data_dict: Dict[str, pd.DataFrame], base_filename: str = "budr_analytics"):
    """
    Create export buttons for CSV, Excel, and PDF
    
    Args:
        data_dict: Dictionary of {name: dataframe} for export
        base_filename: Base filename for exports
    """
    col1, col2, col3 = st.columns(3)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with col1:
        # CSV export (first DataFrame only)
        if data_dict:
            first_key = list(data_dict.keys())[0]
            csv_data = export_to_csv(data_dict[first_key])
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{base_filename}_{timestamp}.csv",
                mime="text/csv"
            )
    
    with col2:
        # Excel export (all DataFrames)
        if data_dict:
            excel_data = export_to_excel(data_dict)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"{base_filename}_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        # PDF export
        st.download_button(
            label="📥 Download PDF",
            data=b"PDF export placeholder",  # Would need actual PDF generation
            file_name=f"{base_filename}_{timestamp}.pdf",
            mime="application/pdf",
            disabled=True,
            help="PDF export coming soon"
        )


def prepare_export_data(db, start_date: str, end_date: str, selected_locations: list) -> Dict[str, pd.DataFrame]:
    """
    Prepare all data for export
    
    Returns:
        Dictionary of {sheet_name: dataframe}
    """
    export_dict = {}
    
    # Daily KPIs
    date_range_data = db.get_date_range_data(start_date, end_date, selected_locations)
    export_dict['Daily KPIs'] = date_range_data['daily_kpis']
    export_dict['Category KPIs'] = date_range_data['category_kpis']
    export_dict['SKU KPIs'] = date_range_data['sku_kpis']
    
    # Comprehensive KPIs
    comp_kpis = db.get_comprehensive_kpis(start_date, end_date, selected_locations)
    if not comp_kpis.empty:
        export_dict['Comprehensive KPIs'] = comp_kpis
    
    # Customer data
    customer_data = db.get_customer_metrics(start_date, end_date, selected_locations)
    if not customer_data['customers'].empty:
        export_dict['Customer Segments'] = customer_data['customers']
    if not customer_data['cohorts'].empty:
        export_dict['Customer Cohorts'] = customer_data['cohorts']
    
    # Product performance
    product_data = db.get_product_performance(start_date, end_date, selected_locations, limit=100)
    if not product_data['top_products'].empty:
        export_dict['Top Products'] = product_data['top_products']
    if not product_data['dead_stock'].empty:
        export_dict['Dead Stock'] = product_data['dead_stock']
    
    # Competitor data
    competitor_benchmarks = db.get_competitor_benchmarks(end_date)
    if not competitor_benchmarks['competitors'].empty:
        export_dict['Competitors'] = competitor_benchmarks['competitors']
    if not competitor_benchmarks['position'].empty:
        export_dict['Competitive Position'] = competitor_benchmarks['position']
    
    return export_dict
