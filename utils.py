import requests

def fetch_prices(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
        response = requests.get(url)
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        return prices
    except Exception as e:
        print("Error fetching prices:", e)
        return []
