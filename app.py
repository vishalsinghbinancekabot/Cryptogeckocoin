import requests
import numpy as np
from telegram import Bot
import time
import os

# 🔧 ENV VARIABLES (add these in environment or manually set)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

# ✅ Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
INTERVAL = "1h"
LIMIT = 100

# 🟡 Fetch historical klines
def get_klines(symbol, interval, limit):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    close_prices = [float(candle[4]) for candle in data]
    return close_prices

# 🧠 EMA Calculation
def calculate_ema(prices, period):
    prices = np.array(prices)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(prices, weights, mode='full')[:len(prices)]
    return a[-1]

# 🧠 RSI Calculation
def calculate_rsi(prices, period=14):
    prices = np.array(prices)
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0).mean()
    loss = -np.where(delta < 0, delta, 0).mean()
    if loss == 0:
        return 100
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🧠 MACD Calculation
def calculate_macd(prices):
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    return ema12 - ema26

# 🧠 Bollinger Bands
def calculate_bollinger(prices, period=20):
    prices = np.array(prices[-period:])
    sma = np.mean(prices)
    std = np.std(prices)
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper, lower

# 📊 Signal Analysis
def analyze(prices):
    signals = []

    # RSI
    rsi = calculate_rsi(prices)
    if rsi < 30:
        signals.append("RSI: 🔼 Buy")
    elif rsi > 70:
        signals.append("RSI: 🔽 Sell")

    # MACD
    macd = calculate_macd(prices)
    if macd > 0:
        signals.append("MACD: 🔼 Buy")
    else:
        signals.append("MACD: 🔽 Sell")

    # EMA Crossover
    ema10 = calculate_ema(prices, 10)
    ema20 = calculate_ema(prices, 20)
    if ema10 > ema20:
        signals.append("EMA: 🔼 Buy")
    else:
        signals.append("EMA: 🔽 Sell")

    # Bollinger Band
    upper, lower = calculate_bollinger(prices)
    if prices[-1] < lower:
        signals.append("Bollinger: 🔼 Buy")
    elif prices[-1] > upper:
        signals.append("Bollinger: 🔽 Sell")

    return signals

# 🚀 Main logic
def run_bot():
    for symbol in SYMBOLS:
        try:
            prices = get_klines(symbol, INTERVAL, LIMIT)
            signals = analyze(prices)
            buy_count = sum("Buy" in s for s in signals)
            sell_count = sum("Sell" in s for s in signals)

            if buy_count >= 3:
                msg = f"✅ *BUY Signal for {symbol}*\n" + "\n".join(signals)
            elif sell_count >= 3:
                msg = f"⚠️ *SELL Signal for {symbol}*\n" + "\n".join(signals)
            else:
                msg = f"ℹ️ *Hold for {symbol}*\n" + "\n".join(signals)

            print(msg)
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

# 🔁 Run every hour
while True:
    run_bot()
    time.sleep(3600)  # run every 1 hour
