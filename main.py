import os
import time
import requests
import pandas as pd
import ta

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing! Please set them in environment.")

COINS = [
    # 🔹 Mega Caps
    "ADAUSDT", "AVAXUSDT", "BNBUSDT", "BTCUSDT", "DOGEUSDT", "DOTUSDT", "ETHUSDT", "LINKUSDT", "LTCUSDT", "MATICUSDT",
    "NEARUSDT", "SHIBUSDT", "SOLUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "XRPUSDT", "ATOMUSDT", "ETCUSDT", "LUNAUSDT",

    # 🔸 Layer-1 & Layer-2
    "ALGOUSDT", "ANKRUSDT", "APTUSDT", "ARBUSDT", "BSCUSDT", "CELRUSDT", "CSPRUSDT", "ELFUSDT", "FETUSDT", "GRTUSDT",
    "ICPUSDT", "KAVAUSDT", "KLAYUSDT", "MINAUSDT", "OPUSDT", "RUNEUSDT", "STXUSDT", "SUIUSDT", "XNOUSDT", "ZILUSDT",

    # 🧠 DeFi / Yield
    "1INCHUSDT", "AAVEUSDT", "BALUSDT", "BNTUSDT", "COMPUSDT", "CRVUSDT", "DYDXUSDT", "FTMUSDT", "INJUSDT", "LDOUSDT",
    "MKRUSDT", "PENDLEUSDT", "RAYUSDT", "SNXUSDT", "SXPUSDT", "UMAUSDT", "YFIUSDT",

    # 🎮 NFT / Metaverse
    "APEUSDT", "AXSUSDT", "CHZUSDT", "ENJUSDT", "GALAUSDT", "ILVUSDT", "LOKAUSDT", "MANAUSDT", "RNDRUSDT", "SANDUSDT",
    "SLPUSDT", "SUSHIUSDT",

    # ⚡ High-risk / high-return altcoins
    "ARDRUSDT", "AVAXUSDT", "BYNUSDT", "BTGUSDT", "COTIUSDT", "DASHUSDT", "ETCUSDT", "FILUSDT", "HNSUSDT", "KSMUSDT",
    "OCEANUSDT", "PHAUSDT", "QTUMUSDT", "RVNUSDT", "SCUSDT", "SYSUSDT", "XDCUSDT", "XTZUSDT", "ZECUSDT", "ZRXUSDT",

    # 🚀 Meme & Viral Tokens
    "BONKUSDT", "FLOKIUSDT", "GALUSDT", "HATIUSDT", "KOISHIUSDT", "NOTUSDT", "PEPEUSDT", "POLUSDT", "SNOUSDT", "WIFUSDT",

    # 🔬 Oracles, AI, Narrative
    "AGIXUSDT", "API3USDT", "ARNXUSDT", "DIAUSDT", "HIGHUSDT", "HOOKUSDT", "IDUSDT", "IQUSDT", "LINKUSDT", "NMRUSDT",
    "SSVUSDT", "TRBUSDT",

    # 🌐 Infra / Web3 / Middleware
    "ARUSDT", "BANDUSDT", "CVCUSDT", "CTSIUSDT", "CTXTUSDT", "FIDAUSDT", "POWRUSDT", "REQUSDT", "STORJUSDT", "THETAUSDT",

    # 🔄 Payments / CBDC
    "DBUSDT", "EOSUSDT", "GRTUSDT", "M GROUSDT", "QLCUSDT", "STRAXUSDT", "USDNUSDT", "VETUSDT", "XNOUSDT",

    # 🛠️ Emerging / Misc
    "ACHUSDT", "BICOUSDT", "BRZUSDT", "CELOUSDT", "CLVUSDT", "COTIUSDT", "FIROUSDT", "FORTHUSDT", "HNTUSDT", "HODLUSDT",
    "LPTUSDT", "MASKUSDT", "MERUSDT", "MLKUSDT", "NKNUSDT", "PLAUSDT", "PNUTUSDT", "POLUSDT", "PUNDIXUSDT", "PSGUSDT",
    "SLPUSDT", "SRMUSDT", "STMXUSDT", "TRIBEUSDT", "TRUUSDT", "WNXMUSDT", "ZILUSDT"
]
COINS = list(set(COINS))  # Duplicate hata dega

