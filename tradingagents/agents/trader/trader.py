import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        
        # Check if we're in options trading mode
        trading_mode = state.get("trading_mode", "stock")
        options_report = state.get("options_report", "")

        # Build situation context
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        if trading_mode == "options" and options_report:
            curr_situation += f"\n\n{options_report}"
        
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # Build system message based on trading mode
        if trading_mode == "options":
            system_content = f"""You are an expert options trading agent analyzing market data to make options trading decisions. Based on your analysis, provide a specific recommendation for options strategies.

Your decision should include:
1. **Options Strategy**: Specify the strategy (e.g., 'CALL', 'PUT', 'BULL_CALL_SPREAD', 'IRON_CONDOR', 'STRADDLE', etc.)
2. **Direction**: BUY or SELL
3. **Strike Price(s)**: Specific strike price(s) for the option(s)
4. **Expiration Date**: When the option(s) expire
5. **Reasoning**: Clear rationale based on IV, Greeks, and market outlook
6. **Risk/Reward**: Maximum profit, maximum loss, and breakeven points

Always conclude your response with:
'FINAL TRANSACTION PROPOSAL: **BUY/SELL [STRATEGY] [STRIKE] [EXPIRATION]**'

Examples:
- 'FINAL TRANSACTION PROPOSAL: **BUY CALL $150 2024-06-21**'
- 'FINAL TRANSACTION PROPOSAL: **SELL IRON_CONDOR $145/$150/$160/$165 2024-06-21**'
- 'FINAL TRANSACTION PROPOSAL: **BUY STRADDLE $155 2024-07-19**'

Do not forget to utilize lessons from past decisions. Here are reflections from similar situations: {past_memory_str}"""
        else:
            system_content = f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situations you traded in and the lessons learned: {past_memory_str}"""

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": system_content,
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
