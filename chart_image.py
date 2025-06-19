def generate_chart(df, symbol, signal_type):
    import io
    import mplfinance as mpf

    df_chart = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    # ✅ Convert to float
    df_chart["Open"] = pd.to_numeric(df_chart["Open"], errors="coerce")
    df_chart["High"] = pd.to_numeric(df_chart["High"], errors="coerce")
    df_chart["Low"] = pd.to_numeric(df_chart["Low"], errors="coerce")
    df_chart["Close"] = pd.to_numeric(df_chart["Close"], errors="coerce")
    df_chart["Volume"] = pd.to_numeric(df_chart["Volume"], errors="coerce")

    # ✅ Remove rows with NaN after conversion
    df_chart.dropna(inplace=True)

    df_chart.index.name = 'Date'

    # ✅ Save to buffer (for Telegram) OR path (for saving)
    buf = io.BytesIO()
    mpf.plot(
        df_chart,
        type="candle",
        style="yahoo",
        volume=True,
        savefig=dict(fname=buf, dpi=100, bbox_inches="tight")
    )
    buf.seek(0)
    return buf
