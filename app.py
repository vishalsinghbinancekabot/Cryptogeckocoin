import requests
import numpy as np
from telegram import Bot
import time
import os
import asyncio

# 🔧 ENV VARIABLES (from Render.com env settings)
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

# 🚀 Main logic (now async)
async def run_bot():
    for symbol in SYMBOLS:
        try:
            prices = get_klines(symbol, INTERVAL, LIMIT)
            signals = analyze(prices)
            buy_count = sum("Buy" in s for s in signals)
            sell_count = sum("Sell" in s for s in signals)

            entry_price = round(prices[-1], 2)
            target_price = round(entry_price * 1.03, 2)
            stop_loss = round(entry_price * 0.98, 2)

            if buy_count >= 3:
                msg = f"""✅ *BUY Signal for {symbol}*
💰 Entry Price: ${entry_price}
🎯 Target Price: ${target_price} (+3%)
🛡️ Stop Loss: ${stop_loss} (-2%)

📊 Indicators:
{chr(10).join(signals)}
"""
            elif sell_count >= 3:
                sell_target = round(entry_price * 0.97, 2)
                sell_stop = round(entry_price * 1.02, 2)
                msg = f"""⚠️ *SELL Signal for {symbol}*
💰 Entry Price: ${entry_price}
🎯 Target Price: ${sell_target} (-3%)
🛡️ Stop Loss: ${sell_stop} (+2%)

📊 Indicators:
{chr(10).join(signals)}
"""
            else:
                msg = f"""ℹ️ *HOLD Signal for {symbol}*
💰 Entry Price: ${entry_price}
🎯 Suggested Watch Target: ${target_price} (+3%)
🛡️ Suggested Stop Monitor: ${stop_loss} (-2%)

📊 Indicators:
{chr(10).join(signals)}
"""

            print(msg)
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")

# 🔁 Loop every 1 hour
async def main():
    while True:
        await run_bot()
        await asyncio.sleep(3600)  # 1 hour delay

# 🟢 Run the bot
if __name__ == "__main__":
    asyncio.run(main())
