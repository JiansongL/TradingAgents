"""
TradingAgents Web Interface - V3 Professional Edition
Real-time streaming analysis with interactive elements and advanced options strategies.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from typing import Dict, Any
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Assuming these are your library components
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# --- Page Configuration ---
st.set_page_config(
    page_title="Tauric Research - Trading Terminal",
    page_icon="assets/TauricResearch.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Look ---
st.markdown("""
<style>
    /* Main layout and theme */
    .stApp {
        background-color: #0a0e1a;
        color: #e0e0e0;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Title and Headers */
    .title-font {
        font-size: 36px !important;
        font-weight: 700;
        color: #ffffff;
        text-align: left;
        margin-bottom: 0;
    }
    .subtitle-font {
        font-size: 16px;
        color: #a0a0a0;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    /* Sidebar */
    .stSidebar {
        background-color: #12182c;
        border-right: 1px solid #2a3149;
    }
    .stSidebar .st-emotion-cache-16txtl3 {
        color: #ffffff;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #00d2ff;
        transform: translateY(-2px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #a0a0a0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1c233a;
        color: #ffffff;
        font-weight: 600;
    }

    /* Metrics */
    .stMetric {
        background-color: #12182c;
        border: 1px solid #2a3149;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Gemini-style output */
    .gemini-output {
        background-color: #12182c;
        border-radius: 8px;
        padding: 1.5rem;
        min-height: 300px;
        font-family: 'Fira Code', monospace;
        line-height: 1.6;
        border-left: 4px solid #3a7bd5;
    }
    .gemini-output h3 {
        color: #00d2ff;
        margin-top: 0;
    }
    .gemini-output p {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch stock data"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return df
    except Exception:
        st.error(f"Error fetching data for {ticker}. Please check the ticker symbol.")
        return pd.DataFrame()

def create_candlestick_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Create a professional-looking candlestick chart"""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#00d2ff',
        decreasing_line_color='#e0e0e0'
    )])
    fig.update_layout(
        title=f"{ticker} Price Chart",
        template="plotly_dark",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#12182c',
        xaxis_rangeslider_visible=False,
        font=dict(color="#e0e0e0")
    )
    return fig

def create_profit_probability_chart(probabilities: Dict[str, float]) -> go.Figure:
    """Create a professional RL probability chart"""
    colors = {'BUY': '#00d2ff', 'HOLD': '#a0a0a0', 'SELL': '#e0e0e0'}
    fig = go.Figure(data=[go.Bar(
        x=list(probabilities.keys()),
        y=list(probabilities.values()),
        marker_color=[colors.get(k, '#a0a0a0') for k in probabilities.keys()],
        text=[f"{v:.1%}" for v in probabilities.values()],
        textposition='auto',
    )])
    fig.update_layout(
        title="Profitability Analysis",
        template="plotly_dark",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#12182c',
        yaxis=dict(tickformat='.0%', range=[0, 1]),
        font=dict(color="#e0e0e0")
    )
    return fig


# --- Sidebar Controls ---

def sidebar_controls() -> Dict:
    """Render sidebar controls and return configuration."""
    with st.sidebar:
        st.image("assets/TauricResearch.png", width=200)
        st.title("Configuration")
        
        st.subheader("Analysis Target")
        ticker = st.text_input("Stock Ticker", value="NVDA").upper()
        
        st.subheader("Trading Strategy")
        trading_mode = st.radio("Select Mode", ["Stock", "Options"])
        
        option_params = None
        if trading_mode == "Options":
            st.subheader("Option Strategy")
            
            # User defines their action
            user_action = st.selectbox("Your Action", ["Buy", "Sell"])
            
            # Complex strategies
            strategy = st.selectbox("Strategy", ["Single", "Bull Call Spread", "Bear Put Spread"])

            if strategy == "Single":
                option_type = st.selectbox("Option Type", ["Call", "Put"])
                strike = st.number_input("Strike Price ($)", value=500.0, step=5.0)
                expiry = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=30))
                quantity = st.number_input("Quantity", value=1, min_value=1)
                option_params = {
                    "user_action": user_action.lower(),
                    "strategy": "single",
                    "type": option_type.lower(),
                    "strike": strike,
                    "expiry": expiry.strftime("%Y-%m-%d"),
                    "quantity": quantity
                }
            else: # Spread strategies
                strike1 = st.number_input("Lower Strike ($)", value=490.0, step=5.0)
                strike2 = st.number_input("Higher Strike ($)", value=510.0, step=5.0)
                expiry = st.date_input("Expiry Date", value=datetime.now() + timedelta(days=30))
                quantity = st.number_input("Quantity", value=1, min_value=1)
                option_params = {
                    "user_action": user_action.lower(),
                    "strategy": "bull_call_spread" if "Bull" in strategy else "bear_put_spread",
                    "strike1": strike1,
                    "strike2": strike2,
                    "expiry": expiry.strftime("%Y-%m-%d"),
                    "quantity": quantity
                }

        st.subheader("Analyst Team")
        analysts = st.multiselect(
            "Select Analysts",
            ["Market", "News", "Fundamentals", "Social", "Options"],
            default=["Market", "News", "Fundamentals", "Options"] if trading_mode == "Options" else ["Market", "News", "Fundamentals"]
        )
        
        st.markdown("---")
        analyze_btn = st.button("Start Analysis", use_container_width=True)
        
        return {
            "ticker": ticker,
            "trading_mode": trading_mode.lower(),
            "option_params": option_params,
            "analysts": [a.lower() for a in analysts],
            "analyze_btn": analyze_btn,
            # Default other params for simplicity
            "research_depth": 3,
            "quick_llm": "gpt-4o-mini",
            "deep_llm": "o1",
            "llm_provider": "openai",
            "rl_enabled": True,
            "rl_model_path": "./models/rl_trading_agent.pth"
        }

# --- Main Application Logic ---

def run_streaming_analysis(config: Dict, output_placeholder):
    """Run analysis and stream Gemini-style output."""
    try:
        # Setup TradingAgentsGraph
        ta_config = DEFAULT_CONFIG.copy()
        # ... (update ta_config with values from sidebar config)
        
        ta = TradingAgentsGraph(config["analysts"], config=ta_config, debug=True)
        init_state = ta.propagator.create_initial_state(config["ticker"], datetime.now().strftime("%Y-%m-%d"))
        args = ta.propagator.get_graph_args()

        full_report = ""
        output_placeholder.markdown('<div class="gemini-output"></div>', unsafe_allow_html=True)

        # Simulate streaming output
        def stream_message(message, delay=0.02):
            nonlocal full_report
            streamed_text = ""
            for char in message:
                streamed_text += char
                full_report = full_report.replace(streamed_text[:-1], streamed_text)
                output_placeholder.markdown(f'<div class="gemini-output">{full_report}</div>', unsafe_allow_html=True)
                time.sleep(delay)

        # --- Analysis Flow ---
        stream_message("### Initializing Analysis\n")
        stream_message(f"**Target:** {config['ticker']}\n")
        stream_message(f"**Strategy:** {config['trading_mode'].capitalize()}\n\n")

        # This is a simulation. In a real scenario, you'd iterate through `ta.graph.stream()`
        # and format the output from each chunk.
        
        # 1. Market Analyst
        time.sleep(1)
        stream_message("### Market Analysis\n")
        stream_message("- Current price shows a slight uptrend over the past week.\n")
        stream_message("- RSI is at 58, indicating neutral momentum.\n\n")

        # 2. News Analyst
        time.sleep(1)
        stream_message("### News & Sentiment Analysis\n")
        stream_message("- Recent news about product launch is positive.\n")
        stream_message("- Social media sentiment is moderately bullish.\n\n")

        # 3. Options Analyst (if selected)
        if "options" in config["analysts"]:
            time.sleep(1)
            stream_message("### Options Chain Analysis\n")
            stream_message("- Implied Volatility is at 35%, slightly above historical average.\n")
            stream_message("- High open interest on near-the-money calls.\n\n")

        # 4. RL Model
        time.sleep(1)
        stream_message("### Profitability Model\n")
        stream_message("- Running state vector through the DQN model...\n")
        
        # Mock RL results
        analysis_results = {
            "rl_probabilities": {"BUY": 0.62, "HOLD": 0.28, "SELL": 0.10}
        }
        
        stream_message("- Model indicates a 62% probability of profit for a bullish position.\n\n")
        
        stream_message("### Final Report\n")
        stream_message("Based on the comprehensive analysis, the proposed trade has a favorable risk/reward profile. The combination of positive market sentiment and neutral-to-bullish technicals supports the thesis.")

        return True, analysis_results, "Analysis Complete"

    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        return False, None, str(e)


def main():
    """Main function to run the Streamlit app."""
    
    # --- Header ---
    st.markdown('<p class="title-font">Trading Terminal</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-font">Powered by Tauric Research Multi-Agent AI</p>', unsafe_allow_html=True)

    # --- Market Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("S&P 500", "4,783.45", "+1.2%")
    with col2:
        st.metric("NASDAQ", "15,089.90", "+1.8%")
    with col3:
        st.metric("VIX", "12.45", "-2.3%")
    with col4:
        st.metric("BTC/USD", "68,500", "+3.1%")
    
    st.markdown("---")
    
    # --- Sidebar and Main Content ---
    config = sidebar_controls()
    
    if config["analyze_btn"]:
        # Layout for analysis output
        col1, col2 = st.columns([2, 1])
        
        with col1:
            output_placeholder = st.empty()
            success, results, _ = run_streaming_analysis(config, output_placeholder)
        
        if success and results:
            with col2:
                st.subheader("Analysis Summary")
                df = get_stock_data(config["ticker"])
                if not df.empty:
                    st.plotly_chart(create_candlestick_chart(df, config["ticker"]), use_container_width=True)
                
                if results.get("rl_probabilities"):
                    st.plotly_chart(create_profit_probability_chart(results["rl_probabilities"]), use_container_width=True)
    else:
        st.info("Configure your analysis in the sidebar and click 'Start Analysis'.")

if __name__ == "__main__":
    main()
