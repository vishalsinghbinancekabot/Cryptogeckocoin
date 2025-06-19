VishalX ProBot - Signal Scoring Logic

def get_signal_score(df): latest = df.iloc[-1] score = 0

# RSI
if latest['rsi'] < 35:
    score += 15

# MACD crossover
if latest['macd'] > latest['macd_signal']:
    score += 15

# EMA crossover
if latest['ema12'] > latest['ema26']:
    score += 10

# Supertrend confirmation
if latest['supertrend'] > latest['ema26']:
    score += 10

# ADX strong trend
if latest['adx'] > 25:
    score += 10

# Bollinger Band support zone
if latest['close'] < latest['bb_low']:
    score += 10

# Volume spike
if latest['volume_spike']:
    score += 10

# Additional filter: Price near support and volatility check
if latest['atr'] < (latest['close'] * 0.03):  # less than 3% movement
    score += 5

# Total max: 95
return int(score)

def get_signal_type(score): if score >= 90: return "BUY" elif score <= 20: return "SELL" else: return "HOLD"

