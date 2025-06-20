def get_signal_score(df):
    score = 0
    reasons = []
    latest = df.iloc[-1]

    # RSI
    if latest['rsi'] < 30:
        score += 15
        reasons.append("🟢 RSI Oversold (+15)")
    elif latest['rsi'] > 70:
        score -= 15
        reasons.append("🔴 RSI Overbought (-15)")
    elif 30 <= latest['rsi'] <= 40:
        score += 7
        reasons.append("🟢 RSI Weak Buy (+7)")
    elif 60 <= latest['rsi'] <= 70:
        score -= 7
        reasons.append("🔴 RSI Weak Sell (-7)")

    # MACD
    if latest['macd'] > 0:
        score += 15
        reasons.append("🟢 MACD Bullish (+15)")
    else:
        score -= 15
        reasons.append("🔴 MACD Bearish (-15)")

    # EMA
    if latest['ema_fast'] > latest['ema_slow']:
        score += 15
        reasons.append("🟢 EMA Crossover (+15)")
    else:
        score -= 15
        reasons.append("🔴 EMA Bearish (-15)")

    # ADX
    if latest['adx'] > 25:
        score += 10
        reasons.append("📈 ADX > 25 (+10)")
    if latest['adx'] > 40:
        score += 5
        reasons.append("🚀 ADX > 40 (+5)")

    # Bollinger Bands
    if latest['close'] < latest['bb_lower']:
        score += 10
        reasons.append("🟢 BB Lower Bounce (+10)")
    elif latest['close'] > latest['bb_upper']:
        score -= 10
        reasons.append("🔴 BB Upper Breakout (-10)")

    # Volume Spike (Safe)
    if 'vol_spike' in latest and latest['vol_spike']:
        score += 10
        reasons.append("💥 Volume Spike (+10)")

    # SuperTrend (Safe)
    if 'supertrend' in latest:
        if latest['supertrend'] == "buy":
            score += 10
            reasons.append("🟢 SuperTrend BUY (+10)")
        elif latest['supertrend'] == "sell":
            score -= 10
            reasons.append("🔴 SuperTrend SELL (-10)")

    # ATR Compression
    if latest['atr'] < df['atr'].mean() * 0.9:
        score += 5
        reasons.append("🌀 Low Volatility Setup (+5)")

    return max(0, min(100, score)), reasons
