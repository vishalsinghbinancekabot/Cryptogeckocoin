import os

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

# === IMPORTS ===
import time
import requests
import pandas as pd
import ta

# === TELEGRAM BOT ===
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!/'
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
    latest = df.iloc[-1]
    if latest['rsi'] < 30:
        score += 10
    elif latest['rsi'] > 70:
        score -= 10
    if latest['macd'] > 0:
        score += 10
    else:
        score -= 10
    if latest['ema_fast'] > latest['ema_slow']:
        score += 10
    else:
        score -= 10
    if latest['adx'] > 25:
        score += 10
    if latest['close'] < latest['bb_lower']:
        score += 5
    elif latest['close'] > latest['bb_upper']:
        score -= 5
    return max(0, min(100, score))

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

def format_signal_message(coin, interval, signal, trade_type, score, price):
    r_percent = 2
    t_percent = 3
    if signal == "BUY":
        sl = round(price * (1 - r_percent / 100), 4)
        target = round(price * (1 + t_percent / 100), 4)
    elif signal == "SELL":
        sl = round(price * (1 + r_percent / 100), 4)
        target = round(price * (1 - t_percent / 100), 4)
    else:
        return f"ℹ️ HOLD Signal for {coin} ({interval})\nConfidence: {score}/100"
    return f"""✅ {signal} Signal for {coin} ({interval})
💰 Entry Price: {price}
🎯 Target Price: {target} (+{t_percent}%)
🛡️ Stop Loss: {sl} (-{r_percent}%)
📊 Confidence Score: {score}/100
📌 Trade Type: {trade_type}"""

# === FETCH DATA FROM BINANCE ===
def fetch_ohlcv(symbol, interval, limit):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","x","n","taker","b","q","ignore"])
    df = df[["o","h","l","c"]].astype(float)
    df.columns = ["open", "high", "low", "close"]
    return df

# === BOT RUNNER ===
def run_bot():
    while True:
        for coin in COINS:
            for interval in INTERVALS:
                try:
                    print(f"Checking {coin} @ {interval}...")
                    df = fetch_ohlcv(coin, interval, CANDLE_LIMIT)
                    df = calculate_indicators(df)
                    score = get_signal_score(df)
                    signal = get_signal_type(score)
                    trade_type = detect_trade_type(interval)
                    price = df['close'].iloc[-1]                    
  if score >= 70:
    signal_type = signal
    entry_price = price
    stop_loss = round(price * 0.98, 2)
    target_price = round(price * 1.03, 2)

    message = format_signal_message(
        coin,
        interval,
        signal_type,
        score,
        trade_type,
        entry_price,
        stop_loss,
        target_price
    )
    send_telegram_message(message)
    
# === START ===
if __name__ == "__main__":
    run_bot()
