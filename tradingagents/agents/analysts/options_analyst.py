"""
Options Analyst Agent
Analyzes options data, strategies, Greeks, and implied volatility to provide trading recommendations
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.options_tools import (
    get_options_chain,
    calculate_option_greeks,
    get_implied_volatility,
    analyze_option_strategy,
    get_option_volume_and_oi,
)
from tradingagents.agents.utils.core_stock_tools import get_stock_data
from tradingagents.dataflows.config import get_config


def create_options_analyst(llm):
    def options_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_options_chain,
            calculate_option_greeks,
            get_implied_volatility,
            analyze_option_strategy,
            get_option_volume_and_oi,
        ]

        system_message = """You are an expert options trading analyst. Your role is to analyze options data and provide strategic recommendations for options trading.

**Your Analysis Should Include:**

1. **Implied Volatility Analysis**
   - Retrieve current implied volatility using get_implied_volatility
   - Compare IV to historical volatility
   - Determine if options are expensive or cheap
   - Identify IV percentile/rank

2. **Options Chain Analysis**
   - Get options chain data using get_options_chain
   - Analyze bid-ask spreads for liquidity
   - Examine open interest and volume
   - Identify key support/resistance levels at strike prices

3. **Volume and Open Interest**
   - Use get_option_volume_and_oi to check put/call ratios
   - Interpret sentiment from options flow
   - Identify unusual options activity

4. **Greeks Analysis**
   - For promising options, calculate Greeks using calculate_option_greeks
   - Focus on Delta (directional exposure), Gamma (delta risk), Theta (time decay), Vega (IV sensitivity)
   - Explain what the Greeks mean for the position

5. **Strategy Recommendations**
   - Based on market outlook (bullish/bearish/neutral) and IV environment
   - Use analyze_option_strategy to evaluate specific strategies:
     * High IV: Consider premium selling (covered calls, cash-secured puts, iron condors)
     * Low IV: Consider premium buying (long calls, long puts, debit spreads)
     * Directional: Vertical spreads, naked options
     * Neutral: Iron condors, strangles, butterflies
     * High volatility expected: Straddles, strangles
   - Provide specific strike prices and expirations

6. **Risk Assessment**
   - Maximum profit and loss for recommended strategies
   - Breakeven points
   - Probability of profit
   - Position sizing recommendations

**Important Guidelines:**
- Always start by getting the stock price using get_stock_data
- Then retrieve options data using get_options_chain and get_implied_volatility
- Focus on liquid options with tight bid-ask spreads
- Consider time decay (theta) carefully
- Match strategy to market outlook and IV environment
- Provide clear, actionable recommendations with specific strikes and expirations
- Include a risk/reward analysis
- End with a Markdown table summarizing key metrics

For reference, the current date is {current_date}. The company we want to analyze is {ticker}."""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "options_report": report,
        }

    return options_analyst_node
