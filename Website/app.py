from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Cache to reduce API calls
cache = {}

def get_stock_data(ticker, period='1m', interval='1d'):
    """Fetch stock data from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def format_daily_data(ticker):
    """Return daily closes for the last month up to yesterday"""
    try:
        data = get_stock_data(ticker, period='1mo', interval='1d')
        if data is None or data.empty:
            return {"error": "No data available"}

        today = datetime.utcnow().date()
        filtered = data[data.index.date < today]
        if filtered.empty:
            return {"error": "No historical data before today"}

        recent = filtered.tail(30)
        labels = [d.strftime('%Y-%m-%d') for d in recent.index]
        values = [round(float(price), 2) for price in recent['Close']]
        
        return {
            "ticker": ticker,
            "range": "daily",
            "labels": labels,
            "values": values,
            "count": len(values)
        }
    except Exception as e:
        return {"error": str(e)}

def format_intraday_data(ticker):
    """Return yesterday's intraday trend (30-minute bars)"""
    try:
        data = get_stock_data(ticker, period='2d', interval='30m')
        if data is None or data.empty:
            return {"error": "No data available"}

        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        filtered = data[data.index.date == yesterday]

        # fallback: if market closed (weekends/holidays), use most recent available day
        if filtered.empty and not data.empty:
            last_date = data.index.date[-1]
            filtered = data[data.index.date == last_date]

        if filtered.empty:
            return {"error": "No intraday data available"}

        labels = [ts.strftime('%H:%M') for ts in filtered.index]
        values = [round(float(price), 2) for price in filtered['Close']]

        return {
            "ticker": ticker,
            "range": "intraday",
            "labels": labels,
            "values": values,
            "count": len(values)
        }
    except Exception as e:
        return {"error": str(e)}

def format_monthly_data(ticker):
    """Return average close for the past month"""
    try:
        data = get_stock_data(ticker, period='1mo', interval='1d')
        if data is None or data.empty:
            return {"error": "No data available"}
        
        avg_close = round(float(data['Close'].mean()), 2)
        period_label = data.index[-1].strftime('%Y-%m')

        labels = [period_label]
        values = [avg_close]
        
        return {
            "ticker": ticker,
            "range": "monthly",
            "labels": labels,
            "values": values,
            "count": len(values)
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/<ticker>/daily', methods=['GET'])
def get_daily(ticker):
    """GET daily price data for 1 month"""
    ticker = ticker.upper()
    return jsonify(format_daily_data(ticker))

@app.route('/api/<ticker>/monthly', methods=['GET'])
def get_monthly(ticker):
    """GET monthly average price data for 1 year"""
    ticker = ticker.upper()
    return jsonify(format_monthly_data(ticker))

@app.route('/api/<ticker>/intraday', methods=['GET'])
def get_intraday(ticker):
    """GET yesterday intraday price trend"""
    ticker = ticker.upper()
    return jsonify(format_intraday_data(ticker))

@app.route('/api/<ticker>/info', methods=['GET'])
def get_info(ticker):
    """GET basic stock info"""
    try:
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        info = stock.info
        return jsonify({
            "ticker": ticker,
            "name": info.get('longName', 'N/A'),
            "price": info.get('currentPrice', 'N/A'),
            "change": info.get('regularMarketChange', 'N/A'),
            "changePercent": info.get('regularMarketChangePercent', 'N/A')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/<ticker>/decision', methods=['GET'])
def get_decision(ticker):
    """Use Gemini to decide BUY/SELL/HOLD"""
    try:
        ticker = ticker.upper()
        
        if not GEMINI_API_KEY:
            # Fallback if no API key
            return jsonify({
                "ticker": ticker,
                "action": "HOLD",
                "reason": "No Gemini API key configured. Using default HOLD action."
            })
        
        # Fetch recent data for context
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        info = stock.info
        
        if hist.empty:
            return jsonify({"error": "No data available"}), 400
        
        recent_prices = hist['Close'].tail(5).tolist()
        current_price = recent_prices[-1] if recent_prices else 0
        
        prompt = f"""You are a trading advisor using reinforcement learning to analyze stock data.

Ticker: {ticker}
Company: {info.get('longName', ticker)}
Current Price: ${current_price:.2f}
Recent 5-day closing prices: {[f'${p:.2f}' for p in recent_prices]}

Based on this data, provide a trading decision. Respond with ONLY one word: BUY, SELL, or HOLD.
Then on a new line, provide a brief one-sentence reason (max 15 words).

Format:
ACTION
Reason here."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse response
        lines = response.text.strip().split('\n')
        action = lines[0].strip().upper()
        reason = lines[1].strip() if len(lines) > 1 else "AI analysis complete."
        
        # Validate action
        if action not in ['BUY', 'SELL', 'HOLD']:
            action = 'HOLD'
            reason = "Unable to determine clear action; defaulting to HOLD."
        
        return jsonify({
            "ticker": ticker,
            "action": action,
            "reason": reason
        })
    except Exception as e:
        print(f"Gemini API error: {e}")
        return jsonify({
            "ticker": ticker,
            "action": "HOLD",
            "reason": f"Error during analysis: {str(e)[:50]}"
        }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/')
def index():
    """Serve index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS, images)"""
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='127.0.0.1')
