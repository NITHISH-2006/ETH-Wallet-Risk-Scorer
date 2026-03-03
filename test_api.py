import requests
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("ETHERSCAN_API_KEY")
address = "0x28c6c06298d514db089934071355e5743bf21d60"  # Binance hot wallet

url = "https://api.etherscan.io/v2/api"  
params = {
    "module": "account",
    "action": "txlist",
    "address": address,
    "startblock": 0,
    "endblock": 99999999,
    "sort": "asc",
    "apikey": key,
    "page": 1,
    "offset": 10,  # small for test
    "chainid": "1"
}

response = requests.get(url, params=params)
data = response.json()

print("Status code:", response.status_code)
print("Full response:", data)

if data.get("status") == "1":
    print("Success! Transactions found:", len(data["result"]))
else:
    print("Error message:", data.get("message", "Unknown"))