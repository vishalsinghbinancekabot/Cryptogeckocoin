import requests

TELEGRAM_TOKEN = "7858591209:AAHuFzy2IDyuH4WRV5FiWQMNb3d--5-vaVs"  # ← replace only if changed
TELEGRAM_CHAT_ID = "<your_chat_id_here>"  # ← replace with real value

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!/'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def send_telegram_message(text):
    escaped_text = escape_markdown(text)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escaped_text,
        "parse_mode": "MarkdownV2"
    }
    try:
        print("🧪 Sending to Telegram:\n", escaped_text)
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Message sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")
        return False

# 💬 Test Message
coin = "LINKUSDT"
interval = "1d"
signal = "SELL"
trade_type = "Swing"
score = 0

message = f"{coin} ({interval})\nSignal: {signal}\nType: {trade_type}\nScore: {score}/100"
send_telegram_message(message)
