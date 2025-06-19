📁 FILE: main.py

VishalX ProBot - Main Controller Script

import time import requests import pandas as pd from config import COINS, INTERVALS, CANDLE_LIMIT, CHECK_INTERVAL_SECONDS from indicators import calculate_indicators from strategy import get_signal_score, get_signal_type from trade_type import detect_trade_type from chart_image import generate_chart from bot import send_telegram_message, send_telegram_image from logger import log_signal

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_candles(symbol, interval): params = { "symbol": symbol, "interval": interval, "limit": CANDLE_LIMIT } try: response = requests.get(BINANCE_URL, params=params) data = response.json() df = pd.DataFrame(data, columns=[ 'timestamp', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6' ]) df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']] df['timestamp'] = df['timestamp'].astype(int) return df except Exception as e: print(f"❌ Error fetching data for {symbol}: {e}") return None

def process(): for coin in COINS: for interval in INTERVALS: print(f"🔍 Checking {coin} @ {interval}...") df = fetch_candles(coin, interval) if df is None or df.empty: continue

df = calculate_indicators(df)
        score = get_signal_score(df)
        signal_type = get_signal_type(score)
        trade_type = detect_trade_type(df)

        if signal_type in ["BUY", "SELL"]:
            generate_chart(df, coin, signal_type)
            caption = f"*{coin}* ({interval})\n📊 Signal: *{signal_type}*\n⚡ Type: {trade_type}\n🎯 Score: {score}/100"
            send_telegram_image(caption)
            log_signal(coin, interval, signal_type, trade_type, score)

def run(): while True: print("🚀 Running VishalX ProBot signal check...") process() print(f"⏳ Waiting {CHECK_INTERVAL_SECONDS} seconds...\n") time.sleep(CHECK_INTERVAL_SECONDS)

if name == "main": run()
