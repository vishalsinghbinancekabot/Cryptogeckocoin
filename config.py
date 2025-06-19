# 📁 FILE: config.py

COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "MATICUSDT",
    "ADAUSDT", "XRPUSDT", "DOGEUSDT", "DOTUSDT", "AVAXUSDT",
    "LTCUSDT", "TRXUSDT", "LINKUSDT", "ATOMUSDT", "NEARUSDT",
    "UNIUSDT", "FILUSDT", "AAVEUSDT", "ETCUSDT", "INJUSDT",
    "OPUSDT", "RUNEUSDT", "SANDUSDT", "APTUSDT", "HBARUSDT"
]

INTERVALS = ["5m", "15m", "1h", "1d"]       # Multi-timeframe
CANDLE_LIMIT = 100                         # Past candles to fetch

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

IMAGE_PATH = "chart.png"                   # Chart image file name
CHECK_INTERVAL_SECONDS = 900               # 15 minute signal loop
