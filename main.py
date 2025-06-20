✅ config.py

TELEGRAM_TOKEN = "your_telegram_bot_token" TELEGRAM_CHAT_ID = "your_telegram_chat_id"

COINS = ["BTCUSDT", "ETHUSDT", "LINKUSDT", "TRXUSDT"] INTERVALS = ["5m", "15m", "1h", "1d"]

CANDLE_LIMIT = 100 CHECK_INTERVAL_SECONDS = 900  # 15 minutes BINANCE_URL = "https://api.binance.com/api/v3/klines"

✅ bot.py

import requests

def escape_markdown(text): escape_chars = r'_*~`>#+-=|{}.!/' return ''.join(['\' + c if c in escape_chars else c for c in text])

def send_telegram_message(text): from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID escaped = escape_markdown(text) url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" payload = { "chat_id": TELEGRAM_CHAT_ID, "text": escaped, "parse_mode": "MarkdownV2" } try: print("🧪 Sending:\n", escaped) r = requests.post(url, json=payload) r.raise_for_status() print("✅ Message sent") return True except Exception as e: print(f"❌ Failed: {e}") return False

✅ indicators + strategy + runner (main logic)

import time import pandas as pd import ta

from config import COINS, INTERVALS, BINANCE_URL, CANDLE_LIMIT, CHECK_INTERVAL_SECONDS from bot import send_telegram_message

def calculate_indicators(df): df = df.copy() df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi() df['macd'] = ta.trend.MACD(df['close']).macd_diff() df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator() df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator() df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx() bb = ta.volatility.BollingerBands(df['close']) df['bb_upper'] = bb.bollinger_hband() df['bb_lower'] = bb.bollinger_lband() df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range() return df.dropna()

def get_signal_score(df): score = 0 latest = df.iloc[-1] if latest['rsi'] < 30: score += 10 elif latest['rsi'] > 70: score -= 10 if latest['macd'] > 0: score += 10 else: score -= 10 if latest['ema_fast'] > latest['ema_slow']: score += 10 else: score -= 10 if latest['adx'] > 25: score += 10 if latest['close'] < latest['bb_lower']: score += 5 elif latest['close'] > latest['bb_upper']: score -= 5 return max(0, min(100, score))

def get_signal_type(score): if score >= 70: return "BUY" elif score <= 30: return "SELL" return "HOLD"

def detect_trade_type(interval): if interval in ["5m", "15m"]: return "Scalping" elif interval == "1h": return "Intraday" return "Swing"

def format_signal_message(coin, interval, signal, trade_type, score, price): r_percent = 2 t_percent = 3 if signal == "BUY": sl = round(price * (1 - r_percent / 100), 4) target = round(price * (1 + t_percent / 100), 4) elif signal == "SELL": sl = round(price * (1 + r_percent / 100), 4) target = round(price * (1 - t_percent / 100), 4) else: return f"ℹ️ HOLD Signal for {coin} ({interval})\nConfidence: {score}/100" return f"""✅ {signal} Signal for {coin} ({interval}) 💰 Entry Price: {price} 🎯 Target Price: {target} (+{t_percent}%) 🛡️ Stop Loss: {sl} (-{r_percent}%) 📊 Confidence Score: {score}/100 📌 Trade Type: {trade_type}"""

def fetch_ohlcv(symbol, interval, limit): url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}" r = requests.get(url) data = r.json() df = pd.DataFrame(data, columns=["t","o","h","l","c","v","x","n","taker","b","q","ignore"]) df = df[["o","h","l","c"]].astype(float) df.columns = ["open", "high", "low", "close"] return df

def run_bot(): while True: for coin in COINS: for interval in INTERVALS: try: print(f"🔍 {coin} @ {interval}") df = fetch_ohlcv(coin, interval, CANDLE_LIMIT) df = calculate_indicators(df) score = get_signal_score(df) signal = get_signal_type(score) trade_type = detect_trade_type(interval) price = df['close'].iloc[-1] message = format_signal_message(coin, interval, signal, trade_type, score, price) send_telegram_message(message) except Exception as e: print(f"❌ {coin}@{interval} Error: {e}") time.sleep(CHECK_INTERVAL_SECONDS)

if name == "main": run_bot()


