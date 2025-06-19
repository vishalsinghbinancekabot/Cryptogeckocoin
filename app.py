import os
import time
import requests
import threading
from flask import Flask
from dotenv import load_dotenv
import telebot
import pandas as pd

load_dotenv()

print("🛠️ Bot Loaded!")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)


COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "polygon"]

last_fetch_time = {}

# ✅ Should Fetch Logic
def should_fetch(coin):
    now = time.time()
    if coin not in last_fetch_time or now - last_fetch_time[coin] > 3600:
        last_fetch_time[coin] = now
        return True
    return False

# ✅ Fetch Current Price
def fetch_current_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; TelegramBot/1.0)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"🔗 Fetching {coin_id}: {url}")
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")

        data = response.json()
        return data[coin_id]["usd"]
    except Exception as e:
        print(f"❌ Error fetching price for {coin_id}: {e}")
        return None

# ✅ Fetch Price History
def fetch_price_history(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
        response = requests.get(url)
        data = response.json()

        print(f"📡 API URL: {url}")
        print(f"📦 API Response: {data}")

        if "prices" not in data:
            print(f"⚠️ 'prices' key not in API response for {coin_id}")
            return []

        prices = [price[1] for price in data["prices"]]
        print(f"✅ Fetched {len(prices)} prices for {coin_id}")
        return prices
    except Exception as e:
        print(f"❌ Error fetching price history for {coin_id}: {e}")
        return []
        
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

# ✅ Analyze Market
def analyze_market(prices):
    if len(prices) < 26:
        print(f"⚠️ Not enough data | Got only {len(prices)} prices")
        return "⚠️ Not enough data"

    current_price = prices[-1]
    rsi = calculate_rsi(prices)
    macd, signal_line = calculate_macd(prices)
    ema9, ema21 = calculate_ema_crossover(prices)
    upper, lower = calculate_bollinger_bands(prices)

    print(f"🔍 Price: {current_price}, RSI: {rsi:.2f}, MACD: {macd:.2f}, Signal: {signal_line:.2f}")

    # ✅ PRICE-BASED SIGNAL LOGIC
    if current_price > 70000:
        return f"🔴 PRICE ALERT | SELL {current_price:.2f} > 70000\nRSI: {rsi:.2f}, MACD: {macd:.2f}"
    elif current_price < 60000:
        return f"🟢 PRICE ALERT | BUY {current_price:.2f} < 60000\nRSI: {rsi:.2f}, MACD: {macd:.2f}"

    # ✅ INDICATOR-BASED STRATEGY
    if rsi < 30 and macd > signal_line and ema9 > ema21 and current_price < lower:
        return f"💹 STRONG BUY\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"
    elif rsi > 70 and macd < signal_line and ema9 < ema21 and current_price > upper:
        return f"🔻 STRONG SELL\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"
    else:
        return f"⚖️ HOLD\nRSI: {rsi:.2f}, MACD: {macd:.2f}, Price: ${current_price:.2f}"

# ✅ Signal Sending Thread
def send_signal():
    print("📡 Signal loop started...")
    while True:
        for coin in COINS:
            if not should_fetch(coin):
                continue
            prices = fetch_price_history(coin)
            if not prices:
                continue
            signal = analyze_market(prices)
            bot.send_message(TELEGRAM_CHAT_ID, f"📢 {coin.upper()} Signal:\n{signal}")
        time.sleep(150)  # wait 1 hour

# ✅ Routes
@app.route('/')
def home():
    return "✅ Bot is running..."
    
@app.route('/test-signal')
def test_signal():
    output = []
    for coin in COINS:
        try:
            print(f"🧪 Testing {coin}...")
            prices = fetch_price_history(coin)
            if not prices:
                output.append(f"{coin}: ❌ No prices")
                continue
            signal = analyze_market(prices)
            print(f"📤 Sending signal for {coin}: {signal}")
            bot.send_message(TELEGRAM_CHAT_ID, f"🧪 {coin.upper()} Test:\n{signal}")
            output.append(f"{coin}: ✅ Sent")
        except Exception as e:
            print(f"❌ Error in {coin}: {e}")
            output.append(f"{coin}: ❌ Error")
    return "<br>".join(output)

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

# ✅ Launch Bot
if __name__ == '__main__':
    print("🚀 Starting bot...")
    threading.Thread(target=send_signal).start()
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
