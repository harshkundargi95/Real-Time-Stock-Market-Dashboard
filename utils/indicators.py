import pandas as pd
import numpy as np


def add_moving_averages(df: pd.DataFrame, windows: list = [20, 50, 200]) -> pd.DataFrame:
    """Add Simple Moving Averages to dataframe."""
    for window in windows:
        if len(df) >= window:
            df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()
    return df


def add_ema(df: pd.DataFrame, windows: list = [12, 26]) -> pd.DataFrame:
    """Add Exponential Moving Averages."""
    for window in windows:
        df[f"EMA_{window}"] = df["Close"].ewm(span=window, adjust=False).mean()
    return df


def add_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2) -> pd.DataFrame:
    """Add Bollinger Bands."""
    if len(df) >= window:
        sma = df["Close"].rolling(window=window).mean()
        std = df["Close"].rolling(window=window).std()
        df["BB_Upper"] = sma + (std * num_std)
        df["BB_Middle"] = sma
        df["BB_Lower"] = sma - (std * num_std)
    return df


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Add Relative Strength Index."""
    if len(df) < window:
        return df
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Add MACD indicator."""
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Add Volume Weighted Average Price."""
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df


def get_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
    """Calculate simple support and resistance levels."""
    if len(df) < window:
        return {}
    recent = df.tail(window * 3)
    resistance = recent["High"].rolling(window=window).max().iloc[-1]
    support = recent["Low"].rolling(window=window).min().iloc[-1]
    return {"support": support, "resistance": resistance}


def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily and cumulative returns."""
    df["Daily_Return"] = df["Close"].pct_change() * 100
    df["Cumulative_Return"] = ((1 + df["Close"].pct_change()).cumprod() - 1) * 100
    return df


def get_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """Calculate annualized volatility."""
    if len(df) < 2:
        return 0
    daily_returns = df["Close"].pct_change().dropna()
    return daily_returns.rolling(window=window).std().iloc[-1] * np.sqrt(252) * 100
