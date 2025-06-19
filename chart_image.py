import mplfinance as mpf
import pandas as pd
import os

def generate_chart(df, coin, signal_type, save_path="chart.png"):
    df_chart = df.copy()
    df_chart.index = pd.to_datetime(df_chart['timestamp'], unit='ms')

    df_chart = df_chart[['open', 'high', 'low', 'close', 'volume']]
    df_chart.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    ema12 = df['ema12']
    ema26 = df['ema26']

    apds = [
        mpf.make_addplot(ema12, color='cyan'),
        mpf.make_addplot(ema26, color='magenta')
    ]

    title = f"{coin} - Signal: {signal_type}"

    mpf.plot(
        df_chart,
        type='candle',
        style='yahoo',
        title=title,
        ylabel='Price (USDT)',
        volume=True,
        addplot=apds,
        savefig=dict(fname=save_path, dpi=100, bbox_inches="tight")
    )

    return os.path.exists(save_path)
