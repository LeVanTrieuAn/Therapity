import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

CMS_BASE_URL = os.getenv("CMS_BASE_URL", "https://thapsang.digiforce.vn/api")
CMS_API_KEY = os.getenv("CMS_API_KEY")

headers = {
    "Authorization": f"Bearer {CMS_API_KEY}",
    "Content-Type": "application/json"
}

try:
    resp = requests.get(f"{CMS_BASE_URL}/collections", headers=headers, timeout=5)
    print("=== COLLECTIONS DATA ===")
    print(resp.json())
except Exception as e:
    print("Failed collections:", e)

# Also check root URL headers
try:
    resp = requests.get("https://thapsang.digiforce.vn", timeout=5)
    print("\n=== HEADERS ===")
    for k, v in resp.headers.items():
        print(f"{k}: {v}")
except Exception as e:
    print("Failed headers:", e)
