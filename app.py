import streamlit as st
import pandas as pd
from datetime import datetime
from utils.chatbot import analyze_stock, get_chat_response
from utils import (
    get_stock_data, get_stock_info, get_current_price,
    format_market_cap, format_volume, POPULAR_STOCKS, PERIOD_MAP,
    add_moving_averages, add_bollinger_bands, add_rsi, add_macd,
    add_vwap, calculate_returns, get_volatility,
    make_candlestick_chart, make_rsi_chart, make_macd_chart,
    make_comparison_chart, make_returns_histogram,
)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockPulse · Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0e1a;
    --panel: #0f1629;
    --border: #1e2d4a;
    --green: #00d4aa;
    --red: #ff4757;
    --blue: #3d8ef8;
    --yellow: #ffd32a;
    --text: #c8d6ef;
    --dim: #4a5568;
    --white: #e8f0fe;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--panel) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headers */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: var(--white) !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: var(--dim) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: var(--white) !important; font-size: 1.4rem !important; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600;
    color: var(--dim) !important;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom-color: var(--blue) !important;
    background: transparent !important;
}

/* Select/Input */
.stSelectbox > div > div, .stTextInput > div > div {
    background-color: var(--panel) !important;
    border-color: var(--border) !important;
    color: var(--white) !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Info cards */
.info-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}
.info-card-title {
    color: var(--dim);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.info-card-value {
    color: var(--white);
    font-size: 1rem;
    font-weight: 600;
}

/* Price tag */
.price-up { color: #00d4aa; }
.price-down { color: #ff4757; }
.price-neutral { color: #c8d6ef; }

/* Ticker badge */
.ticker-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e2d4a, #162038);
    border: 1px solid #3d8ef8;
    border-radius: 4px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: #3d8ef8;
    font-size: 0.9rem;
}

/* Logo / Header */
.dashboard-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--white);
    letter-spacing: -0.02em;
    margin-bottom: 0;
}
.dashboard-subtitle {
    font-size: 0.7rem;
    color: var(--dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--green);
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.stButton > button {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stButton > button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}

.stCheckbox label { color: var(--text) !important; }
.stSlider label { color: var(--text) !important; }
.stMultiSelect label { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="padding: 16px 0 8px;">
            <div class="dashboard-header">📈 StockPulse</div>
            <div class="dashboard-subtitle">Real-Time Market Dashboard</div>
        </div>
        <hr/>
    """, unsafe_allow_html=True)

    # Ticker input
    st.markdown("#### 🔍 Stock Selection")
    custom_ticker = st.text_input(
        "Enter Ticker Symbol",
        placeholder="e.g. AAPL, TSLA, NVDA",
        help="Enter any valid stock ticker symbol"
    ).upper().strip()

    st.markdown("**— or pick from popular —**")
    selected_name = st.selectbox("Popular Stocks", [""] + list(POPULAR_STOCKS.keys()))
    ticker = custom_ticker if custom_ticker else (POPULAR_STOCKS.get(selected_name, "") if selected_name else "AAPL")

    st.markdown("---")

    # Time period
    st.markdown("#### 📅 Time Period")
    period_label = st.select_slider(
        "Select Range",
        options=list(PERIOD_MAP.keys()),
        value="3 Months"
    )
    period, interval = PERIOD_MAP[period_label]

    st.markdown("---")

    # Chart overlays
    st.markdown("#### 🔧 Chart Overlays")
    show_sma = st.checkbox("Moving Averages (SMA 20/50/200)", value=True)
    show_bb = st.checkbox("Bollinger Bands", value=False)
    show_volume = st.checkbox("Volume", value=True)
    show_rsi = st.checkbox("RSI Indicator", value=True)
    show_macd = st.checkbox("MACD", value=False)

    st.markdown("---")

    # Comparison mode
    st.markdown("#### ⚡ Compare Stocks")
    compare_tickers = st.multiselect(
        "Add stocks to compare",
        options=list(POPULAR_STOCKS.values()) + ["SPY", "QQQ", "DIA"],
        default=[],
        max_selections=4,
        placeholder="Select up to 4 stocks"
    )
    if ticker and ticker not in compare_tickers:
        compare_tickers = [ticker] + compare_tickers

    st.markdown("---")
    st.markdown(f"""
        <div style="font-size: 0.65rem; color: var(--dim); text-align: center;">
            Data via Yahoo Finance · yfinance<br/>
            Last updated: {datetime.now().strftime('%H:%M:%S')}
        </div>
    """, unsafe_allow_html=True)

    refresh = st.button("🔄 Refresh Data", width="stretch")


# ─── MAIN CONTENT ───────────────────────────────────────────────────────────────
if not ticker:
    st.info("Enter a ticker symbol in the sidebar to get started.")
    st.stop()

# ─── FETCH DATA ─────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching data for **{ticker}**..."):
    df = get_stock_data(ticker, period=period, interval=interval)
    info = get_stock_info(ticker)
    price_data = get_current_price(ticker)

if df.empty:
    st.error(f"❌ Could not fetch data for **{ticker}**. Please check the ticker symbol.")
    st.stop()

# Apply indicators
df = add_moving_averages(df)
if show_bb:
    df = add_bollinger_bands(df)
df = add_rsi(df)
df = add_macd(df)
df = calculate_returns(df)

# ─── HEADER ──────────────────────────────────────────────────────────────────────
company_name = info.get("name", ticker)
sector = info.get("sector", "N/A")
price = price_data.get("price", 0)
change = price_data.get("change", 0)
change_pct = price_data.get("change_pct", 0)
color_class = "price-up" if change >= 0 else "price-down"
arrow = "▲" if change >= 0 else "▼"

# --- NEW: CURRENCY DETECTION ---
currency_code = info.get("currency", "USD")
currency_symbols = {"USD": "$", "INR": "₹", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"}
sym = currency_symbols.get(currency_code, "$") # Defaults to $ if currency is unknown

st.markdown(f"""
<div style="display:flex; align-items:center; gap:16px; padding: 8px 0 16px;">
    <div>
        <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#e8f0fe;">
            {company_name}
            <span class="ticker-badge" style="margin-left:10px; vertical-align: middle;">{ticker}</span>
        </div>
        <div style="color: #4a5568; font-size:0.75rem; margin-top:2px;">{sector} · {info.get("industry","N/A")}</div>
    </div>
    <div style="margin-left:auto; text-align:right;">
        <div style="font-size:2.2rem; font-weight:700; color:#e8f0fe;">{sym}{price:,.2f}</div>
        <div class="{color_class}" style="font-size:1rem; font-weight:600;">
            {arrow} {sym}{abs(change):.2f} ({arrow} {abs(change_pct):.2f}%)
        </div>
    </div>
</div>
<hr/>
""", unsafe_allow_html=True)

# ─── KEY METRICS ─────────────────────────────────────────────────────────────────
cols = st.columns(7)
metrics = [
    ("Open", f"{sym}{price_data.get('open', 0):,.2f}", None),
    ("Day High", f"{sym}{price_data.get('high', 0):,.2f}", None),
    ("Day Low", f"{sym}{price_data.get('low', 0):,.2f}", None),
    ("Volume", format_volume(price_data.get("volume", 0)), None),
    ("Market Cap", format_market_cap(info.get("market_cap", 0), sym), None),
    ("P/E Ratio", f"{info.get('pe_ratio', 0):.1f}" if info.get("pe_ratio") else "N/A", None),
    ("52W High", f"{sym}{info.get('52w_high', 0):,.2f}" if info.get("52w_high") else "N/A", None),
]
for col, (label, value, delta) in zip(cols, metrics):
    col.metric(label, value, delta)

st.markdown("<br/>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Chart & Indicators", "📉 Compare", "📋 Fundamentals", "🔬 Analytics", "💬 AI Chat"])

# ── TAB 1: CHART ───────────────────────────────────────────────────────────────
with tab1:
    fig = make_candlestick_chart(df, ticker, show_volume=show_volume, show_sma=show_sma, show_bb=show_bb)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    if show_rsi and "RSI" in df.columns:
        rsi_val = df["RSI"].iloc[-1]
        rsi_color = "#ff4757" if rsi_val > 70 else ("#00d4aa" if rsi_val < 30 else "#3d8ef8")
        st.markdown(f"""
            <div style="text-align:right; margin-top:-10px; margin-bottom:4px; font-size:0.8rem; color:{rsi_color};">
                RSI: <strong>{rsi_val:.1f}</strong>
                {"— ⚠️ Overbought" if rsi_val > 70 else ("— 💡 Oversold" if rsi_val < 30 else "— Neutral")}
            </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_rsi_chart(df), width="stretch", config={"displayModeBar": False})

    if show_macd and "MACD" in df.columns:
        st.plotly_chart(make_macd_chart(df), width="stretch", config={"displayModeBar": False})

# ── TAB 2: COMPARE ─────────────────────────────────────────────────────────────
with tab2:
    if len(compare_tickers) < 2:
        st.info("💡 Add stocks from the sidebar **Compare Stocks** section to compare performance.")
    else:
        with st.spinner("Fetching comparison data..."):
            data_dict = {}
            for t in compare_tickers:
                d = get_stock_data(t, period=period, interval=interval)
                if not d.empty:
                    data_dict[t] = d

        if data_dict:
            st.plotly_chart(make_comparison_chart(data_dict), width="stretch",
                            config={"displayModeBar": False})

            # Stats table
            stats_rows = []
            for t, d in data_dict.items():
                d = calculate_returns(d)
                ret = d["Cumulative_Return"].iloc[-1] if "Cumulative_Return" in d.columns else 0
                vol = get_volatility(d)
                stats_rows.append({
                    "Ticker": t,
                    "Return (Period)": f"{ret:+.2f}%",
                    "Annualized Volatility": f"{vol:.2f}%",
                    "Start Price": f"{sym}{d['Close'].iloc[0]:.2f}",
                    "End Price": f"{sym}{d['Close'].iloc[-1]:.2f}",
                    "Data Points": len(d),
                })
            st.dataframe(
                pd.DataFrame(stats_rows).set_index("Ticker"),
                width="stretch",
            )

# ── TAB 3: FUNDAMENTALS ─────────────────────────────────────────────────────────
with tab3:
    if not info:
        st.warning("Could not load fundamental data.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("##### 📌 Company Overview")
            fund_data = {
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Market Cap": format_market_cap(info.get("market_cap", 0), sym),
                "P/E Ratio": f"{info.get('pe_ratio', 0):.2f}" if info.get("pe_ratio") else "N/A",
                "EPS (TTM)": f"{sym}{info.get('eps', 0):.2f}" if info.get("eps") else "N/A",
                "Beta": f"{info.get('beta', 0):.2f}" if info.get("beta") else "N/A",
                "Dividend Yield": f"{info.get('dividend_yield', 0)*100:.2f}%" if info.get("dividend_yield") else "N/A",
            }
            for k, v in fund_data.items():
                st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">{k}</div>
                    <div class="info-card-value">{v}</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("##### 📊 52-Week Range")
            low_52 = info.get("52w_low", 0) or 0
            high_52 = info.get("52w_high", 0) or 0
            if low_52 and high_52 and high_52 > low_52:
                pct_pos = (price - low_52) / (high_52 - low_52) * 100
                st.markdown(f"""
                <div style="margin: 8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#4a5568; margin-bottom:6px;">
                        <span>52W Low: {sym}{low_52:.2f}</span>
                        <span>52W High: {sym}{high_52:.2f}</span>
                    </div>
                    <div style="background:#1e2d4a; border-radius:6px; height:10px; position:relative; overflow:hidden;">
                        <div style="background: linear-gradient(90deg, #00d4aa, #3d8ef8); width:{pct_pos:.1f}%; height:100%; border-radius:6px;"></div>
                    </div>
                    <div style="text-align:center; font-size:0.75rem; color:#c8d6ef; margin-top:4px;">
                        Current at <strong>{pct_pos:.1f}%</strong> of 52W range
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### 📰 About")
            description = info.get("description", "No description available.")
            if description and len(description) > 400:
                description = description[:400] + "..."
            st.markdown(f'<p style="font-size:0.8rem; color:#c8d6ef; line-height:1.6;">{description}</p>',
                        unsafe_allow_html=True)

            if info.get("website"):
                st.markdown(f'<a href="{info["website"]}" target="_blank" style="color:#3d8ef8; font-size:0.8rem;">🌐 {info["website"]}</a>',
                            unsafe_allow_html=True)

# ── TAB 4: ANALYTICS ───────────────────────────────────────────────────────────
with tab4:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("##### 📈 Price Statistics")
        if not df.empty:
            close = df["Close"]
            stats = {
                "Current Price": f"{sym}{price:.2f}",
                "Period High": f"{sym}{close.max():.2f}",
                "Period Low": f"{sym}{close.min():.2f}",
                "Period Avg": f"{sym}{close.mean():.2f}",
                "Period Return": f"{((close.iloc[-1]/close.iloc[0])-1)*100:+.2f}%",
                "Annualized Volatility": f"{get_volatility(df):.2f}%",
                "Total Candles": str(len(df)),
            }
            for k, v in stats.items():
                color = "#00d4aa" if "+" in str(v) else ("#ff4757" if "-" in str(v) else "#c8d6ef")
                if "Return" in k:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1e2d4a; font-size:0.85rem;">
                        <span style="color:#4a5568;">{k}</span>
                        <span style="color:{color}; font-weight:700;">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1e2d4a; font-size:0.85rem;">
                        <span style="color:#4a5568;">{k}</span>
                        <span style="color:#c8d6ef;">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown("##### 📊 Returns Distribution")
        st.plotly_chart(make_returns_histogram(df, ticker), width="stretch",
                        config={"displayModeBar": False})

    st.markdown("---")
    st.markdown("##### 📁 Raw Data")
    display_cols = ["Open", "High", "Low", "Close", "Volume"]
    if "RSI" in df.columns:
        display_cols.append("RSI")
    if "Daily_Return" in df.columns:
        display_cols.append("Daily_Return")

    display_df = df[display_cols].copy()
    display_df.index = display_df.index.strftime("%Y-%m-%d %H:%M") if interval in ["5m", "15m", "1h"] else display_df.index.strftime("%Y-%m-%d")
    display_df = display_df.round(2).iloc[::-1]
    st.dataframe(display_df, width="stretch", height=300)

    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        csv = df.to_csv().encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"{ticker}_{period_label.replace(' ', '_')}_data.csv",
            mime="text/csv",
        )

# ── TAB 5: AI CHAT ─────────────────────────────────────────────────────────────
with tab5:
    st.markdown("##### 💬 Market Assistant")
    st.markdown("<span style='color:var(--dim); font-size:0.85rem;'>Ask me anything about investing, technical indicators, or how to use this dashboard!</span>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)

    # Initialize chat history in Streamlit session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Create a scrollable container with a fixed height for the chat history
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Use a form for the input so it stays locked inside the tab
    with st.form("chat_input_form", clear_on_submit=True):
        cols = st.columns([5, 1])
        with cols[0]:
            user_input = st.text_input("Message", label_visibility="collapsed", placeholder="e.g., What is the difference between SMA and EMA?")
        with cols[1]:
            submit_btn = st.form_submit_button("Send", width="stretch")

    # Handle the submission
    if submit_btn and user_input:
        # Save user message and display it immediately
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Fetch and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_chat_response(st.session_state.chat_messages[:-1], user_input)
                    st.markdown(reply)
                    
        # Save AI response to history
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

# ─── AI ANALYZE ─────────────────────────────────────────────────────────────────
st.markdown("""
<hr/>
<div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800;
            color:#e8f0fe; margin-bottom:4px;">
    🤖 AI Stock Analysis
</div>
<div style="font-size:0.72rem; color:#4a5568; margin-bottom:12px;">
    Powered by Gemini AI · For educational purposes only · Not financial advice
</div>
""", unsafe_allow_html=True)

if st.button("🔍 Analyse " + ticker + " with AI", width="content"):
    with st.spinner("🤖 AI is analysing " + ticker + "... please wait"):
        result = analyze_stock(ticker, company_name, price_data, info, df.tail(60))

    if "error" in result:
        st.error("❌ " + result["error"])
    else:
        # ── Row 1: About + Trend ──────────────────────────────────────────────
        col1, col2 = st.columns([1.6, 1])

        with col1:
            st.markdown(f"""
            <div style="background:#0f1629; border:1px solid #1e2d4a; border-radius:10px;
                        padding:16px 20px; height:100%;">
                <div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase;
                            letter-spacing:0.1em; margin-bottom:6px;">📌 About the Company</div>
                <div style="color:#c8d6ef; font-size:0.92rem; line-height:1.6;">
                    {result.get('about','N/A')}
                </div>
            </div>""", unsafe_allow_html=True)

        with col2:
            trend    = result.get("trend", "N/A")
            t_upper  = trend.upper()
            if   "STRONG UPTREND"   in t_upper: t_color, t_icon = "#00d4aa", "🚀"
            elif "UPTREND"          in t_upper: t_color, t_icon = "#00d4aa", "📈"
            elif "STRONG DOWNTREND" in t_upper: t_color, t_icon = "#ff4757", "🔻"
            elif "DOWNTREND"        in t_upper: t_color, t_icon = "#ff4757", "📉"
            else:                                t_color, t_icon = "#ffd32a", "➡️"

            # Split verdict label from explanation
            trend_parts = trend.split(" — ", 1) if " — " in trend else trend.split(" ", 1)
            trend_label = trend_parts[0].strip()
            trend_desc  = trend_parts[1].strip() if len(trend_parts) > 1 else ""

            st.markdown(f"""
            <div style="background:#0f1629; border:1px solid #1e2d4a; border-radius:10px;
                        padding:16px 20px; height:100%;">
                <div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase;
                            letter-spacing:0.1em; margin-bottom:6px;">📊 Current Trend</div>
                <div style="color:{t_color}; font-size:1.15rem; font-weight:800;
                            font-family:'Syne',sans-serif; margin-bottom:6px;">
                    {t_icon}  {trend_label}
                </div>
                <div style="color:#7a8fa6; font-size:0.82rem; line-height:1.5;">
                    {trend_desc}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Row 2: Performance ───────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#0f1629; border:1px solid #1e2d4a; border-radius:10px;
                    padding:16px 20px;">
            <div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:6px;">📅 Recent Performance</div>
            <div style="color:#c8d6ef; font-size:0.92rem; line-height:1.7;">
                {result.get('performance','N/A')}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Row 3: Verdicts ───────────────────────────────────────────────────
        col3, col4 = st.columns(2)

        with col3:
            exp_raw    = result.get("experienced_verdict", "HOLD")
            exp_parts  = exp_raw.split(" — ", 1) if " — " in exp_raw else exp_raw.split(" ", 1)
            exp_label  = exp_parts[0].strip()
            exp_desc   = exp_parts[1].strip() if len(exp_parts) > 1 else ""
            exp_colors = {"BUY":"#00d4aa", "HOLD":"#ffd32a", "SELL":"#ff4757"}
            exp_icons  = {"BUY":"✅", "HOLD":"⏸️", "SELL":"❌"}
            exp_color  = exp_colors.get(exp_label.upper(), "#c8d6ef")
            exp_icon   = exp_icons.get(exp_label.upper(), "📊")

            st.markdown(f"""
            <div style="background:#0f1629; border:1px solid #1e2d4a; border-radius:10px;
                        padding:16px 20px;">
                <div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase;
                            letter-spacing:0.1em; margin-bottom:6px;">
                    💼 For Experienced Investors
                </div>
                <div style="color:{exp_color}; font-size:1.5rem; font-weight:800;
                            font-family:'Syne',sans-serif; margin-bottom:6px;">
                    {exp_icon}  {exp_label}
                </div>
                <div style="color:#7a8fa6; font-size:0.85rem; line-height:1.5;">
                    {exp_desc}
                </div>
            </div>""", unsafe_allow_html=True)

        with col4:
            beg_raw    = result.get("beginner_verdict", "AVOID")
            beg_parts  = beg_raw.split(" — ", 1) if " — " in beg_raw else beg_raw.split(" ", 1)
            beg_label  = beg_parts[0].strip()
            beg_desc   = beg_parts[1].strip() if len(beg_parts) > 1 else ""
            beg_colors = {"BUY":"#00d4aa", "AVOID":"#ff4757"}
            beg_icons  = {"BUY":"✅", "AVOID":"⚠️"}
            beg_color  = beg_colors.get(beg_label.upper(), "#c8d6ef")
            beg_icon   = beg_icons.get(beg_label.upper(), "📊")

            st.markdown(f"""
            <div style="background:#0f1629; border:1px solid #1e2d4a; border-radius:10px;
                        padding:16px 20px;">
                <div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase;
                            letter-spacing:0.1em; margin-bottom:6px;">
                    🎓 For Beginners
                </div>
                <div style="color:{beg_color}; font-size:1.5rem; font-weight:800;
                            font-family:'Syne',sans-serif; margin-bottom:6px;">
                    {beg_icon}  {beg_label}
                </div>
                <div style="color:#7a8fa6; font-size:0.85rem; line-height:1.5;">
                    {beg_desc}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Row 4: Final Suggestion ───────────────────────────────────────────
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0f1629, #162038);
                    border:1px solid #3d8ef8; border-radius:10px;
                    padding:18px 22px; border-left: 4px solid #3d8ef8;">
            <div style="font-size:0.7rem; color:#3d8ef8; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:8px;">🎯 Final Suggestion</div>
            <div style="color:#e8f0fe; font-size:0.95rem; line-height:1.7; font-weight:500;">
                {result.get('final_suggestion','N/A')}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; font-size:0.65rem; color:#2d3748; margin-top:10px;">
            ⚠️ This analysis is AI-generated for educational purposes only.
            It is NOT financial advice. Always do your own research before investing.
        </div>""", unsafe_allow_html=True)

# ─── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr/>
<div style="text-align:center; font-size:0.65rem; color:#2d3748; padding: 8px 0;">
    StockPulse Dashboard · Data sourced from Yahoo Finance via yfinance · For educational purposes only · Not financial advice
</div>
""", unsafe_allow_html=True)