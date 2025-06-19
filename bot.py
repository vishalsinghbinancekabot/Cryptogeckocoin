import os
import re
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def escape_markdown(text):
    return re.sub(r'([\*_`])', r'\\\1', text)

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

def send_telegram_image(caption, image_path):
    print(f"📤 Sending image: {image_path}")
    if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
        print(f"❌ Image file missing or empty: {image_path}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': escape_markdown(caption),
                'parse_mode': 'MarkdownV2'
            }
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"❌ Failed to send image: {e}")
        return False
