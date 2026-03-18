#!/bin/bash
# Quick launch script for BUDR Analytics Demo

echo "🚀 Starting BUDR Analytics Demo Dashboard..."
echo ""
echo "📊 This demo includes:"
echo "   - 7 BUDR locations"
echo "   - 8 CT competitors"
echo "   - 30 days of sample data"
echo "   - All 8 tabs functional"
echo ""
echo "🌐 Dashboard will open at: http://localhost:8501"
echo ""

cd "$(dirname "$0")"
streamlit run app.py
