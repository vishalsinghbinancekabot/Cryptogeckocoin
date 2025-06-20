strategy.py

def get_signal_score(df): latest = df.iloc[-1] score = 0

if latest['rsi'] < 35:
    score += 15
if latest['macd'] > latest['macd_signal']:
    score += 15
if latest['ema12'] > latest['ema26']:
    score += 10
if latest['supertrend'] > latest['ema26']:
    score += 10
if latest['adx'] > 25:
    score += 10
if latest['close'] < latest['bb_low']:
    score += 10
if latest['volume_spike']:
    score += 10
if latest['atr'] < (latest['close'] * 0.03):
    score += 5

return int(score)

def get_signal_type(score): if score >= 90: return "BUY" elif score <= 20: return "SELL" else: return "HOLD"

def calculate_entry_targets(signal_type, close_price): if signal_type == "BUY": entry = close_price target = round(close_price * 1.03, 2)  # +3% stop_loss = round(close_price * 0.98, 2)  # -2% elif signal_type == "SELL": entry = close_price target = round(close_price * 0.97, 2)  # -3% stop_loss = round(close_price * 1.02, 2)  # +2% else: entry = target = stop_loss = close_price return entry, target, stop_loss

def format_signal_message(symbol, interval, signal_type, trade_type, score, entry, target, stop_loss): msg = ( f"\u2705 {signal_type} Signal for {symbol} ({interval})\n" f"\U0001F4B0 Entry Price: ${entry}\n" f"\U0001F3AF Target: ${target}\n" f"\U0001F6E1\uFE0F Stop Loss: ${stop_loss}\n\n" f"\U0001F4CA Indicators Confidence: {score}/100\n" f"\U0001F4C8 Trade Type: {trade_type}" ) return msg

