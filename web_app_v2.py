"""
TradingAgents Web Interface - Enhanced Version
Real-time streaming analysis with RL integration
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import yfinance as yf
from typing import Optional, Dict, Any
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
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

# Custom CSS (same as before)
st.markdown("""
<style>
    .big-font {
        font-size: 48px !important;
        font-weight: 700;
        background: linear-gradient(90deg, #00ff88, #0066ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00ff88, #0066ff);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
    }
    .status-running { color: #ffaa00; animation: pulse 2s infinite; }
    .status-complete { color: #00ff88; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_state' not in st.session_state:
    st.session_state.analysis_state = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'progress_status' not in st.session_state:
    st.session_state.progress_status = {}


def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch stock data"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def create_candlestick_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Create candlestick chart"""
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
        template="plotly_dark",
        height=400,
        paper_bgcolor='rgba(20, 24, 41, 0.8)',
        xaxis_rangeslider_visible=False
    )
    
    return fig


def create_profit_probability_chart(probabilities: Dict[str, float]) -> go.Figure:
    """Create RL probability chart"""
    fig = go.Figure(data=[go.Bar(
        x=list(probabilities.keys()),
        y=list(probabilities.values()),
        marker=dict(color=['#00ff88', '#ffaa00', '#ff4444']),
        text=[f"{v:.1%}" for v in probabilities.values()],
        textposition='auto',
    )])
    
    fig.update_layout(
        title="RL Model: Profit Probability",
        template="plotly_dark",
        height=300,
        paper_bgcolor='rgba(20, 24, 41, 0.8)',
        yaxis=dict(tickformat='.0%', range=[0, 1])
    )
    
    return fig


def sidebar_controls():
    """Sidebar configuration"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Basic settings
        st.subheader("🎯 Analysis Settings")
        ticker = st.text_input("Stock Ticker", value="NVDA").upper()
        analysis_date = st.date_input("Analysis Date", value=datetime.now())
        
        # Trading mode
        st.subheader("💼 Trading Mode")
        trading_mode = st.radio("Select Mode", ["Stock Trading", "Options Trading"])
        
        # Options parameters (only show if Options Trading)
        option_params = None
        if trading_mode == "Options Trading":
            st.subheader("📊 Option Parameters")
            option_type = st.selectbox("Option Type", ["CALL", "PUT"])
            strike_price = st.number_input("Strike Price ($)", value=500.0, step=5.0)
            expiry_date = st.date_input("Expiry Date", value=datetime.now())
            quantity = st.number_input("Quantity", value=1, min_value=1)
            
            option_params = {
                "type": option_type,
                "strike": strike_price,
                "expiry": expiry_date.strftime("%Y-%m-%d"),
                "quantity": quantity
            }
        
        # Analysts
        st.subheader("👥 Analyst Team")
        analysts = st.multiselect(
            "Select Analysts",
            ["Market", "News", "Fundamentals", "Social"],
            default=["Market", "News", "Fundamentals"]
        )
        
        # Research depth
        st.subheader("🔍 Research Depth")
        depth = st.select_slider("Depth", ["Shallow", "Medium", "Deep"], value="Medium")
        depth_map = {"Shallow": 1, "Medium": 3, "Deep": 5}
        
        # RL settings
        st.subheader("🤖 AI Enhancement")
        rl_enabled = st.checkbox("Enable RL Model", value=True)
        rl_mode = None
        rl_model_path = None
        
        if rl_enabled:
            rl_mode = st.radio("RL Mode", ["Training", "Inference"])
            if rl_mode == "Inference":
                rl_model_path = st.text_input("Model Path", value="./models/rl_trading_agent.pth")
        
        # LLM settings
        st.subheader("🧠 AI Model")
        llm_provider = st.selectbox("Provider", ["OpenAI", "Anthropic", "Google"])
        quick_llm = st.selectbox("Quick Model", ["gpt-4o-mini", "gpt-4.1-mini"])
        deep_llm = st.selectbox("Deep Model", ["o4-mini", "o1"])
        
        st.markdown("---")
        analyze_btn = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
        
        return {
            "ticker": ticker,
            "analysis_date": analysis_date.strftime("%Y-%m-%d"),
            "trading_mode": "stock" if trading_mode == "Stock Trading" else "options",
            "option_params": option_params,
            "analysts": [a.lower() for a in analysts],
            "research_depth": depth_map[depth],
            "rl_enabled": rl_enabled,
            "rl_mode": rl_mode,
            "rl_model_path": rl_model_path if rl_mode == "Inference" else None,
            "llm_provider": llm_provider.lower(),
            "quick_llm": quick_llm,
            "deep_llm": deep_llm,
            "analyze_btn": analyze_btn
        }


def run_streaming_analysis(config: Dict[str, Any], progress_placeholder, status_placeholder):
    """Run analysis with real-time streaming updates"""
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
        status_placeholder.markdown('⚡ Initializing AI agents...', unsafe_allow_html=True)
        progress_placeholder.progress(0.05)
        
        ta = TradingAgentsGraph(
            config["analysts"],
            config=ta_config,
            debug=True
        )
        
        # Create initial state
        status_placeholder.markdown('⚡ Creating analysis state...', unsafe_allow_html=True)
        progress_placeholder.progress(0.1)
        
        init_state = ta.propagator.create_initial_state(
            config["ticker"],
            config["analysis_date"]
        )
        
        # Get graph args
        args = ta.propagator.get_graph_args()
        
        # Stream the analysis
        progress = 0.1
        progress_step = 0.8 / 10  # Remaining progress divided by approximate steps
        
        analysis_results = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
            "rl_probabilities": None
        }
        
        for chunk in ta.graph.stream(init_state, **args):
            # Update progress
            progress = min(progress + progress_step, 0.9)
            progress_placeholder.progress(progress)
            
            # Parse chunk data
            if "market_report" in chunk and chunk["market_report"]:
                status_placeholder.markdown('📊 Market analysis complete...', unsafe_allow_html=True)
                analysis_results["market_report"] = chunk["market_report"]
                
            if "sentiment_report" in chunk and chunk["sentiment_report"]:
                status_placeholder.markdown('💬 Sentiment analysis complete...', unsafe_allow_html=True)
                analysis_results["sentiment_report"] = chunk["sentiment_report"]
                
            if "news_report" in chunk and chunk["news_report"]:
                status_placeholder.markdown('📰 News analysis complete...', unsafe_allow_html=True)
                analysis_results["news_report"] = chunk["news_report"]
                
            if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                status_placeholder.markdown('💰 Fundamentals analysis complete...', unsafe_allow_html=True)
                analysis_results["fundamentals_report"] = chunk["fundamentals_report"]
                
            if "investment_plan" in chunk and chunk["investment_plan"]:
                status_placeholder.markdown('🔬 Research team decision complete...', unsafe_allow_html=True)
                analysis_results["investment_plan"] = chunk["investment_plan"]
                
            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                status_placeholder.markdown('💼 Trading strategy complete...', unsafe_allow_html=True)
                analysis_results["trader_investment_plan"] = chunk["trader_investment_plan"]
                
            if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
                status_placeholder.markdown('⚖️ Risk assessment complete...', unsafe_allow_html=True)
                analysis_results["final_trade_decision"] = chunk["final_trade_decision"]
        
        # Get final decision
        status_placeholder.markdown('🤖 Generating RL prediction...', unsafe_allow_html=True)
        progress_placeholder.progress(0.95)
        
        final_state = list(ta.graph.stream(init_state, **args))[-1]
        decision = ta.process_signal(final_state.get("final_trade_decision", ""))
        
        # Real RL model prediction
        if config["rl_enabled"]:
            try:
                from tradingagents.rl.rl_agent import RLTradingAgent
                from tradingagents.rl.rl_state_encoder import StateEncoder
                
                # Encode state from analysis results
                encoder = StateEncoder(state_dim=128)
                state_data = {
                    "market_report": analysis_results.get("market_report", ""),
                    "news_report": analysis_results.get("news_report", ""),
                    "fundamentals_report": analysis_results.get("fundamentals_report", ""),
                    "sentiment_report": analysis_results.get("sentiment_report", ""),
                    "trading_mode": config.get("trading_mode", "stock"),
                }
                
                # Add option parameters if in options mode
                if config.get("option_params"):
                    state_data["options_report"] = f"Option Type: {config['option_params'].get('type', 'CALL')}, Strike: ${config['option_params'].get('strike', 0)}, Expiry: {config['option_params'].get('expiry', 'N/A')}"
                
                state_vector = encoder.encode(state_data)
                
                # Initialize RL agent
                rl_agent = RLTradingAgent(state_dim=128, action_dim=3)
                
                # Load model if path provided
                if config.get("rl_model_path") and os.path.exists(config["rl_model_path"]):
                    rl_agent.load_model(config["rl_model_path"])
                    status_placeholder.markdown('🧠 Using trained RL model...', unsafe_allow_html=True)
                else:
                    status_placeholder.markdown('🧠 Using untrained RL model (random predictions)...', unsafe_allow_html=True)
                
                # Get probabilities
                probabilities = rl_agent.get_all_action_probabilities(state_vector)
                analysis_results["rl_probabilities"] = probabilities
                
            except Exception as e:
                st.warning(f"⚠️ RL Model error: {e}. Using default probabilities.")
                analysis_results["rl_probabilities"] = {
                    "BUY": 0.33,
                    "HOLD": 0.34,
                    "SELL": 0.33
                }
        
        status_placeholder.markdown('✅ Analysis Complete!', unsafe_allow_html=True)
        progress_placeholder.progress(1.0)
        
        return True, analysis_results, decision
        
    except Exception as e:
        status_placeholder.markdown(f'❌ Error: {str(e)}', unsafe_allow_html=True)
        return False, None, str(e)


def main():
    # Header
    st.markdown('<p class="big-font">📈 TradingAgents Pro</p>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent AI Financial Analysis Platform")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Market", "🟢 OPEN", "NYSE")
    with col2:
        st.metric("S&P 500", "4,783.45", "+1.2%")
    with col3:
        st.metric("NASDAQ", "15,089.90", "+1.8%")
    with col4:
        st.metric("VIX", "12.45", "-2.3%")
    
    st.markdown("---")
    
    # Sidebar controls
    config = sidebar_controls()
    
    # Main content
    if config["analyze_btn"]:
        # Create placeholders for real-time updates
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        st.markdown("---")
        
        # Run analysis with streaming
        success, results, decision = run_streaming_analysis(config, progress_placeholder, status_placeholder)
        
        if success and results:
            st.session_state.analysis_result = results
            st.session_state.config = config
            
            # Show results
            st.success("✅ Analysis completed successfully!")
            display_results(config, results, decision)
    
    elif st.session_state.analysis_result:
        # Display previous results
        display_results(st.session_state.config, st.session_state.analysis_result, None)
    
    else:
        # Welcome screen
        st.info("👈 Configure your analysis in the sidebar and click **Start Analysis**")


def display_results(config, results, decision):
    """Display analysis results in tabs"""
    
    ticker = config["ticker"]
    df = get_stock_data(ticker)
    
    # Create tabs
    tabs = st.tabs([
        "📊 Market", 
        "🎯 Decision", 
        "🤖 AI Analysis",
        "🧠 RL Model",  # New tab for RL
        "📈 Charts"
    ])
    
    with tabs[0]:
        # Market Overview
        st.subheader(f"📊 {ticker} Market Overview")
        if not df.empty:
            st.plotly_chart(create_candlestick_chart(df, ticker), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current", f"${df['Close'].iloc[-1]:.2f}")
            with col2:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
            with col3:
                change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                st.metric("Change", f"{change:+.2f}%")
    
    with tabs[1]:
        # Trading Decision
        st.subheader("🎯 Final Trading Decision")
        
        if decision:
            decision_str = str(decision).upper()
            if "BUY" in decision_str:
                st.success("### 🟢 RECOMMENDATION: BUY")
                st.balloons()
            elif "SELL" in decision_str:
                st.error("### 🔴 RECOMMENDATION: SELL")
            else:
                st.warning("### 🟡 RECOMMENDATION: HOLD")
            
            st.markdown("### 📝 Analysis Summary")
            st.markdown(str(decision))
        else:
            st.info("Waiting for analysis to complete...")
    
    with tabs[2]:
        # AI Analysis
        st.subheader("🤖 Multi-Agent AI Analysis")
        
        if results.get("market_report"):
            with st.expander("📊 Market Analysis", expanded=True):
                st.markdown(results["market_report"])
        
        if results.get("news_report"):
            with st.expander("📰 News Analysis", expanded=True):
                st.markdown(results["news_report"])
        
        if results.get("fundamentals_report"):
            with st.expander("💰 Fundamentals", expanded=False):
                st.markdown(results["fundamentals_report"])
        
        if results.get("sentiment_report"):
            with st.expander("💬 Social Sentiment", expanded=False):
                st.markdown(results["sentiment_report"])
    
    with tabs[3]:
        # RL Model Tab
        st.subheader("🧠 Reinforcement Learning Model")
        
        if results.get("rl_probabilities"):
            probs = results["rl_probabilities"]
            
            # Show probability chart
            st.plotly_chart(create_profit_probability_chart(probs), use_container_width=True)
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BUY Probability", f"{probs['BUY']:.1%}", 
                         "High" if probs['BUY'] > 0.4 else "")
            with col2:
                st.metric("HOLD Probability", f"{probs['HOLD']:.1%}")
            with col3:
                st.metric("SELL Probability", f"{probs['SELL']:.1%}")
            
            # Show option parameters if applicable
            if config.get("option_params"):
                st.markdown("### 📊 Option Trade Parameters")
                params = config["option_params"]
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Type**: {params['type']}")
                    st.info(f"**Strike**: ${params['strike']:.2f}")
                with col2:
                    st.info(f"**Expiry**: {params['expiry']}")
                    st.info(f"**Quantity**: {params['quantity']}")
                
                # Calculate expected profit/loss
                max_profit = recommended_action = None
                if probs['BUY'] > max(probs['HOLD'], probs['SELL']):
                    recommended_action = "BUY"
                elif probs['SELL'] > probs['HOLD']:
                    recommended_action = "SELL"
                else:
                    recommended_action = "HOLD"
                
                st.success(f"### Recommended Action: {recommended_action}")
                st.info(f"Confidence: {max(probs.values()):.1%}")
        else:
            st.info("RL model not enabled for this analysis")
    
    with tabs[4]:
        # Technical Charts
        st.subheader("📈 Technical Analysis Charts")
        if not df.empty:
            # RSI
            st.markdown("**RSI (14)**")
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', 
                                        name='RSI', line=dict(color='#00ff88')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff4444")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00ff88")
            fig_rsi.update_layout(
                template="plotly_dark",
                height=300,
                paper_bgcolor='rgba(20, 24, 41, 0.8)',
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_rsi, use_container_width=True)


if __name__ == "__main__":
    main()
