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

# In directus, fields can be queried via /fields or /relations
# Let's try some metadata URLs
meta_urls = [
    "/fields",
    "/relations",
    "/collections"
]

for murl in meta_urls:
    try:
        resp = requests.get(f"{CMS_BASE_URL}{murl}", headers=headers, timeout=5)
        print(f"URL: {murl} -> Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"Total items: {len(data)}")
            if data:
                # print some items
                for item in data[:10]:
                    if isinstance(item, dict):
                        # Filter for thapsang specific collections
                        col = item.get("collection")
                        if col and col in ["users", "chat_sessions", "diary_entries", "diary_folders", "aoa_posts", "aoa_comments", "tasks", "cohort_members", "cohort_syllabus", "analytics_assessments"]:
                            print(item)
    except Exception as e:
        print(f"Failed {murl}: {e}")
