import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# POPULAR STOCKS
# ============================================================

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
    "ITC Limited": "ITC.NS",
}


# ============================================================
# FALLBACK COMPANY METADATA
# ============================================================
#
# Yahoo Finance's stock.info endpoint can occasionally return
# incomplete data depending on environment/network/rate limits.
#
# These values are used ONLY when Yahoo does not provide them.
# Prices and historical data remain live from Yahoo Finance.
#

STOCK_METADATA = {
    # ---------------- US STOCKS ----------------

    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
    },

    "MSFT": {
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "industry": "Software—Infrastructure",
    },

    "GOOGL": {
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
    },

    "AMZN": {
        "name": "Amazon.com, Inc.",
        "sector": "Consumer Cyclical",
        "industry": "Internet Retail",
    },

    "TSLA": {
        "name": "Tesla, Inc.",
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
    },

    "META": {
        "name": "Meta Platforms, Inc.",
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
    },

    "NVDA": {
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
    },

    "NFLX": {
        "name": "Netflix, Inc.",
        "sector": "Communication Services",
        "industry": "Entertainment",
    },

    "BRK-B": {
        "name": "Berkshire Hathaway Inc.",
        "sector": "Financial Services",
        "industry": "Insurance—Diversified",
    },

    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "sector": "Financial Services",
        "industry": "Banks—Diversified",
    },


    # ---------------- INDIAN STOCKS ----------------

    "RELIANCE.NS": {
        "name": "Reliance Industries Limited",
        "sector": "Energy",
        "industry": "Oil & Gas Integrated",
    },

    "TCS.NS": {
        "name": "Tata Consultancy Services Limited",
        "sector": "Technology",
        "industry": "Information Technology Services",
    },

    "HDFCBANK.NS": {
        "name": "HDFC Bank Limited",
        "sector": "Financial Services",
        "industry": "Banks—Diversified",
    },

    "INFY.NS": {
        "name": "Infosys Limited",
        "sector": "Technology",
        "industry": "Information Technology Services",
    },

    "TATAMOTORS.NS": {
        "name": "Tata Motors Limited",
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
    },

    "SBIN.NS": {
        "name": "State Bank of India",
        "sector": "Financial Services",
        "industry": "Banks—Diversified",
    },

    "BHARTIARTL.NS": {
        "name": "Bharti Airtel Limited",
        "sector": "Communication Services",
        "industry": "Telecom Services",
    },

    "ITC.NS": {
        "name": "ITC Limited",
        "sector": "Consumer Defensive",
        "industry": "Tobacco",
    },
}


# ============================================================
# PERIOD MAP
# ============================================================

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


# ============================================================
# HISTORICAL STOCK DATA
# ============================================================

def get_stock_data(
    ticker: str,
    period: str = "3mo",
    interval: str = "1d"
) -> pd.DataFrame:
    """Fetch historical stock data."""

    try:
        stock = yf.Ticker(ticker)

        df = stock.history(
            period=period,
            interval=interval
        )

        if df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df.index)

        if df.index.tz:
            df.index = df.index.tz_localize(None)

        return df

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


# ============================================================
# COMPANY INFORMATION
# ============================================================

def get_stock_info(ticker: str) -> dict:
    """
    Fetch company information and key metrics.

    Yahoo Finance's `stock.info` can sometimes return incomplete
    metadata when running on Streamlit Cloud.

    We therefore:
        1. Start with local fallback metadata.
        2. Try Yahoo Finance.
        3. Use Yahoo values when available.
        4. Keep fallback values when Yahoo values are missing.
    """

    # Get our local fallback data first.
    fallback = STOCK_METADATA.get(
        ticker,
        {
            "name": ticker,
            "sector": "N/A",
            "industry": "N/A",
        }
    )

    try:
        stock = yf.Ticker(ticker)

        # Yahoo Finance company information
        info = stock.info or {}

        # ----------------------------------------------------
        # Use Yahoo data when available.
        # Otherwise use our fallback metadata.
        # ----------------------------------------------------

        name = (
            info.get("longName")
            or info.get("shortName")
            or fallback.get("name")
            or ticker
        )

        sector = (
            info.get("sector")
            or fallback.get("sector")
            or "N/A"
        )

        industry = (
            info.get("industry")
            or fallback.get("industry")
            or "N/A"
        )

        return {
            "name": name,

            # These are now protected by fallback values.
            "sector": sector,
            "industry": industry,

            # Dynamic Yahoo Finance values.
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),

            "description": info.get(
                "longBusinessSummary",
                ""
            ),

            "website": info.get(
                "website",
                ""
            ),

            "currency": info.get(
                "currency",
                "USD"
            ),
        }

    except Exception as e:

        # IMPORTANT:
        # Do NOT return {} here.
        #
        # Returning {} was one of the reasons the UI could
        # eventually fall back to N/A values.
        #
        # Instead, return our local metadata so that the
        # application still has useful company information.

        print(
            f"Error fetching company info for {ticker}: {e}"
        )

        return {
            "name": fallback.get("name", ticker),
            "sector": fallback.get("sector", "N/A"),
            "industry": fallback.get("industry", "N/A"),

            "market_cap": 0,
            "pe_ratio": None,
            "eps": None,
            "52w_high": None,
            "52w_low": None,
            "avg_volume": None,
            "dividend_yield": None,
            "beta": None,

            "description": "",
            "website": "",

            # Most of your US stocks use USD.
            # Indian NSE stocks use INR.
            "currency": (
                "INR"
                if ticker.endswith(".NS")
                else "USD"
            ),
        }


# ============================================================
# CURRENT PRICE
# ============================================================

def get_current_price(ticker: str) -> dict:
    """Get current/latest price data."""

    try:
        stock = yf.Ticker(ticker)

        # Fetch 5 days to safely skip weekends,
        # holidays and bad/incomplete data.
        df = stock.history(
            period="5d",
            interval="1d"
        )

        if df.empty:
            return {}

        # Drop broken rows where Yahoo did not provide prices.
        df = df.dropna(
            subset=[
                "Close",
                "Open",
                "High",
                "Low"
            ]
        )

        if df.empty:
            return {}

        latest = df.iloc[-1]

        prev = (
            df.iloc[-2]
            if len(df) > 1
            else df.iloc[-1]
        )

        change = latest["Close"] - prev["Close"]

        if prev["Close"] != 0:
            change_pct = (
                change / prev["Close"]
            ) * 100
        else:
            change_pct = 0

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
        print(
            f"Error fetching price for {ticker}: {e}"
        )
        return {}


# ============================================================
# FORMAT MARKET CAP
# ============================================================

def format_market_cap(
    value: float,
    symbol: str = "$"
) -> str:
    """Format market cap to human-readable string."""

    if not value:
        return "N/A"

    if value >= 1e12:
        return f"{symbol}{value / 1e12:.2f}T"

    elif value >= 1e9:
        return f"{symbol}{value / 1e9:.2f}B"

    elif value >= 1e6:
        return f"{symbol}{value / 1e6:.2f}M"

    return f"{symbol}{value:,.0f}"


# ============================================================
# FORMAT VOLUME
# ============================================================

def format_volume(value: float) -> str:
    """Format volume to human-readable string."""

    if not value:
        return "N/A"

    if value >= 1e9:
        return f"{value / 1e9:.2f}B"

    elif value >= 1e6:
        return f"{value / 1e6:.2f}M"

    elif value >= 1e3:
        return f"{value / 1e3:.2f}K"

    return f"{value:,.0f}"