INTERVALS = ["5m", "15m", "1h", "1d"]
CANDLE_LIMIT = 100
CHECK_INTERVAL_SECONDS = 1800  # every 30 mins
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# === TELEGRAM BOT ===
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def send_telegram_message(text):
    escaped = escape_markdown(text)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escaped,
        "parse_mode": "MarkdownV2"
    }
    try:
        print("Sending:\n", escaped)
        r = requests.post(url, json=payload)
        r.raise_for_status()
        print("Message sent")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

# === INDICATOR CALCULATIONS ===
def calculate_indicators(df):
    df = df.copy()
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['macd'] = ta.trend.MACD(df['close']).macd_diff()
    df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()

    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()

    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()

    # === ✅ SuperTrend Calculation ===
    factor = 3
    atr = df['atr']
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + (factor * atr)
    lowerband = hl2 - (factor * atr)

    supertrend = []
    in_uptrend = True

    for i in range(len(df)):
        if i == 0:
            supertrend.append(in_uptrend)
            continue

        if df['close'].iloc[i] > upperband.iloc[i - 1]:
            in_uptrend = True
        elif df['close'].iloc[i] < lowerband.iloc[i - 1]:
            in_uptrend = False

        supertrend.append(in_uptrend)

    df['supertrend'] = ['buy' if val else 'sell' for val in supertrend]

    return df.dropna()

# === STRATEGY ===

def estimate_target_success(confidence, adx, atr, volume_spike):
    base = confidence / 100
    if adx > 40:
        base += 0.10
    elif adx > 25:
        base += 0.05
    if atr > 0:
        base += 0.05
    if volume_spike:
        base += 0.05
    return max(min(round(base * 100), 95), 10)
    
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

def get_signal_score(df):
    score = 0
    reasons = []
    latest = df.iloc[-1]

    # RSI Analysis
    if latest['rsi'] < 20:
        score += 20
        reasons.append("🔥 RSI < 20 (Very Oversold)")
    elif latest['rsi'] < 30:
        score += 15
        reasons.append("✅ RSI < 30 (Oversold)")
    elif latest['rsi'] > 80:
        score -= 20
        reasons.append("❌ RSI > 80 (Very Overbought)")
    elif latest['rsi'] > 70:
        score -= 10
        reasons.append("⚠️ RSI > 70 (Overbought)")

    # MACD
    if latest['macd'] > 0:
        score += 15
        reasons.append("✅ MACD bullish crossover")
    else:
        score -= 10
        reasons.append("❌ MACD bearish")

    # EMA Crossover
    if latest['ema_fast'] > latest['ema_slow']:
        score += 10
        reasons.append("✅ EMA Fast > Slow (Bullish)")
    else:
        score -= 10
        reasons.append("❌ EMA Fast < Slow (Bearish)")

    # ADX (trend strength)
    if latest['adx'] > 40:
        score += 15
        reasons.append("🔥 Strong trend (ADX > 40)")
    elif latest['adx'] > 25:
        score += 10
        reasons.append("✅ Moderate trend (ADX > 25)")
    elif latest['adx'] < 15:
        score -= 10
        reasons.append("❌ No trend (ADX < 15)")

    # Bollinger Band breakout
    if latest['close'] < latest['bb_lower']:
        score += 10
        reasons.append("✅ Close below lower BB (Buy Zone)")
    elif latest['close'] > latest['bb_upper']:
        score -= 10
        reasons.append("❌ Close above upper BB (Sell Zone)")

    # ATR breakout (volatility expansion)
    if df['close'].iloc[-1] - df['close'].iloc[-2] > latest['atr']:
        score += 5
        reasons.append("✅ Price > ATR range (Momentum breakout)")

    # Volume Spike
    avg_vol = df['volume'].iloc[-20:].mean()
    if latest['volume'] > 1.5 * avg_vol:
        score += 10
        reasons.append("✅ Volume Spike Detected")

    # SuperTrend (must be added in indicators)
    if 'supertrend' in latest and latest['supertrend'] == 'buy':
        score += 15
        reasons.append("✅ SuperTrend: Buy Signal")
    elif 'supertrend' in latest and latest['supertrend'] == 'sell':
        score -= 15
        reasons.append("❌ SuperTrend: Sell Signal")

    avg_vol = df['volume'].iloc[-20:].mean()
    volume_spike = latest['volume'] > 1.5 * avg_vol

    hit_chance = estimate_target_success(score, latest['adx'], latest['atr'], volume_spike)
    return max(0, min(100, score)), reasons, hit_chance, latest['atr']
    
def get_signal_type(score):
    if score >= 70:
        return "BUY"
    elif score <= 30:
        return "SELL"
    return "HOLD"

