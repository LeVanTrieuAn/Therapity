import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

CMS_BASE_URL = os.getenv("CMS_BASE_URL", "http://localhost:13000/api")
CMS_API_KEY = os.getenv("CMS_API_KEY")

headers = {
    "Authorization": f"Bearer {CMS_API_KEY}",
    "Content-Type": "application/json"
}

tests = [
    {"where": "(username,eq,non_existent_user_999)"},
    {"where": "username=non_existent_user_999"},
    {"filters[username][$eq]": "non_existent_user_999"},
    {"username": "non_existent_user_999"},
]

print("=== TESTING FILTER SYNTAXES WITH NON-EXISTENT ===")
for i, params in enumerate(tests, 1):
    try:
        resp = requests.get(f"{CMS_BASE_URL}/users", headers=headers, params=params, timeout=5)
        print(f"Test #{i} params: {params} -> Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"  Success! Found {len(data)} items.")
        else:
            print(f"  Error: {resp.status_code}")
    except Exception as e:
        print(f"  Exception: {e}")
