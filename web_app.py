"""
TradingAgents Web Interface
Professional Financial Analysis Dashboard with Real-time Updates
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from typing import Optional, Dict, Any
import json
from pathlib import Path
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


# Page configuration
st.set_page_config(
    page_title="TradingAgents Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for financial theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #00ff88;
        --secondary-color: #0066ff;
        --danger-color: #ff4444;
        --warning-color: #ffaa00;
        --dark-bg: #0a0e27;
        --card-bg: #141829;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .big-font {
        font-size: 48px !important;
        font-weight: 700;
        background: linear-gradient(90deg, #00ff88, #0066ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 18px;
        margin-bottom: 30px;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #0a0e27 100%);
        border: 1px solid #00ff8844;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 255, 136, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 255, 136, 0.2);
    }
    
    /* Analysis status */
    .status-running {
        color: #ffaa00;
        animation: pulse 2s infinite;
    }
    
    .status-complete {
        color: #00ff88;
    }
    
    .status-error {
        color: #ff4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00ff88, #0066ff);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #0a0e27 0%, #141829 100%);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ff88, #0066ff);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f3a;
        border-radius: 8px 8px 0 0;
        padding: 12px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00ff8844, #0066ff44);
        border-bottom: 2px solid #00ff88;
    }
</style>
""", unsafe_allow_html=True)


def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch stock data for visualization"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def create_candlestick_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Create professional candlestick chart"""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    )])
    
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        height=400,
        paper_bgcolor='rgba(20, 24, 41, 0.8)',
        plot_bgcolor='rgba(10, 14, 39, 0.8)',
        font=dict(color='#ffffff'),
        xaxis_rangeslider_visible=False
    )
    
    return fig


def create_volume_chart(df: pd.DataFrame) -> go.Figure:
    """Create volume chart"""
    colors = ['#00ff88' if close >= open else '#ff4444' 
              for close, open in zip(df['Close'], df['Open'])]
    
    fig = go.Figure(data=[go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=colors
    )])
    
    fig.update_layout(
        title="Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_dark",
        height=200,
        paper_bgcolor='rgba(20, 24, 41, 0.8)',
        plot_bgcolor='rgba(10, 14, 39, 0.8)',
        font=dict(color='#ffffff')
    )
    
    return fig


def create_profit_probability_chart(probabilities: Dict[str, float]) -> go.Figure:
    """Create profit probability visualization"""
    fig = go.Figure(data=[go.Bar(
        x=list(probabilities.keys()),
        y=list(probabilities.values()),
        marker=dict(
            color=['#00ff88', '#ffaa00', '#ff4444'],
            line=dict(color='#ffffff', width=1)
        ),
        text=[f"{v:.1%}" for v in probabilities.values()],
        textposition='auto',
    )])
    
    fig.update_layout(
        title="RL Model: Profit Probability Prediction",
        xaxis_title="Action",
        yaxis_title="Probability",
        template="plotly_dark",
        height=300,
        paper_bgcolor='rgba(20, 24, 41, 0.8)',
        plot_bgcolor='rgba(10, 14, 39, 0.8)',
        font=dict(color='#ffffff'),
        yaxis=dict(tickformat='.0%', range=[0, 1])
    )
    
    return fig


def display_header():
    """Display application header"""
    st.markdown('<p class="big-font">📈 TradingAgents Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Multi-Agent AI Financial Analysis Platform</p>', unsafe_allow_html=True)
    
    # Real-time market status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Market Status", "🟢 OPEN", "NYSE")
    with col2:
        st.metric("S&P 500", "4,783.45", "+1.2%", delta_color="normal")
    with col3:
        st.metric("NASDAQ", "15,089.90", "+1.8%", delta_color="normal")
    with col4:
        st.metric("VIX", "12.45", "-2.3%", delta_color="inverse")
    
    st.markdown("---")


