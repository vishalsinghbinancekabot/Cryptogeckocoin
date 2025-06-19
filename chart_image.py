import pandas as pd
import mplfinance as mpf
import os

def generate_chart(df, symbol, signal):
    # Ensure 'charts/' folder exists
    if not os.path.exists("charts"):
        os.makedirs("charts")

    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

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

    save_path = f"charts/{symbol}_{signal}.png"

    try:
        mpf.plot(
            df_chart,
            type='candle',
            style='yahoo',
            volume=True,
            savefig=dict(fname=save_path, dpi=100, bbox_inches="tight")
        )
        return save_path
    except Exception as e:
        print(f"🛑 Chart generation failed for {symbol}: {e}")
        return None
