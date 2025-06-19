# --- Coin & Timeframe Settings ---
COINS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "MATICUSDT",
    "ADAUSDT", "XRPUSDT", "DOGEUSDT", "DOTUSDT", "AVAXUSDT",
    "LTCUSDT", "TRXUSDT", "LINKUSDT", "ATOMUSDT", "NEARUSDT",
    "UNIUSDT", "FILUSDT", "AAVEUSDT", "ETCUSDT", "INJUSDT",
    "OPUSDT", "RUNEUSDT", "SANDUSDT", "APTUSDT", "HBARUSDT"
]
INTERVALS = ["5m", "15m", "1h", "1d"]       # Timeframes for analysis
CANDLE_LIMIT = 100                         # Number of candles to fetch per request

# --- Telegram Bot Credentials ---
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# --- Chart Config ---
IMAGE_PATH = "chart.png"                   # Path to save chart image

# --- Bot Loop Timing ---
CHECK_INTERVAL_SECONDS = 900               # 15 minutes = 900 seconds
