import requests
import re
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

#def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!%:'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

# ✅ Message sender
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escape_markdown(text),
        "parse_mode": "MarkdownV2"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")
        return False
