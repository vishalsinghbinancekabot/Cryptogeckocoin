import os
import time
import requests
import pandas as pd
import ta

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing! Please set them in environment.")

COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT",
    "AVAXUSDT", "TRXUSDT", "LINKUSDT", "MATICUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "ATOMUSDT",
    "NEARUSDT", "XLMUSDT", "FILUSDT", "ETCUSDT", "SANDUSDT", "MANAUSDT", "EOSUSDT", "AAVEUSDT",
    "GRTUSDT", "ALGOUSDT", "RUNEUSDT", "XTZUSDT", "THETAUSDT", "CAKEUSDT", "FTMUSDT", "KAVAUSDT",
    "CRVUSDT", "1INCHUSDT", "COMPUSDT", "ZECUSDT", "ENJUSDT", "SNXUSDT", "CHZUSDT", "APEUSDT",
    "OPUSDT", "ARBUSDT", "INJUSDT", "DYDXUSDT", "GMXUSDT", "RNDRUSDT", "LDOUSDT", "TWTUSDT"
]
INTERVALS = ["5m", "15m", "1h", "1d"]
CANDLE_LIMIT = 100
CHECK_INTERVAL_SECONDS = 1800  # every 30 mins
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# === TELEGRAM BOT ===
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def send_telegram_message(text):
    escaped = escape_markdown(text)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escaped,
        "parse_mode": "MarkdownV2"
    }
    try:
        print("Sending:\n", escaped)
        r = requests.post(url, json=payload)
        r.raise_for_status()
        print("Message sent")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

# === INDICATOR CALCULATIONS ===
def calculate_indicators(df):
    df = df.copy()
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['macd'] = ta.trend.MACD(df['close']).macd_diff()
    df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
    return df.dropna()

# === STRATEGY ===
def get_signal_score(df):
    score = 0
    reasons = []
    latest = df.iloc[-1]
    if latest['rsi'] < 30:
        score += 10
        reasons.append("RSI below 30 (Oversold)")
    elif latest['rsi'] > 70:
        score -= 10
        reasons.append("RSI above 70 (Overbought)")
    if latest['macd'] > 0:
        score += 10
        reasons.append("MACD positive crossover")
    else:
        score -= 10
        reasons.append("MACD negative")
    if latest['ema_fast'] > latest['ema_slow']:
        score += 10
        reasons.append("EMA Fast > EMA Slow")
    else:
        score -= 10
        reasons.append("EMA Fast < EMA Slow")
    if latest['adx'] > 25:
        score += 10
        reasons.append("Strong trend (ADX > 25)")
    if latest['close'] < latest['bb_lower']:
        score += 5
        reasons.append("Close below Bollinger Band")
    elif latest['close'] > latest['bb_upper']:
        score -= 5
        reasons.append("Close above Bollinger Band")
    return max(0, min(100, score)), reasons

def get_signal_type(score):
    if score >= 70:
        return "BUY"
    elif score <= 30:
        return "SELL"
    return "HOLD"

def detect_trade_type(interval):
    if interval in ["5m", "15m"]:
        return "Scalping"
    elif interval == "1h":
        return "Intraday"
    return "Swing"

def format_signal_message(coin, interval, signal, score, trade_type, price, reasons):
    r_percent = 2
    t_percent = 3
    sl = target = None

    if signal == "BUY":
        sl = round(price * (1 - r_percent / 100), 4)
        target = round(price * (1 + t_percent / 100), 4)
    elif signal == "SELL":
        sl = round(price * (1 + r_percent / 100), 4)
        target = round(price * (1 - t_percent / 100), 4)

    confidence_bar = "█" * (score // 10) + "░" * (10 - score // 10)
    reason_text = "\n".join(reasons)

    return f"""🚨 {signal} SIGNAL – {coin} ({interval})
💰 Price: {price}
🎯 Target: {target}
🛡️ Stop Loss: {sl}
📌 Trade Type: {trade_type}

📊 Confidence: {score}/100
[{confidence_bar}]
🧠 Reasons:
{reason_text}
"""

# === FETCH DATA FROM BINANCE ===
def fetch_ohlcv(symbol, interval, limit):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    data = r.json()

    if not isinstance(data, list):
        print(f"❌ Error in API response for {symbol} @ {interval}: {data}")
        return None

    try:
        df = pd.DataFrame(data, columns=[
            "t", "o", "h", "l", "c", "v",
            "x", "n", "taker", "b", "q", "ignore"
        ])
        df = df[["o", "h", "l", "c", "v"]].astype(float)
        df.columns = ["open", "high", "low", "close", "volume"]
        return df
    except Exception as e:
        print(f"❌ Data parsing error for {symbol} @ {interval}: {e}")
        return None

# === BOT RUNNER ===
def run_bot():
    while True:
        for coin in COINS:
            for interval in INTERVALS:
                try:
                    print(f"Checking {coin} @ {interval}...")
                    df = fetch_ohlcv(coin, interval, CANDLE_LIMIT)

                    # ✅ Error fix: empty ya none response skip karo
                    if df is None or df.empty:
                        print(f"⚠️ Skipping {coin} @ {interval} due to empty/error data")
                        continue

                    df = calculate_indicators(df)
                    score, reasons = get_signal_score(df)  # ✅ yahan error fix hua
                    signal = get_signal_type(score)
                    trade_type = detect_trade_type(interval)
                    price = df['close'].iloc[-1]

                    print(f"{coin} @ {interval} → Score: {score} → Signal: {signal}")

                    latest = df.iloc[-1]
                    if latest['adx'] < 15:
                        print(f"❌ Flat Market (ADX {latest['adx']}), skipping...")
                        continue
        
        message = format_signal_message(
    coin,
    interval,
    signal,
    score,
    trade_type,
    price,
    reasons
)

if score >= 50:
    send_telegram_message(message)
    time.sleep(1.2)
else:
    print(f"❌ Skipped {coin} @ {interval} due to low confidence ({score})")


                except Exception as e:
                    print(f"Error checking {coin} @ {interval}: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

# === START ===
if __name__ == "__main__":
    run_bot()
