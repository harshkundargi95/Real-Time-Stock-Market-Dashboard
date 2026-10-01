import requests
import json
import streamlit as st
# ── Google Gemini Free API ─────────────────────────────────────────────────────
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = "" # Fallback if secret isn't set

GEMINI_MODEL   = "gemini-3.6-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

def analyze_stock(ticker: str, company_name: str, price_data: dict, info: dict, df_tail) -> dict:
    """Calls Gemini AI to analyze the stock returning a JSON."""
    price    = price_data.get("price", 0)
    change   = price_data.get("change", 0)
    chg_pct  = price_data.get("change_pct", 0)

    rsi_val  = round(float(df_tail["RSI"].iloc[-1]),  1) if "RSI"   in df_tail.columns and not df_tail["RSI"].isna().all()   else "N/A"
    macd_val = round(float(df_tail["MACD"].iloc[-1]), 4) if "MACD"  in df_tail.columns and not df_tail["MACD"].isna().all()  else "N/A"
    sma20    = round(float(df_tail["SMA_20"].iloc[-1]),2) if "SMA_20"  in df_tail.columns and not df_tail["SMA_20"].isna().all()  else "N/A"
    sma50    = round(float(df_tail["SMA_50"].iloc[-1]),2) if "SMA_50"  in df_tail.columns and not df_tail["SMA_50"].isna().all()  else "N/A"
    sma200   = round(float(df_tail["SMA_200"].iloc[-1]),2) if "SMA_200" in df_tail.columns and not df_tail["SMA_200"].isna().all() else "N/A"

    week_ret  = round((df_tail["Close"].iloc[-1] / df_tail["Close"].iloc[-5]  - 1) * 100, 2) if len(df_tail) >= 5  else "N/A"
    month_ret = round((df_tail["Close"].iloc[-1] / df_tail["Close"].iloc[-20] - 1) * 100, 2) if len(df_tail) >= 20 else "N/A"

    prompt = f"""You are a professional stock market analyst. Analyze this stock and respond ONLY in the following JSON format:

{{
  "about": "2 sentences: what the company does and which sector it belongs to",
  "trend": "One of: STRONG UPTREND / UPTREND / SIDEWAYS / DOWNTREND / STRONG DOWNTREND — then 1 sentence explaining why",
  "performance": "2 sentences about how the stock has performed recently based on week and month returns",
  "experienced_verdict": "One of: BUY / HOLD / SELL — then 1 sentence reason for experienced investors",
  "beginner_verdict": "One of: BUY / AVOID — then 1 sentence reason for beginners",
  "final_suggestion": "2 sentences final overall summary and suggestion"
}}

LIVE STOCK DATA:
Ticker         : {ticker}
Company        : {company_name}
Sector         : {info.get('sector','N/A')}
Industry       : {info.get('industry','N/A')}
Current Price  : ${price:,.2f}
Today Change   : {'+' if change>=0 else ''}{chg_pct:.2f}%
Week Return    : {week_ret}%
Month Return   : {month_ret}%
RSI (14)       : {rsi_val}
MACD           : {macd_val}
SMA 20         : {sma20}
SMA 50         : {sma50}
SMA 200        : {sma200}
52W High       : {info.get('52w_high','N/A')}
52W Low        : {info.get('52w_low','N/A')}
P/E Ratio      : {info.get('pe_ratio','N/A')}
Market Cap     : {info.get('market_cap','N/A')}
Beta           : {info.get('beta','N/A')}
"""

    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not set in utils/chatbot.py"}

    headers = {"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2000,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Strip potential markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]
        
        return json.loads(raw.strip())
        
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Check your internet."}
    except json.JSONDecodeError:
        return {"error": "AI response could not be parsed. Please try again."}
    except Exception as e:
        err = str(e)
        if "400" in err: return {"error": "Invalid API key. Please check your GEMINI_API_KEY"}
        if "429" in err: return {"error": "Rate limit hit. Please wait a moment and try again."}
        return {"error": f"Analysis failed: {err}"}

def get_chat_response(messages_history: list, user_message: str) -> str:
    """Sends chat history and new message to Gemini API."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY", GEMINI_API_KEY)
    except Exception:
        api_key = GEMINI_API_KEY

    if not api_key: return "Error: GEMINI_API_KEY not set."

    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    gemini_contents = []
    
    gemini_contents.append({
        "role": "user",
        "parts": [{"text": "You are a professional stock market assistant. Use markdown."}]
    })
    gemini_contents.append({
        "role": "model",
        "parts": [{"text": "Understood. How can I help you today?"}]
    })

    for msg in messages_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    gemini_contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "contents": gemini_contents,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"