import pandas as pd
import ta

def calculate_indicators(df):
    df = df.copy()
    
    # --- Basic Indicators ---
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['macd'] = ta.trend.MACD(df['close']).macd_diff()
    df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()

    # --- SuperTrend ---
    factor = 3
    atr = df['atr']
    hl2 = (df['high'] + df['low']) / 2
    df['supertrend_upper'] = hl2 + (factor * atr)
    df['supertrend_lower'] = hl2 - (factor * atr)
    df['supertrend'] = 'none'
    for i in range(1, len(df)):
        if df['close'][i] > df['supertrend_upper'][i - 1]:
            df.loc[i, 'supertrend'] = 'buy'
        elif df['close'][i] < df['supertrend_lower'][i - 1]:
            df.loc[i, 'supertrend'] = 'sell'
        else:
            df.loc[i, 'supertrend'] = df['supertrend'][i - 1]

    # --- Volume Spike ---
    df['vol_spike'] = df['volume'] > (df['volume'].rolling(20).mean() * 1.5)

    return df.dropna()
