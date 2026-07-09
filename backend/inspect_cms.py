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

collections = [
    "users",
    "chat_sessions",
    "diary_entries",
    "diary_folders",
    "aoa_posts",
    "aoa_comments",
    "tasks",
    "cohort_members",
    "cohort_syllabus",
    "analytics_assessments"
]

print("=== INSPECTING CMS COLLECTIONS ===")
for col in collections:
    url = f"{CMS_BASE_URL}/{col}"
    try:
        resp = requests.get(url, headers=headers, params={"limit": 1}, timeout=5)
        print(f"\nCollection: {col} -> Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                print(f"Sample item keys: {list(data[0].keys())}")
                print(f"Sample item details: {data[0]}")
            else:
                print("No data items found.")
        else:
            print(f"Error Body: {resp.text}")
    except Exception as e:
        print(f"Failed to fetch {col}: {e}")
