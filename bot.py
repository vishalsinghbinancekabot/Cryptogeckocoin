import requests
import re
import os
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# ✅ MarkdownV2 escaping function
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
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

# ✅ Image sender
def send_telegram_image(caption, image_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        # 🛑 Check if image exists and is not empty
        if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
            print(f"🛑 Chart not found or empty: {image_path}")
            return False

        escaped_caption = escape_markdown(caption)
        print(f"📤 Sending image: {image_path}")
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': escaped_caption,
                'parse_mode': 'MarkdownV2'
            }
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"❌ Failed to send image: {e}")
        return False
