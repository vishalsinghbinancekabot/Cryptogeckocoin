import requests

def fetch_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,cardano&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print("❌ Error fetching prices:", e)
        return {}
