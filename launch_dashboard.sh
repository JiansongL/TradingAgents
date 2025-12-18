#!/bin/bash

# TradingAgents Web Interface Launcher
# Professional Financial Analysis Dashboard

echo "🚀 Starting TradingAgents Pro Dashboard..."
echo ""
echo "📊 Features:"
echo "   - Real-time market data visualization"
echo "   - Multi-agent AI analysis"
echo "   - Options trading with Greeks"
echo "   - RL profit probability prediction"
echo ""
echo "🌐 Dashboard will open in your browser..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install streamlit plotly kaleido
fi

# Launch streamlit app
streamlit run web_app.py \
    --server.port 8501 \
    --server.address localhost \
    --theme.primaryColor "#00ff88" \
    --theme.backgroundColor "#0a0e27" \
    --theme.secondaryBackgroundColor "#141829" \
    --theme.textColor "#ffffff" \
    --theme.font "sans serif"
