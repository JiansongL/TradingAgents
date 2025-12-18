"""
Options data provider using yfinance
This module provides options chain data, Greeks calculation, and IV analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm
import warnings

warnings.filterwarnings("ignore")


def get_options_chain(symbol: str, date: str) -> str:
    """
    Retrieve options chain data for a given symbol
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get all available expiration dates
        expirations = ticker.options
        
        if not expirations:
            return f"No options data available for {symbol}"
        
        # Find the closest expiration date to the requested date
        target_date = datetime.strptime(date, "%Y-%m-%d")
        closest_exp = min(
            expirations,
            key=lambda x: abs(
                datetime.strptime(x, "%Y-%m-%d") - target_date
            ),
        )
        
        # Get options chain for the closest expiration
        opt_chain = ticker.option_chain(closest_exp)
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # Format the output
        result = f"Options Chain for {symbol} (Expiration: {closest_exp})\n\n"
        
        result += "=== CALL OPTIONS ===\n"
        result += calls[
            [
                "strike",
                "lastPrice",
                "bid",
                "ask",
                "volume",
                "openInterest",
                "impliedVolatility",
            ]
        ].head(10).to_string()
        
        result += "\n\n=== PUT OPTIONS ===\n"
        result += puts[
            [
                "strike",
                "lastPrice",
                "bid",
                "ask",
                "volume",
                "openInterest",
                "impliedVolatility",
            ]
        ].head(10).to_string()
        
        return result
        
    except Exception as e:
        return f"Error retrieving options chain for {symbol}: {str(e)}"


def calculate_option_greeks(
    symbol: str,
    strike_price: float,
    expiration_date: str,
    option_type: str,
    current_date: str,
) -> str:
    """
    Calculate Black-Scholes Greeks for an option
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current stock price
        hist = ticker.history(period="1d")
        if hist.empty:
            return f"Unable to retrieve current price for {symbol}"
        
        S = hist["Close"].iloc[-1]  # Current stock price
        K = strike_price  # Strike price
        
        # Calculate time to expiration in years
        exp_dt = datetime.strptime(expiration_date, "%Y-%m-%d")
        curr_dt = datetime.strptime(current_date, "%Y-%m-%d")
        T = (exp_dt - curr_dt).days / 365.0
        
        if T <= 0:
            return "Option has already expired or expires today"
        
        # Get implied volatility (using historical volatility as approximation)
        hist_data = ticker.history(period="1y")
        returns = np.log(hist_data["Close"] / hist_data["Close"].shift(1))
        sigma = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Risk-free rate (approximation)
        r = 0.04
        
        # Black-Scholes calculations
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == "call":
            # Call option Greeks
            delta = norm.cdf(d1)
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                - r * K * np.exp(-r * T) * norm.cdf(d2)
            ) / 365
            option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            # Put option Greeks
            delta = norm.cdf(d1) - 1
            theta = (
                -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                + r * K * np.exp(-r * T) * norm.cdf(-d2)
            ) / 365
            option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        # Greeks common to both calls and puts
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        rho = (
            K * T * np.exp(-r * T) * norm.cdf(d2) / 100
            if option_type.lower() == "call"
            else -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        )
        
        result = f"Greeks for {symbol} {option_type.upper()} option\n"
        result += f"Strike: ${K}, Expiration: {expiration_date}\n"
        result += f"Current Stock Price: ${S:.2f}\n"
        result += f"Theoretical Option Price: ${option_price:.2f}\n\n"
        result += f"Delta: {delta:.4f} (change in option price per $1 change in stock)\n"
        result += f"Gamma: {gamma:.4f} (change in delta per $1 change in stock)\n"
        result += f"Theta: ${theta:.4f} (daily time decay)\n"
        result += f"Vega: ${vega:.4f} (change in option price per 1% change in IV)\n"
        result += f"Rho: ${rho:.4f} (change in option price per 1% change in interest rate)\n"
        result += f"\nImplied Volatility (estimated): {sigma*100:.2f}%\n"
        result += f"Days to Expiration: {int(T*365)}\n"
        
        return result
        
    except Exception as e:
        return f"Error calculating Greeks: {str(e)}"


def get_implied_volatility(symbol: str, date: str) -> str:
    """
    Retrieve implied volatility data for options
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get options data
        expirations = ticker.options
        if not expirations:
            return f"No options data available for {symbol}"
        
        # Get IV from the first expiration
        opt_chain = ticker.option_chain(expirations[0])
        
        # Calculate average IV for ATM options
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # Get current stock price
        current_price = ticker.history(period="1d")["Close"].iloc[-1]
        
        # Find ATM options (closest to current price)
        atm_calls = calls.iloc[(calls["strike"] - current_price).abs().argsort()[:5]]
        atm_puts = puts.iloc[(puts["strike"] - current_price).abs().argsort()[:5]]
        
        avg_call_iv = atm_calls["impliedVolatility"].mean() * 100
        avg_put_iv = atm_puts["impliedVolatility"].mean() * 100
        
        # Calculate historical volatility
        hist_data = ticker.history(period="1y")
        returns = np.log(hist_data["Close"] / hist_data["Close"].shift(1))
        hist_vol = returns.std() * np.sqrt(252) * 100
        
        result = f"Implied Volatility Analysis for {symbol}\n\n"
        result += f"Current Stock Price: ${current_price:.2f}\n"
        result += f"ATM Call IV: {avg_call_iv:.2f}%\n"
        result += f"ATM Put IV: {avg_put_iv:.2f}%\n"
        result += f"Historical Volatility (1Y): {hist_vol:.2f}%\n\n"
        
        iv_premium = avg_call_iv - hist_vol
        result += f"IV Premium: {iv_premium:.2f}% "
        
        if iv_premium > 10:
            result += "(Options are expensive - good for selling strategies)\n"
        elif iv_premium < -10:
            result += "(Options are cheap - good for buying strategies)\n"
        else:
            result += "(Options fairly priced)\n"
        
        return result
        
    except Exception as e:
        return f"Error retrieving implied volatility: {str(e)}"


