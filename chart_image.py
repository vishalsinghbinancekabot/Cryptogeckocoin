import pandas as pd
import mplfinance as mpf

def generate_chart(df, symbol, signal):
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # ❗️Check if data is empty after cleaning
    if df.empty or len(df) < 10:
        print(f"⚠️ Not enough data to generate chart for {symbol}. Skipping...")
        return None

    df_chart = pd.DataFrame({
        'Open': df['open'],
        'High': df['high'],
        'Low': df['low'],
        'Close': df['close'],
        'Volume': df['volume']
    }, index=pd.DatetimeIndex(df.index))

    save_path = f"{symbol}_{signal}.png"
    mpf.plot(
        df_chart,
        type='candle',
        style='yahoo',
        volume=True,
        savefig=dict(fname=save_path, dpi=100, bbox_inches="tight")
    )
    return save_path
