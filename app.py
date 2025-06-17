import os
import time
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
import telebot
import requests
import pandas as pd
import numpy as np
import datetime

# ✅ Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Telegram bot init
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# ✅ Coins list
COINS = ["bitcoin", "ethereum", "solana", "bnb", "matic-network"]

# ✅ Fetch price history
def fetch_price_history(coin_id="bitcoin", days=2):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "hourly"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        return prices
    except Exception as e:
        print(f"❌ Error fetching data for {coin_id}:", e)
        return []

# ✅ 24h Price change
def fetch_price_change_24h(coin_id="bitcoin"):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data[coin_id]["usd_24h_change"]
    except Exception as e:
        print(f"❌ Error fetching 24h change for {coin_id}:", e)
        return 0

# ✅ Indicators
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
    ema_short = series.ewm(span=9, adjust=False).mean()
    ema_long = series.ewm(span=21, adjust=False).mean()
    return ema_short.iloc[-1], ema_long.iloc[-1]

def calculate_bollinger_bands(data):
    series = pd.Series(data)
    sma = series.rolling(window=20).mean()
    std = series.rolling(window=20).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return upper_band.iloc[-1], lower_band.iloc[-1]

# ✅ Signal generation
def analyze_market(prices):
    if len(prices) < 26:
        return "⚠️ Not enough data."

    current_price = prices[-1]
    rsi = calculate_rsi(prices)
    macd, signal_line = calculate_macd(prices)
    ema9, ema21 = calculate_ema_crossover(prices)
    upper_band, lower_band = calculate_bollinger_bands(prices)

    if (rsi < 30 and macd > signal_line and ema9 > ema21 and current_price < lower_band):
        return f"💹 STRONG BUY\nRSI: {rsi:.2f}, MACD: {macd:.2f}, EMA9: {ema9:.2f}, Price: ${current_price:.2f}"
    elif (rsi > 70 and macd < signal_line and ema9 < ema21 and current_price > upper_band):
        return f"🔻 STRONG SELL\nRSI: {rsi:.2f}, MACD: {macd:.2f}, EMA9: {ema9:.2f}, Price: ${current_price:.2f}"
    else:
        return f"⚖️ HOLD\nRSI: {rsi:.2f}, MACD: {macd:.2f}, EMA9: {ema9:.2f}, Price: ${current_price:.2f}"

# ✅ Auto signal loop
def send_signal():
    print("✅ DEBUG | Signal loop started...")
    while True:
        try:
            for coin in COINS:
                print(f"📊 Checking: {coin}")
                prices = fetch_price_history(coin)
                print("✅ DEBUG | Prices fetched:", prices[-5:])
                signal = analyze_market(prices)
                print("✅ DEBUG | Signal detected:", signal)
                if "BUY" in signal or "SELL" in signal:
                    bot.send_message(CHAT_ID, f"📢 {coin.upper()} Signal:\n{signal}")
                    print("📤 Sent to Telegram")
                else:
                    print("🟡 HOLD — No action taken")
                time.sleep(5)
        except Exception as e:
            print("❌ Error in signal loop:", e)
        time.sleep(1800)  # Every 30 minutes

# ✅ Daily summary at 8 AM
def daily_summary():
    while True:
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute < 5:
            summary = ["🗓️ DAILY SUMMARY"]
            for coin in COINS:
                try:
                    prices = fetch_price_history(coin)
                    if prices:
                        signal = analyze_market(prices)
                        change = fetch_price_change_24h(coin)
                        summary.append(f"📍 {coin.upper()}:\n{signal}\n🔁 24h Change: {change:.2f}%")
                except Exception as e:
                    summary.append(f"{coin.upper()}: ❌ Error in summary")
            bot.send_message(CHAT_ID, "\n\n".join(summary))
            time.sleep(300)
        time.sleep(60)

# ✅ Flask endpoints
@app.route('/')
def home():
    return "✅ Multi-Coin Bot Running"

@app.route('/test-signal')
def test_signal():
    output = []
    for coin in COINS:
        prices = fetch_price_history(coin)
        if prices:
            signal = analyze_market(prices)
            change = fetch_price_change_24h(coin)
            bot.send_message(CHAT_ID, f"🧪 {coin.upper()} Test:\n{signal}\n🔁 24h Change: {change:.2f}%")
            output.append(f"{coin}: ✅")
    return "✅ Test signals sent."

# ✅ Start everything
if __name__ == "__main__":
    Thread(target=send_signal).start()
    Thread(target=daily_summary).start()
    app.run(host="0.0.0.0", port=10000)
