import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Dark terminal color theme
COLORS = {
    "bg": "#0a0e1a",
    "panel": "#0f1629",
    "border": "#1e2d4a",
    "green": "#00d4aa",
    "red": "#ff4757",
    "blue": "#3d8ef8",
    "yellow": "#ffd32a",
    "purple": "#a55eea",
    "text": "#c8d6ef",
    "dim": "#4a5568",
    "white": "#e8f0fe",
    "orange": "#ff6b35",
}


def make_candlestick_chart(df: pd.DataFrame, ticker: str, show_volume: bool = True,
                            show_sma: bool = True, show_bb: bool = False) -> go.Figure:
    """Create a candlestick chart with optional indicators."""
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1.0]

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name=ticker,
        increasing_line_color=COLORS["green"],
        decreasing_line_color=COLORS["red"],
        increasing_fillcolor=COLORS["green"],
        decreasing_fillcolor=COLORS["red"],
        line=dict(width=1),
    ), row=1, col=1)

    # SMAs
    if show_sma:
        sma_colors = {
            "SMA_20": COLORS["blue"],
            "SMA_50": COLORS["yellow"],
            "SMA_200": COLORS["purple"],
        }
        for sma_col, color in sma_colors.items():
            if sma_col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[sma_col],
                    name=sma_col.replace("_", " "),
                    line=dict(color=color, width=1.5),
                    opacity=0.8,
                ), row=1, col=1)

    # Bollinger Bands
    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Upper"],
            name="BB Upper",
            line=dict(color=COLORS["orange"], width=1, dash="dot"),
            opacity=0.6,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Lower"],
            name="BB Lower",
            line=dict(color=COLORS["orange"], width=1, dash="dot"),
            fill="tonexty",
            fillcolor="rgba(255,107,53,0.05)",
            opacity=0.6,
        ), row=1, col=1)

    # Volume bars
    if show_volume and "Volume" in df.columns:
        colors = [COLORS["green"] if df["Close"].iloc[i] >= df["Open"].iloc[i]
                  else COLORS["red"] for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            name="Volume",
            marker_color=colors,
            opacity=0.6,
            showlegend=False,
        ), row=2, col=1)

    _apply_dark_theme(fig, rows)
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=520,
        title=dict(text=f"{ticker} — Price Chart", font=dict(color=COLORS["white"], size=14)),
    )
    return fig


def make_rsi_chart(df: pd.DataFrame) -> go.Figure:
    """Create RSI chart."""
    fig = go.Figure()

    if "RSI" not in df.columns:
        return fig

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI (14)",
        line=dict(color=COLORS["blue"], width=2),
        fill="tozeroy",
        fillcolor="rgba(61,142,248,0.08)",
    ))

    # Overbought / Oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color=COLORS["red"], opacity=0.6,
                  annotation_text="Overbought (70)", annotation_font_color=COLORS["red"])
    fig.add_hline(y=30, line_dash="dash", line_color=COLORS["green"], opacity=0.6,
                  annotation_text="Oversold (30)", annotation_font_color=COLORS["green"])
    fig.add_hline(y=50, line_dash="dot", line_color=COLORS["dim"], opacity=0.4)

    _apply_dark_theme(fig, 1)
    fig.update_layout(
        height=220,
        title=dict(text="RSI — Relative Strength Index", font=dict(color=COLORS["white"], size=13)),
        yaxis=dict(range=[0, 100]),
    )
    return fig


def make_macd_chart(df: pd.DataFrame) -> go.Figure:
    """Create MACD chart."""
    if "MACD" not in df.columns:
        return go.Figure()

    fig = make_subplots(rows=1, cols=1)

    hist_colors = [COLORS["green"] if v >= 0 else COLORS["red"]
                   for v in df["MACD_Hist"].fillna(0)]

    fig.add_trace(go.Bar(
        x=df.index, y=df["MACD_Hist"],
        name="MACD Histogram",
        marker_color=hist_colors,
        opacity=0.7,
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD",
        line=dict(color=COLORS["blue"], width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_Signal"],
        name="Signal",
        line=dict(color=COLORS["orange"], width=1.5),
    ))

    _apply_dark_theme(fig, 1)
    fig.update_layout(
        height=220,
        title=dict(text="MACD — Moving Average Convergence Divergence",
                   font=dict(color=COLORS["white"], size=13)),
    )
    return fig


def make_comparison_chart(data_dict: dict) -> go.Figure:
    """Create normalized comparison chart for multiple stocks."""
    fig = go.Figure()
    palette = [COLORS["blue"], COLORS["green"], COLORS["yellow"],
               COLORS["purple"], COLORS["orange"]]

    for i, (ticker, df) in enumerate(data_dict.items()):
        if df.empty:
            continue
        normalized = (df["Close"] / df["Close"].iloc[0] - 1) * 100
        fig.add_trace(go.Scatter(
            x=df.index, y=normalized,
            name=ticker,
            line=dict(color=palette[i % len(palette)], width=2),
        ))

    fig.add_hline(y=0, line_dash="dot", line_color=COLORS["dim"], opacity=0.5)
    _apply_dark_theme(fig, 1)
    fig.update_layout(
        height=400,
        title=dict(text="Performance Comparison (% Return from Start)",
                   font=dict(color=COLORS["white"], size=14)),
        yaxis_ticksuffix="%",
    )
    return fig


def make_returns_histogram(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Create daily returns histogram."""
    fig = go.Figure()

    if "Daily_Return" not in df.columns:
        return fig

    returns = df["Daily_Return"].dropna()
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        name="Daily Returns",
        marker_color=COLORS["blue"],
        opacity=0.75,
    ))

    fig.add_vline(x=returns.mean(), line_dash="dash",
                  line_color=COLORS["yellow"], opacity=0.8,
                  annotation_text=f"Mean: {returns.mean():.2f}%",
                  annotation_font_color=COLORS["yellow"])

    _apply_dark_theme(fig, 1)
    fig.update_layout(
        height=280,
        title=dict(text=f"{ticker} — Daily Returns Distribution",
                   font=dict(color=COLORS["white"], size=13)),
        xaxis_ticksuffix="%",
    )
    return fig


def _apply_dark_theme(fig: go.Figure, rows: int):
    """Apply consistent dark theme to figure."""
    axis_style = dict(
        gridcolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["dim"], size=11),
        color=COLORS["dim"],
    )
    layout_updates = dict(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["text"], family="'JetBrains Mono', monospace"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor="rgba(15,22,41,0.8)",
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(color=COLORS["text"], size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS["panel"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["white"], size=11),
        ),
    )
    fig.update_layout(**layout_updates)
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
