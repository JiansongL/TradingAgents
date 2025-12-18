# TradingAgents - Options Trading Extension

## 🎯 Overview

TradingAgents now supports **Options Trading**! The system can analyze options chains, calculate Greeks, evaluate implied volatility, and recommend various options strategies.

## ✨ New Features

### Options Analyst Agent
A specialized AI agent that:
- Analyzes options chain data
- Calculates option Greeks (Delta, Gamma, Theta, Vega, Rho)
- Evaluates implied volatility (IV)
- Analyzes options volume and open interest
- Recommends options strategies

### Options Data Tools
New data tools include:
- `get_options_chain`: Retrieve options chain data
- `calculate_option_greeks`: Calculate Greeks
- `get_implied_volatility`: Get implied volatility
- `analyze_option_strategy`: Analyze options strategies
- `get_option_volume_and_oi`: Get volume and open interest

### Supported Options Strategies
- **Directional**: `call`, `put`
- **Spreads**: `bull_call_spread`, `bear_put_spread`
- **Volatility**: `straddle`, `strangle`
- **Income**: `covered_call`, `iron_condor`

## 🚀 Quick Start

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create config for options trading
config = DEFAULT_CONFIG.copy()
config["trading_mode"] = "options"
config["options_enabled"] = True
config["data_vendors"]["options_data"] = "yfinance"

# Initialize
ta = TradingAgentsGraph(debug=True, config=config)

# Analyze options
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

### Run Example

```bash
python options_example.py
```

## 📊 Options Analysis Workflow

When options mode is enabled:

1. **Base Analysis**: Technical, fundamental, news, and sentiment
2. **Options-Specific Analysis**:
   - Options chain scanning
   - Implied volatility analysis
   - Volume and open interest analysis
   - Put/call ratios
3. **Greeks Calculation**: Delta, Gamma, Theta, Vega, Rho
4. **Strategy Recommendation**: Based on market conditions and IV
5. **Risk Management**: Options-specific risk assessment

## 📈 Decision Format

```
FINAL TRANSACTION PROPOSAL: **BUY/SELL [STRATEGY] [STRIKE] [EXPIRATION]**
```

Examples:
- `FINAL TRANSACTION PROPOSAL: **BUY CALL $150 2024-06-21**`
- `FINAL TRANSACTION PROPOSAL: **SELL IRON_CONDOR $145/$150/$160/$165 2024-06-21**`

## 📚 Documentation

For detailed documentation in Chinese, see [OPTIONS_README_CN.md](OPTIONS_README_CN.md)

## ⚠️ Disclaimer

Options trading carries significant risk. This tool is for research and educational purposes only. Not financial advice.

---

For full documentation and examples, see the complete README files.
