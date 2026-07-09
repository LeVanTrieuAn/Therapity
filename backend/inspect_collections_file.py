import os
import requests
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

CMS_BASE_URL = os.getenv("CMS_BASE_URL", "http://localhost:13000/api")
CMS_API_KEY = os.getenv("CMS_API_KEY")

headers = {
    "Authorization": f"Bearer {CMS_API_KEY}",
    "Content-Type": "application/json"
}

try:
    resp = requests.get(f"{CMS_BASE_URL}/collections", headers=headers, timeout=5)
    with open("collections.json", "w", encoding="utf-8") as f:
        json.dump(resp.json(), f, ensure_ascii=False, indent=4)
    print("Successfully wrote collections.json")
except Exception as e:
    print("Failed:", e)
