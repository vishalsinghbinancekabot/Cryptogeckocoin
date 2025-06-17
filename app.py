import os
import time
from threading import Thread
from flask import Flask
import os
import requests
from dotenv import load_dotenv
import telebot
from strategy import analyze_market
from utils import fetch_prices

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Crypto Signal Bot is Running..."

# ✅ Ye function abhi ek baar signal bhejega
def send_test_signal():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    message = "🧪 Test Signal: Bot is working and connected to Telegram!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    print("✅ Test signal sent! Response:", response.text)
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_signal():
    while True:
        try:
            prices = fetch_prices()
            signal = analyze_market(prices)
            if signal != "HOLD":
                bot.send_message(chat_id, f"📢 Signal: {signal}")
            else:
                print("No clear signal yet.")
        except Exception as e:
            print("Error in signal loop:", e)
        time.sleep(3600)  # every 1 hour

@app.route('/')
def home():
    return "✅ Crypto Signal Bot is Running..."

    # ✅ App run hone se pehle ek baar signal bhejo
send_test_signal()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    Thread(target=send_signal).start()
    app.run(host="0.0.0.0", port=10000)