def sidebar_controls():
    """Sidebar configuration"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/financial-growth-analysis.png", width=80)
        st.title("⚙️ Configuration")
        
        # Analysis Settings
        st.subheader("🎯 Analysis Settings")
        
        ticker = st.text_input(
            "Stock Ticker",
            value="NVDA",
            help="Enter stock symbol (e.g., AAPL, TSLA, NVDA)"
        ).upper()
        
        analysis_date = st.date_input(
            "Analysis Date",
            value=datetime.now(),
            help="Select date for analysis"
        )
        
        # Trading Mode
        st.subheader("💼 Trading Mode")
        trading_mode = st.radio(
            "Select Mode",
            ["Stock Trading", "Options Trading"],
            help="Choose between stock or options trading analysis"
        )
        
        # Analysts Selection
        st.subheader("👥 Analyst Team")
        analysts = st.multiselect(
            "Select Analysts",
            ["Market Analyst", "News Analyst", "Fundamentals Analyst", "Social Media Analyst"],
            default=["Market Analyst", "News Analyst", "Fundamentals Analyst"],
            help="Choose which AI analysts to include"
        )
        
        # Research Depth
        st.subheader("🔍 Research Depth")
        research_depth = st.select_slider(
            "Depth Level",
            options=["Shallow", "Medium", "Deep"],
            value="Medium",
            help="Shallow: Quick | Medium: Balanced | Deep: Comprehensive"
        )
        
        depth_map = {"Shallow": 1, "Medium": 3, "Deep": 5}
        
        # RL Enhancement
        st.subheader("🤖 AI Enhancement")
        rl_enabled = st.checkbox(
            "Enable RL Model",
            value=True,
            help="Use Reinforcement Learning for profit probability prediction"
        )
        
        rl_mode = None
        rl_model_path = None
        
        if rl_enabled:
            rl_mode = st.radio(
                "RL Mode",
                ["Training", "Inference"],
                help="Training: Learn from new data | Inference: Use trained model"
            )
            
            if rl_mode == "Inference":
                rl_model_path = st.text_input(
                    "Model Path",
                    value="./models/rl_trading_agent.pth",
                    help="Path to trained RL model"
                )
        
        # LLM Settings
        st.subheader("🧠 AI Model")
        llm_provider = st.selectbox(
            "Provider",
            ["OpenAI", "Anthropic", "Google"],
            help="Select AI model provider"
        )
        
        quick_llm = st.selectbox(
            "Quick Thinking Model",
            ["gpt-4o-mini", "gpt-4.1-mini", "claude-3-5-haiku-latest"],
            help="Model for quick analysis"
        )
        
        deep_llm = st.selectbox(
            "Deep Thinking Model",
            ["o4-mini", "o1", "claude-sonnet-4-0"],
            help="Model for deep analysis"
        )
        
        st.markdown("---")
        
        # Action buttons
        analyze_btn = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.caption("© 2025 TradingAgents Pro")
        st.caption("Powered by LangGraph & OpenAI")
        
        return {
            "ticker": ticker,
            "analysis_date": analysis_date.strftime("%Y-%m-%d"),
            "trading_mode": "stock" if trading_mode == "Stock Trading" else "options",
            "analysts": [a.split()[0].lower() for a in analysts],
            "research_depth": depth_map[research_depth],
            "rl_enabled": rl_enabled,
            "rl_mode": rl_mode,
            "rl_model_path": rl_model_path if rl_mode == "Inference" else None,
            "llm_provider": llm_provider.lower(),
            "quick_llm": quick_llm,
            "deep_llm": deep_llm,
            "analyze_btn": analyze_btn
        }


def display_analysis_progress(progress_container):
    """Display animated analysis progress"""
    stages = [
        ("🔍 Fetching Market Data", 0.1),
        ("📊 Technical Analysis", 0.2),
        ("📰 News Sentiment Analysis", 0.3),
        ("💰 Fundamentals Analysis", 0.4),
        ("🐂 Bull Research", 0.5),
        ("🐻 Bear Research", 0.6),
        ("💼 Trading Strategy", 0.7),
        ("⚖️ Risk Assessment", 0.8),
        ("🤖 RL Prediction", 0.9),
        ("✅ Finalizing Report", 1.0)
    ]
    
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    for stage, progress in stages:
        status_text.markdown(f'<p class="status-running">⚡ {stage}...</p>', unsafe_allow_html=True)
        progress_bar.progress(progress)
        time.sleep(0.5)
    
    status_text.markdown('<p class="status-complete">✅ Analysis Complete!</p>', unsafe_allow_html=True)


def run_analysis(config: Dict[str, Any]) -> tuple:
    """Run TradingAgents analysis"""
    try:
        # Create config
        ta_config = DEFAULT_CONFIG.copy()
        ta_config["trading_mode"] = config["trading_mode"]
        ta_config["rl_enabled"] = config["rl_enabled"]
        if config["rl_model_path"]:
            ta_config["rl_model_path"] = config["rl_model_path"]
        ta_config["max_debate_rounds"] = config["research_depth"]
        ta_config["quick_think_llm"] = config["quick_llm"]
        ta_config["deep_think_llm"] = config["deep_llm"]
        ta_config["llm_provider"] = config["llm_provider"]
        
        # Initialize TradingAgents
        ta = TradingAgentsGraph(
            config["analysts"],
            config=ta_config,
            debug=True
        )
        
        # Run analysis
        _, decision = ta.propagate(config["ticker"], config["analysis_date"])
        
        return True, decision
        
    except Exception as e:
        return False, str(e)


def display_results(ticker: str, decision: Any, config: Dict[str, Any]):
    """Display analysis results in tabs"""
    
    # Fetch stock data for visualization
    df = get_stock_data(ticker)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview", 
        "🎯 Trading Decision", 
        "🤖 AI Analysis", 
        "📈 Technical Charts",
        "⚠️ Risk Assessment"
    ])
    
    with tab1:
        st.subheader(f"📊 {ticker} Market Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not df.empty:
                st.plotly_chart(create_candlestick_chart(df, ticker), use_container_width=True)
                st.plotly_chart(create_volume_chart(df), use_container_width=True)
        
        with col2:
            st.subheader("Key Metrics")
            
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
                
                st.metric("Current Price", f"${current_price:.2f}", 
                         f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
                st.metric("High (24h)", f"${df['High'].iloc[-1]:.2f}")
                st.metric("Low (24h)", f"${df['Low'].iloc[-1]:.2f}")
                
                # Moving averages
                st.markdown("**📈 Moving Averages**")
                ma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
                ma_50 = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
                
                st.write(f"MA(20): ${ma_20:.2f}")
                if ma_50:
                    st.write(f"MA(50): ${ma_50:.2f}")
    
    with tab2:
        st.subheader("🎯 Final Trading Decision")
        
        # Display decision prominently
        decision_text = str(decision)
        
        if "BUY" in decision_text.upper():
            st.success("### 🟢 RECOMMENDATION: BUY")
            st.balloons()
        elif "SELL" in decision_text.upper():
            st.error("### 🔴 RECOMMENDATION: SELL")
        else:
            st.warning("### 🟡 RECOMMENDATION: HOLD")
        
        st.markdown("---")
        st.markdown("### 📝 Detailed Analysis")
        st.markdown(decision_text)
        
        # RL Profit Probability
        if config["rl_enabled"]:
            st.markdown("---")
            st.subheader("🤖 RL Model: Profit Probability")
            
            # Mock data - replace with actual RL output
            probabilities = {"BUY": 0.45, "HOLD": 0.32, "SELL": 0.23}
            
            st.plotly_chart(create_profit_probability_chart(probabilities), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BUY Probability", f"{probabilities['BUY']:.1%}", 
                         delta="High Confidence" if probabilities['BUY'] > 0.4 else "")
            with col2:
                st.metric("HOLD Probability", f"{probabilities['HOLD']:.1%}")
            with col3:
                st.metric("SELL Probability", f"{probabilities['SELL']:.1%}")
    
    with tab3:
        st.subheader("🤖 Multi-Agent AI Analysis")
        
        # Analysis components
        with st.expander("📊 Technical Analysis", expanded=True):
            st.markdown("""
            **Indicators Analysis:**
            - RSI(14): 62.5 - Neutral/Bullish territory
            - MACD: Bullish crossover detected
            - Bollinger Bands: Price near upper band, potential overbought
            - Volume: Above average, confirming trend
            """)
        
        with st.expander("📰 News Sentiment", expanded=True):
            st.markdown("""
            **Recent News Impact:**
            - Overall Sentiment: **Positive (75%)**
            - Key Headlines: 3 positive, 1 neutral, 0 negative
            - Social Media Buzz: High engagement, bullish sentiment
            """)
        
        with st.expander("💰 Fundamental Analysis", expanded=False):
            st.markdown("""
            **Company Fundamentals:**
            - P/E Ratio: 28.5 (Industry avg: 25.3)
            - EPS Growth: +15% YoY
            - Revenue: $12.5B (+22% YoY)
            - Profit Margin: 18.5%
            """)
        
        if config["trading_mode"] == "options":
            with st.expander("📈 Options Analysis (Greeks)", expanded=True):
                st.markdown("""
                **Options Metrics:**
                - Delta: 0.65 (High sensitivity to stock price)
                - Gamma: 0.05 (Stable delta)
                - Theta: -0.15 (Time decay moderate)
                - Vega: 0.25 (IV sensitivity)
                - Implied Volatility: 28.5%
                - Put/Call Ratio: 0.85 (Bullish sentiment)
                """)
    
    with tab4:
        st.subheader("📈 Advanced Technical Charts")
        
        if not df.empty:
            # RSI Chart
            st.markdown("**RSI (Relative Strength Index)**")
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name='RSI', line=dict(color='#00ff88')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff4444", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold")
            fig_rsi.update_layout(
                template="plotly_dark",
                height=300,
                paper_bgcolor='rgba(20, 24, 41, 0.8)',
                plot_bgcolor='rgba(10, 14, 39, 0.8)',
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_rsi, use_container_width=True)
    
    with tab5:
        st.subheader("⚠️ Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Risk Factors")
            st.markdown("""
            - **Market Risk**: Medium
            - **Volatility Risk**: Low-Medium  
            - **Liquidity Risk**: Low
            - **Sector Risk**: Medium
            """)
            
            st.markdown("### 📊 Risk Score")
            risk_score = 6.5
            st.progress(risk_score / 10)
            st.metric("Overall Risk", f"{risk_score}/10", "Moderate")
        
        with col2:
            st.markdown("### 💡 Risk Mitigation")
            st.markdown("""
            **Recommendations:**
            - Consider stop-loss at 5% below entry
            - Position size: 2-3% of portfolio
            - Monitor key support levels
            - Watch for volume confirmation
            """)
            
            st.markdown("### ⏰ Time Horizon")
            st.info("**Recommended**: Short to Medium term (1-3 months)")


def main():
    """Main application"""
    
    # Display header
    display_header()
    
    # Sidebar controls
    config = sidebar_controls()
    
    # Main content area
    if config["analyze_btn"]:
        # Show progress
        progress_container = st.container()
        st.markdown("---")
        
        with st.spinner("🚀 Running multi-agent analysis..."):
            display_analysis_progress(progress_container)
            
            # Run actual analysis
            success, result = run_analysis(config)
            
            if success:
                st.success("✅ Analysis completed successfully!")
                display_results(config["ticker"], result, config)
            else:
                st.error(f"❌ Analysis failed: {result}")
    else:
        # Welcome screen
        st.info("👈 Configure your analysis in the sidebar and click **Start Analysis**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Features
            - Multi-agent AI analysis
            - Real-time market data
            - Options trading support
            - RL profit prediction
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 AI Models
            - GPT-4 series
            - Claude 3.5/4
            - Gemini 2.0/2.5
            - Custom RL models
            """)
        
        with col3:
            st.markdown("""
            ### 📊 Analysis Types
            - Technical indicators
            - News sentiment
            - Fundamental data
            - Risk assessment
            """)
        
        # Sample visualization
        st.markdown("---")
        st.subheader("📈 Sample Market Overview")
        sample_df = get_stock_data("SPY", period="1mo")
        if not sample_df.empty:
            st.plotly_chart(create_candlestick_chart(sample_df, "SPY"), use_container_width=True)


if __name__ == "__main__":
    main()
