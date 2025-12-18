"""
Options-specific trading tools for retrieving options chain data,
calculating Greeks, implied volatility, and analyzing options strategies.
"""
from langchain_core.tools import tool
from typing import Annotated, Optional
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_options_chain(
    symbol: Annotated[str, "ticker symbol of the company"],
    date: Annotated[str, "Date to retrieve options chain for in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve options chain data for a given ticker symbol on a specific date.
    Returns information about available call and put options including strike prices,
    bid/ask prices, volume, open interest, and implied volatility.
    
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, NVDA
        date (str): Date in yyyy-mm-dd format
    
    Returns:
        str: A formatted string containing the options chain data including calls and puts
    """
    return route_to_vendor("get_options_chain", symbol, date)


@tool
def calculate_option_greeks(
    symbol: Annotated[str, "ticker symbol of the company"],
    strike_price: Annotated[float, "strike price of the option"],
    expiration_date: Annotated[str, "expiration date in yyyy-mm-dd format"],
    option_type: Annotated[str, "option type: 'call' or 'put'"],
    current_date: Annotated[str, "current date in yyyy-mm-dd format"],
) -> str:
    """
    Calculate the Greeks (Delta, Gamma, Theta, Vega, Rho) for a specific option.
    Greeks measure the sensitivity of an option's price to various factors.
    
    - Delta: Rate of change of option price with respect to underlying price
    - Gamma: Rate of change of delta with respect to underlying price
    - Theta: Rate of option value decay over time (time decay)
    - Vega: Sensitivity to changes in implied volatility
    - Rho: Sensitivity to changes in interest rates
    
    Args:
        symbol (str): Ticker symbol
        strike_price (float): Strike price of the option
        expiration_date (str): Expiration date in yyyy-mm-dd format
        option_type (str): 'call' or 'put'
        current_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted string containing all Greeks values
    """
    return route_to_vendor(
        "calculate_option_greeks",
        symbol,
        strike_price,
        expiration_date,
        option_type,
        current_date,
    )


@tool
def get_implied_volatility(
    symbol: Annotated[str, "ticker symbol of the company"],
    date: Annotated[str, "Date to retrieve IV for in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve the implied volatility (IV) for options on a given stock.
    Implied volatility represents the market's expectation of future volatility.
    Higher IV typically means more expensive options and greater expected price movement.
    
    Args:
        symbol (str): Ticker symbol of the company
        date (str): Date in yyyy-mm-dd format
    
    Returns:
        str: Implied volatility data including IV percentile and historical comparison
    """
    return route_to_vendor("get_implied_volatility", symbol, date)


@tool
def analyze_option_strategy(
    symbol: Annotated[str, "ticker symbol of the company"],
    strategy_type: Annotated[
        str,
        "Type of options strategy: 'covered_call', 'protective_put', 'bull_call_spread', 'bear_put_spread', 'iron_condor', 'straddle', 'strangle'",
    ],
    current_price: Annotated[float, "Current price of the underlying stock"],
    date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
    """
    Analyze a specific options strategy and provide profit/loss scenarios.
    
    Available strategies:
    - covered_call: Own stock + sell call (income generation)
    - protective_put: Own stock + buy put (downside protection)
    - bull_call_spread: Buy call + sell higher strike call (bullish, limited risk)
    - bear_put_spread: Buy put + sell lower strike put (bearish, limited risk)
    - iron_condor: Sell OTM call & put + buy further OTM call & put (neutral, range-bound)
    - straddle: Buy call + put at same strike (high volatility expected)
    - strangle: Buy OTM call + OTM put (high volatility, lower cost than straddle)
    
    Args:
        symbol (str): Ticker symbol
        strategy_type (str): Name of the strategy
        current_price (float): Current stock price
        date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: Analysis of the strategy including max profit, max loss, breakeven points, and probability of profit
    """
    return route_to_vendor(
        "analyze_option_strategy", symbol, strategy_type, current_price, date
    )


@tool
def get_option_volume_and_oi(
    symbol: Annotated[str, "ticker symbol of the company"],
    date: Annotated[str, "Date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve options volume and open interest data to gauge market sentiment and liquidity.
    
    - Volume: Number of contracts traded today (indicates current interest)
    - Open Interest: Total number of outstanding contracts (indicates overall market interest)
    - Put/Call Ratio: Ratio of put volume to call volume (sentiment indicator)
    
    High put/call ratio may indicate bearish sentiment, low ratio may indicate bullish sentiment.
    
    Args:
        symbol (str): Ticker symbol
        date (str): Date in yyyy-mm-dd format
    
    Returns:
        str: Options volume, open interest, and put/call ratio analysis
    """
    return route_to_vendor("get_option_volume_and_oi", symbol, date)
