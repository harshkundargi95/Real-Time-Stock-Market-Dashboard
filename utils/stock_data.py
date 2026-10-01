import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

POPULAR_STOCKS = {
    # US Stocks
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    
    # Indian Stocks (NSE)
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy (TCS)": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC Limited": "ITC.NS"
}

PERIOD_MAP = {
    "1 Day": ("1d", "5m"),
    "5 Days": ("5d", "15m"),
    "1 Month": ("1mo", "1h"),
    "3 Months": ("3mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "2 Years": ("2y", "1wk"),
    "5 Years": ("5y", "1wk"),
}

def get_stock_data(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical stock data."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None) if df.index.tz else df.index
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def get_stock_info(ticker: str) -> dict:
    """Fetch company info and key metrics."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", None),
            "eps": info.get("trailingEps", None),
            "52w_high": info.get("fiftyTwoWeekHigh", None),
            "52w_low": info.get("fiftyTwoWeekLow", None),
            "avg_volume": info.get("averageVolume", None),
            "dividend_yield": info.get("dividendYield", None),
            "beta": info.get("beta", None),
            "description": info.get("longBusinessSummary", ""),
            "website": info.get("website", ""),
            "currency": info.get("currency", "USD"),
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {}

def get_current_price(ticker: str) -> dict:
    """Get current/latest price data."""
    try:
        stock = yf.Ticker(ticker)
        # Fetch 5 days to safely skip weekends/holidays/bad data
        df = stock.history(period="5d", interval="1d")
        
        if df.empty:
            return {}
            
        # THE FIX: Drop any broken rows where Yahoo forgot to send the price
        df = df.dropna(subset=["Close", "Open", "High", "Low"])
        
        if df.empty:
            return {}

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
        
        change = latest["Close"] - prev["Close"]
        change_pct = (change / prev["Close"]) * 100
        
        return {
            "price": latest["Close"],
            "open": latest["Open"],
            "high": latest["High"],
            "low": latest["Low"],
            "volume": latest["Volume"],
            "change": change,
            "change_pct": change_pct,
        }
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return {}

def format_market_cap(value: float, symbol: str = "$") -> str:
    """Format market cap to human-readable string."""
    if not value:
        return "N/A"
    if value >= 1e12:
        return f"{symbol}{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"{symbol}{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{symbol}{value/1e6:.2f}M"
    return f"{symbol}{value:,.0f}"

def format_volume(value: float) -> str:
    """Format volume to human-readable string."""
    if not value:
        return "N/A"
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    return f"{value:,.0f}"