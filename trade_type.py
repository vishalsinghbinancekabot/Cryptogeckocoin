def detect_trade_type(df):
    latest = df.iloc[-1]
    atr = latest['atr']
    close = latest['close']
    atr_percent = (atr / close) * 100

    if atr_percent < 1.2:
        return "Scalping"
    elif atr_percent < 3:
        return "Intraday"
    else:
        return "Swing"

