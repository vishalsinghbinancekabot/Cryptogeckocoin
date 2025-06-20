import os
import requests
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def escape_markdown(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN or CHAT_ID missing")
        return False

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
        print("✅ Message sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print("❌ Failed to send message:")
        print("➡️", e.response.text)
        return False
