import time
import requests
import pandas as pd

from config import COINS, INTERVALS, CANDLE_LIMIT, CHECK_INTERVAL_SECONDS
from indicators import calculate_indicators
from strategy import get_signal_score, get_signal_type
from trade_type import detect_trade_type
from chart_image import generate_chart
from bot import send_telegram_message, send_telegram_image
from logger import log_signal

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_candles(symbol, interval):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": CANDLE_LIMIT
    }
    try:
        response = requests.get(BINANCE_URL, params=params)
        if response.status_code != 200:
            print(f"❌ Failed API for {symbol}: HTTP {response.status_code}")
            return None
        
        data = response.json()
        if not data or not isinstance(data, list):
            print(f"❌ Empty or invalid response for {symbol}")
            return None

        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            '_1', '_2', '_3', '_4', '_5', '_6'
        ])
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(inplace=True)

        if df.empty or len(df) < 10:
            print(f"⚠️ Not enough valid data for {symbol}")
            return None

        return df

    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return None

def process():
    for coin in COINS:
        for interval in INTERVALS:
            print(f"🔍 Checking {coin} @ {interval}...")
            df = fetch_candles(coin, interval)
            if df is None or df.empty:
                continue

            try:
                df = calculate_indicators(df)
                df.dropna(inplace=True)

                score = get_signal_score(df)
                signal_type = get_signal_type(score)
                trade_type = detect_trade_type(df)

                if signal_type in ["BUY", "SELL"]:
                    chart_path = generate_chart(df, coin, signal_type)
                    if chart_path:
                        caption = f"*{coin}* ({interval})\n📊 Signal: *{signal_type}*\n⚡ Type: {trade_type}*\n🎯 Score: {score}/100"
                        send_telegram_image(caption, chart_path)
                        log_signal(coin, interval, signal_type, trade_type, score)
                    else:
                        print(f"⛔ Chart not sent for {coin} due to invalid data.")
                else:
                    print(f"ℹ️ No strong signal for {coin} ({score}/100)")
            except Exception as e:
                print(f"❌ Error processing {coin}@{interval}: {e}")


def run():
    while True:
        print("🚀 Running VishalX ProBot signal check...")
        process()
        print(f"⏳ Waiting {CHECK_INTERVAL_SECONDS} seconds...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run()
