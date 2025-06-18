import os
import time
import threading
import requests
import pandas as pd
import numpy as np
import datetime
from flask import Flask
from dotenv import load_dotenv
import telebot

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

bot.send_message(TELEGRAM_CHAT_ID, "✅ Test message from your bot.")
app = Flask(__name__)

COINS = ["bitcoin", "ethereum", "solana", "bnb", "matic-network"]

# --------------------- PRICE FETCH FUNCTION ---------------------
def fetch_price_history(coin_id="bitcoin", days=3):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = [price[1] for price in data["prices"]]

        # 👉 YAHAN PRINT LAGAO
        print(f"📊 {coin_id} fetched {len(prices)} prices.")

        return prices
    except Exception as e:
        print(f"❌ Error fetching data for {coin_id}:", e)
        return []
# --------------------- INDICATOR CALCULATIONS ---------------------
def calculate_rsi(data, period=14):
    series = pd.Series(data)
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(data):
    series = pd.Series(data)
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

def calculate_ema_crossover(data):
    series = pd.Series(data)
    ema9 = series.ewm(span=9, adjust=False).mean()
    ema21 = series.ewm(span=21, adjust=False).mean()
    return ema9.iloc[-1], ema21.iloc[-1]

def calculate_bollinger_bands(data):
    series = pd.Series(data)
    sma = series.rolling(window=20).mean()
    std = series.rolling(window=20).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return upper.iloc[-1], lower.iloc[-1]

# --------------------- ANALYZE & SEND SIGNAL ---------------------
def analyze_market(prices):
    if len(prices) < 26:
        print(f"⚠️ Not enough data | Got only {len(prices)} prices")
        return "⚠️ Not enough data"

    current_price = prices[-1]
    rsi = calculate_rsi(prices)
    macd, signal_line = calculate_macd(prices)
    ema9, ema21 = calculate_ema_crossover(prices)
    upper, lower = calculate_bollinger_bands(prices)

    # 👉 YAHAN PRINT LAGAO
    print(f"🔍 Price: {current_price}, RSI: {rsi:.2f}, MACD: {macd:.2f}, Signal: {signal_line:.2f}")

    if rsi < 30 and macd > signal_line and ema9 > ema21 and current_price < lower:
        return f"💹 STRONG BUY\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"
    elif rsi > 70 and macd < signal_line and ema9 < ema21 and current_price > upper:
        return f"🔻 STRONG SELL\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"
    else:
        return f"⚖️ HOLD\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"

def send_signal():
    print("📡 Signal loop started...")  # ✅ 1. Start indicator
    while True:
        try:
            for coin in COINS:
                prices = fetch_price_history(coin)
                if not prices:
                    print(f"⚠️ No prices for {coin}")
                    continue

                # ✅ 2. Prices check karne ke liye
                print(f"🔍 {coin} prices: {prices[-5:]}")

                signal = analyze_market(prices)

                # ✅ 3. Analyze ke baad kya aaya
                print(f"🧠 Analyzed Signal for {coin}: {signal}")

                # ✅ 4. Always send signal for now
                bot.send_message(TELEGRAM_CHAT_ID, f"📢 {coin.upper()}:\n{signal}")
                print(f"✅ Sent signal for {coin}")
        except Exception as e:
            print("❌ Error in signal loop:", e)
        
        time.sleep(30)  # ✅ 5. Har 1 ghnate me signal check

@app.route('/')
def home():
    return "✅ Bot is running..."

@app.route('/test-signal')
def test_signal():
    output = []
    for coin in COINS:
        prices = fetch_price_history(coin)
        if not prices:
            continue
        signal = analyze_market(prices)
        bot.send_message(TELEGRAM_CHAT_ID, f"🧪 {coin.upper()} Test:\n{signal}")
        output.append(f"{coin}: Sent")
    return "\n".join(output)
   
@app.route('/force-signal/<coin>/<signal_type>')
def force_signal(coin, signal_type):
    signal_type = signal_type.lower()
    if signal_type == "buy":
        signal = f"💹 FORCED BUY SIGNAL\nCoin: {coin.upper()}\nThis is a test buy signal."
    elif signal_type == "sell":
        signal = f"🔻 FORCED SELL SIGNAL\nCoin: {coin.upper()}\nThis is a test sell signal."
    else:
        return "❌ Invalid signal type. Use 'buy' or 'sell'."
    
    bot.send_message(TELEGRAM_CHAT_ID, f"📢 {coin.upper()} SIGNAL:\n{signal}")
    return f"✅ Forced {signal_type.upper()} signal sent for {coin.upper()}"


if __name__ == '__main__':
    print("🚀 Starting bot...")
    threading.Thread(target=send_signal).start()
    app.run(host="0.0.0.0", port=10000)
