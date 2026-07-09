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
display_name = "Lê An"

print(f"Starting simulated join_cohort_endpoint for {username}...")

# 1. Gather context
chats = cms_helper.get_chat_sessions(username)
diaries = cms_helper.get_diary_entries(username)
assessments = cms_helper.get_analytics_assessments(username)

chats_list = list(chats.values())
chats_text = ""
for idx, c in enumerate(chats_list[:3]):
    msgs = c.get("chat_history") or c.get("messages") or []
    chat_content = " ".join([m.get("content", "") for m in msgs[-5:] if m.get("content")])
    chats_text += f"- Chat Session {idx+1} '{c.get('custom_title') or c.get('id')}': {chat_content[:800]}\n"

diaries_text = ""
for idx, d in enumerate(diaries[:3]):
    diaries_text += f"- Diary {idx+1} '{d.get('title')}': {d.get('content')[:800]}\n"
    
assessments_text = ""
for a in assessments:
    assessments_text += f"- Decision Quality: {a.get('decisionQualityScore')}, Mindset Retention: {a.get('mindsetRetentionScore')}\n"

ai_prompt = f"""You are the Socratic AI Coach of Thapsang Mindset OS (PDCA Level 2).
The user "{display_name}" (username: {username}) has triggered the AI Personal Roadmap Allocation.
"""

try:
    from openai import OpenAI as _OpenAI
    print("Connecting to OpenAI base_url:", os.getenv("LLM_BASE_URL"))
    _client = _OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://llmapi.digiforce.vn/v1")
    )
    model_name = os.getenv("LLM_MODEL", "thapsang").split(",")[0].strip()
    print("Using model:", model_name)
    
    resp = _client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": ai_prompt}],
        max_tokens=2048,
        temperature=0.7,
        top_p=0.9,
    )
    print("Raw response object:", type(resp), resp)
    ai_response_text = resp.choices[0].message.content.strip()
    print("LLM raw response length:", len(ai_response_text))
    
except Exception as e:
    print("Allocation error:")
    traceback.print_exc()
