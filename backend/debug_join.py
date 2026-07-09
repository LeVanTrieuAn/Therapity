import os
import requests
import json
import sys
from dotenv import load_dotenv
import traceback

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"d:\thapsang\backend"
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

sys.path.append(BASE_DIR)

import cms_helper

username = "trieuan3499@gmail.com"
print(f"Testing Socratic personal roadmap task creation for {username}...")

try:
    task_data = {
        "title": "Debug Test Task",
        "week": 1,
        "status": "in_progress",
        "goal": "Test if NocoBase POST personal_roadmaps works.",
        "type": "core",
        "subtasks": [
            {"title": "Step 1", "done": False}
        ],
        "effort": 2
    }
    res = cms_helper.create_personal_roadmap_task(username, task_data)
    print("Creation Response:", res)
    
except Exception as e:
    print("Creation Error:")
    traceback.print_exc()