def detect_trade_type(interval):
    if interval in ["5m", "15m"]:
        return "Scalping"
    elif interval == "1h":
        return "Intraday"
    return "Swing"

def format_signal_message(coin, interval, signal, score, trade_type, price, reasons, hit_chance, atr): 
    r_mult = 1.5
    t_mult = 2.5
    sl = target = None

    if signal == "BUY":
        sl = round(price - (r_mult * atr), 4)
        target = round(price + (t_mult * atr), 4)
    elif signal == "SELL":
        sl = round(price + (r_mult * atr), 4)
        target = round(price - (t_mult * atr), 4)

    confidence_bar = "█" * (score // 10) + "░" * (10 - score // 10)
    reason_text = "\n".join(reasons)

    return f"""🚨 {signal} SIGNAL – {coin} ({interval})
💰 Price: {price}
🎯 Target: {target} (🎯 Likely: {hit_chance}%)
🛡️ Stop Loss: {sl}
📌 Trade Type: {trade_type}

📊 Confidence: {score}/100
[{confidence_bar}]
🧠 Reasons:
{reason_text}
"""

# === FETCH DATA FROM BINANCE ===
def fetch_ohlcv(symbol, interval, limit):
    url = f"{BINANCE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    data = r.json()

    if not isinstance(data, list):
        print(f"❌ Error in API response for {symbol} @ {interval}: {data}")
        return None

    try:
        df = pd.DataFrame(data, columns=[
            "t", "o", "h", "l", "c", "v",
            "x", "n", "taker", "b", "q", "ignore"
        ])
        df = df[["o", "h", "l", "c", "v"]].astype(float)
        df.columns = ["open", "high", "low", "close", "volume"]
        return df
    except Exception as e:
        print(f"❌ Data parsing error for {symbol} @ {interval}: {e}")
        return None

# === BOT RUNNER ===
def run_bot():
    while True:
        for interval in INTERVALS:
            message_block = f"🕒 *Timeframe: {interval.upper()} Signals*\n\n"
            count = 0

            for coin in COINS:
                try:
                    print(f"Checking {coin} @ {interval}...")
                    df = fetch_ohlcv(coin, interval, CANDLE_LIMIT)

                    if df is None or df.empty:
                        print(f"⚠️ Skipping {coin} @ {interval} due to empty/error data")
                        continue

                    df = calculate_indicators(df)
                    score, reasons, hit_chance, atr = get_signal_score(df)
                    signal = get_signal_type(score)
                    trade_type = detect_trade_type(interval)
                    price = df['close'].iloc[-1]

                    print(f"{coin} @ {interval} → Score: {score} → Signal: {signal}")

                    latest = df.iloc[-1]
                    if latest['adx'] < 15:
                        print(f"❌ Flat Market (ADX {latest['adx']}), skipping...")
                        continue

                    if signal in ["BUY", "SELL"] and score >= 50:
                        message = format_signal_message(
                            coin, interval, signal, score, trade_type, price, reasons, hit_chance, atr
                        )
                        message_block += message + "\n\n"
                        count += 1

                    elif signal == "HOLD" and score >= 50:
                        sl = round(price - (1.5 * atr), 4)
                        target = round(price + (2.5 * atr), 4)
                        confidence_bar = "█" * (score // 10) + "░" * (10 - score // 10)
                        reason_text = "\n".join(reasons)

                        message = f"""ℹ️ HOLD Signal – {coin} ({interval})
💰 Price: {price}
🎯 Target: {target}
🛡️ Stop Loss: {sl}
📌 Trade Type: {trade_type}

📊 Confidence: {score}/100  
[{confidence_bar}]
📈 Hit Chance: {hit_chance}%

🧠 Reasons:
{reason_text}

📎 *Note: This is a HOLD signal (Not yet confirmed). Wait for stronger confirmation before taking a trade.*
"""
                        message_block += message + "\n\n"
                        count += 1

                    else:
                        print(f"❌ Skipped {coin} @ {interval} – Signal: {signal}, Score: {score}")

                except Exception as e:
                    print(f"⚠️ Error processing {coin} @ {interval}: {e}")

            # ✅ Send 1 grouped message for this interval
            if count > 0:
                send_telegram_message(message_block)
                time.sleep(3)  # Optional pause between timeframes
            else:
                print(f"⚠️ No valid signals for {interval}")

        time.sleep(CHECK_INTERVAL_SECONDS)
        
# === START ===
if __name__ == "__main__":
    run_bot()
