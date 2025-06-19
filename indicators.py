import pandas as pd
import ta

def calculate_indicators(df):
    # Ensure float conversion
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)

    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], fillna=False).rsi()

    # MACD
    macd = ta.trend.MACD(df['close'], fillna=False)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # EMA crossover
    df['ema12'] = ta.trend.EMAIndicator(df['close'], window=12, fillna=False).ema_indicator()
    df['ema26'] = ta.trend.EMAIndicator(df['close'], window=26, fillna=False).ema_indicator()

    # SuperTrend proxy (STC)
    df['supertrend'] = ta.trend.STCIndicator(df['close'], fillna=False).stc()

    # ADX
    adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], fillna=False)
    df['adx'] = adx.adx()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['close'], fillna=False)
    df['bb_low'] = bb.bollinger_lband()
    df['bb_high'] = bb.bollinger_hband()

    # ATR
    atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], fillna=False)
    df['atr'] = atr.average_true_range()

    # Volume Spike
    df['volume_avg'] = df['volume'].rolling(window=20).mean()
    df['volume_spike'] = df['volume'] > (1.5 * df['volume_avg'])

    # Drop any rows with NaN values created by indicators
    df.dropna(inplace=True)

    # Extra safety: return None if too few rows remain
    if df.empty or len(df) < 10:
        print("⚠️ Indicator result: insufficient clean data after dropna.")
        return None

    return df