def analyze_option_strategy(
    symbol: str, strategy_type: str, current_price: float, date: str
) -> str:
    """
    Analyze options strategy profit/loss scenarios
    """
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        
        if not expirations:
            return f"No options data available for {symbol}"
        
        opt_chain = ticker.option_chain(expirations[0])
        
        result = f"Strategy Analysis: {strategy_type.upper().replace('_', ' ')}\n"
        result += f"Symbol: {symbol}, Current Price: ${current_price:.2f}\n"
        result += f"Analysis Date: {date}\n\n"
        
        if strategy_type == "covered_call":
            # Find OTM call
            otm_calls = opt_chain.calls[opt_chain.calls["strike"] > current_price].head(3)
            if not otm_calls.empty:
                strike = otm_calls.iloc[0]["strike"]
                premium = otm_calls.iloc[0]["lastPrice"]
                result += f"Sell Call Strike: ${strike:.2f}, Premium: ${premium:.2f}\n"
                result += f"Max Profit: ${(strike - current_price + premium):.2f} (if stock >= ${strike})\n"
                result += f"Max Loss: Unlimited (if stock drops significantly)\n"
                result += f"Breakeven: ${(current_price - premium):.2f}\n"
        
        elif strategy_type == "protective_put":
            # Find OTM put
            otm_puts = opt_chain.puts[opt_chain.puts["strike"] < current_price].tail(3)
            if not otm_puts.empty:
                strike = otm_puts.iloc[-1]["strike"]
                premium = otm_puts.iloc[-1]["lastPrice"]
                result += f"Buy Put Strike: ${strike:.2f}, Premium: ${premium:.2f}\n"
                result += f"Max Loss: ${(current_price - strike + premium):.2f}\n"
                result += f"Breakeven: ${(current_price + premium):.2f}\n"
        
        elif strategy_type == "bull_call_spread":
            calls = opt_chain.calls[opt_chain.calls["strike"] >= current_price].head(5)
            if len(calls) >= 2:
                buy_strike = calls.iloc[0]["strike"]
                sell_strike = calls.iloc[2]["strike"]
                net_debit = calls.iloc[0]["lastPrice"] - calls.iloc[2]["lastPrice"]
                result += f"Buy Call: ${buy_strike:.2f}, Sell Call: ${sell_strike:.2f}\n"
                result += f"Net Debit: ${net_debit:.2f}\n"
                result += f"Max Profit: ${(sell_strike - buy_strike - net_debit):.2f}\n"
                result += f"Max Loss: ${net_debit:.2f}\n"
                result += f"Breakeven: ${(buy_strike + net_debit):.2f}\n"
        
        elif strategy_type == "straddle":
            # Find ATM options
            atm_call = opt_chain.calls.iloc[(opt_chain.calls["strike"] - current_price).abs().argsort()[0]]
            atm_put = opt_chain.puts.iloc[(opt_chain.puts["strike"] - current_price).abs().argsort()[0]]
            strike = atm_call["strike"]
            total_premium = atm_call["lastPrice"] + atm_put["lastPrice"]
            result += f"Strike: ${strike:.2f}\n"
            result += f"Total Premium: ${total_premium:.2f}\n"
            result += f"Upper Breakeven: ${(strike + total_premium):.2f}\n"
            result += f"Lower Breakeven: ${(strike - total_premium):.2f}\n"
            result += f"Max Loss: ${total_premium:.2f} (at strike price)\n"
            result += f"Max Profit: Unlimited\n"
            result += f"\nNote: This strategy profits from large price movements in either direction\n"
        
        else:
            result += f"Strategy '{strategy_type}' analysis not yet implemented\n"
        
        return result
        
    except Exception as e:
        return f"Error analyzing strategy: {str(e)}"


def get_option_volume_and_oi(symbol: str, date: str) -> str:
    """
    Retrieve options volume and open interest data
    """
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        
        if not expirations:
            return f"No options data available for {symbol}"
        
        opt_chain = ticker.option_chain(expirations[0])
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        total_call_volume = calls["volume"].sum()
        total_put_volume = puts["volume"].sum()
        total_call_oi = calls["openInterest"].sum()
        total_put_oi = puts["openInterest"].sum()
        
        pc_ratio_volume = total_put_volume / total_call_volume if total_call_volume > 0 else 0
        pc_ratio_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        result = f"Options Volume and Open Interest for {symbol}\n\n"
        result += f"Call Volume: {total_call_volume:,.0f}\n"
        result += f"Put Volume: {total_put_volume:,.0f}\n"
        result += f"Put/Call Volume Ratio: {pc_ratio_volume:.2f}\n\n"
        result += f"Call Open Interest: {total_call_oi:,.0f}\n"
        result += f"Put Open Interest: {total_put_oi:,.0f}\n"
        result += f"Put/Call OI Ratio: {pc_ratio_oi:.2f}\n\n"
        
        # Interpret the ratios
        if pc_ratio_volume > 1.0:
            result += "Volume Interpretation: BEARISH (more put buying)\n"
        elif pc_ratio_volume < 0.7:
            result += "Volume Interpretation: BULLISH (more call buying)\n"
        else:
            result += "Volume Interpretation: NEUTRAL\n"
        
        return result
        
    except Exception as e:
        return f"Error retrieving volume and OI data: {str(e)}"
