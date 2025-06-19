# 📁 FILE: indicators.py

import pandas as pd
import ta

def calculate_indicators(df):
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)

    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

    # MACD
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # EMA crossover
    df['ema12'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
    df['ema26'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()

    # SuperTrend (using STC as proxy)
    df['supertrend'] = ta.trend.STCIndicator(df['close'], fillna=True).stc()

    # ADX
    adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'])
    df['adx'] = adx.adx()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_low'] = bb.bollinger_lband()
    df['bb_high'] = bb.bollinger_hband()

    # ATR
    atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'])
    df['atr'] = atr.average_true_range()

    # Volume Spike
    df['volume_avg'] = df['volume'].rolling(window=20).mean()
    df['volume_spike'] = df['volume'] > (1.5 * df['volume_avg'])

    return df
