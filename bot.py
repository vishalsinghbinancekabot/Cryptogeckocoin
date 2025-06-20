import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# ✅ Plain message sender (no markdown)
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text  # No markdown escape needed
        # "parse_mode": None ← default is None
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")
        return False
