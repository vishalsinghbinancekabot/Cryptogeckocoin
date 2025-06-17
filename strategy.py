import numpy as np

def calculate_rsi(prices, period=14):
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    ema12 = np.mean(prices[-12:])
    ema26 = np.mean(prices[-26:])
    return ema12 - ema26

def calculate_ema(prices, period=9):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return np.convolve(prices, weights, mode='valid')[-1]

def analyze_market(prices):
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    ema = calculate_ema(prices)

    last_price = prices[-1]

    if rsi < 30 and macd > 0 and last_price > ema:
        return "BUY 📈"
    elif rsi > 70 and macd < 0 and last_price < ema:
        return "SELL 📉"
    else:
        return "HOLD ⏸️"
