VishalX ProBot - Logger for signal history

import csv import os from datetime import datetime

LOG_FILE = "signal_log.csv"

def log_signal(coin, interval, signal_type, trade_type, score): now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") log_exists = os.path.exists(LOG_FILE)

with open(LOG_FILE, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not log_exists:
        writer.writerow(["Time", "Coin", "Interval", "Signal", "TradeType", "Score"])
    writer.writerow([now, coin, interval, signal_type, trade_type, score])
