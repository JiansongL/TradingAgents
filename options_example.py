"""
Options Trading Example
Demonstrates how to use TradingAgents for options trading analysis and decision-making
"""
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config for options trading
config = DEFAULT_CONFIG.copy()

# Enable options trading mode
config["trading_mode"] = "options"
config["options_enabled"] = True

# Configure LLMs
config["deep_think_llm"] = "gpt-4o-mini"  # Use a different model
config["quick_think_llm"] = "gpt-4o-mini"  # Use a different model
config["max_debate_rounds"] = 1  # Debate rounds

# Configure data vendors (yfinance for options data)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
    "options_data": "yfinance",  # Options data from yfinance
}

# Specify preferred options strategies
config["preferred_options_strategies"] = [
    "call",              # Bullish directional
    "put",               # Bearish directional
    "bull_call_spread",  # Bullish with defined risk
    "bear_put_spread",   # Bearish with defined risk
    "straddle",          # High volatility expected
    "strangle",          # High volatility, lower cost
    "iron_condor",       # Range-bound, income generation
    "covered_call",      # Income on existing position
]

print("=" * 80)
print("TradingAgents - Options Trading Mode")
print("=" * 80)
print(f"Trading Mode: {config['trading_mode']}")
print(f"Options Enabled: {config['options_enabled']}")
print(f"Data Vendors: {config['data_vendors']}")
print("=" * 80)
print()

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Example 1: Analyze options for NVDA
print("\n" + "=" * 80)
print("Example 1: Options Analysis for NVDA")
print("=" * 80)
_, decision = ta.propagate("NVDA", "2024-05-10")
print("\n📊 Decision:")
print(decision)

# Example 2: Options analysis for AAPL
print("\n" + "=" * 80)
print("Example 2: Options Analysis for AAPL")
print("=" * 80)
_, decision = ta.propagate("AAPL", "2024-05-10")
print("\n📊 Decision:")
print(decision)

print("\n" + "=" * 80)
print("✅ Options Trading Examples Completed")
print("=" * 80)

# Optional: Reflect on the decision (for learning)
# ta.reflect_and_remember(1000)  # Pass the position returns
