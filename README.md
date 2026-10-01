# 📈 StockPulse — Real-Time Stock Market Dashboard

A professional-grade stock market dashboard built with **Python + Streamlit + Plotly**.
Track live prices, visualize trends, analyze technical indicators, and compare stocks side-by-side.


## 🌐 Live Demo

**Deploy Link:** https://real-time-stock-market-dashboard-using-python-app-plotly-hsk.streamlit.app/

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Live Prices** | Real-time quotes via Yahoo Finance |
| **Candlestick Charts** | Interactive OHLCV candlestick charts |
| **Technical Indicators** | SMA 20/50/200, Bollinger Bands, RSI, MACD |
| **Multi-Stock Comparison** | Compare up to 5 stocks by normalized % return |
| **Fundamentals Panel** | P/E, Market Cap, EPS, Beta, 52W range, description |
| **Analytics Tab** | Stats, returns distribution histogram, raw data |
| **CSV Export** | Download historical data as CSV |
| **Dark UI** | Sleek Bloomberg-style dark terminal interface |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Web framework / UI
- **yfinance** — Yahoo Finance data API
- **Plotly** — Interactive charts
- **Pandas / NumPy** — Data processing

---

## ⚙️ Setup & Installation

### 1. Clone / Download the project
```bash
git clone <your-repo-url>
cd stock_dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** 🎉

---

## 📁 Project Structure

```
stock_dashboard/
├── app.py                  # Main Streamlit app (UI + layout)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── utils/
    ├── __init__.py         # Module exports
    ├── stock_data.py       # Yahoo Finance data fetching
    ├── indicators.py       # Technical indicator calculations
    └── charts.py           # Plotly chart builders
```

---

## 🎛️ How to Use

1. **Enter a ticker** (e.g. `AAPL`, `NVDA`, `BTC-USD`) in the sidebar or pick from popular stocks
2. **Choose a time range** using the slider (1 Day → 5 Years)
3. **Toggle overlays** — SMA, Bollinger Bands, RSI, MACD, Volume
4. **Compare mode** — Add multiple stocks to the comparison section
5. **Download** raw data as CSV from the Analytics tab

---

## 📊 Indicators Explained

| Indicator | What it tells you |
|---|---|
| **SMA 20 / 50 / 200** | Short/medium/long-term trend direction |
| **Bollinger Bands** | Volatility and potential reversal zones |
| **RSI (14)** | Momentum; >70 overbought, <30 oversold |
| **MACD** | Trend momentum and crossover signals |

---

## ⚠️ Disclaimer

This dashboard is for **educational and research purposes only**.
It is **not financial advice**. Always do your own due diligence before making investment decisions.

---

## 🔮 Potential Extensions

- [ ] Add crypto support (BTC-USD, ETH-USD already work via yfinance)
- [ ] Portfolio tracker with custom watchlist
- [ ] Price alerts via email/SMS
- [ ] Machine learning price prediction (Prophet / LSTM)
- [ ] News sentiment integration
- [ ] Options chain viewer
