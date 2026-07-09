# -*- coding: utf-8 -*-
import sys
sys.path.append('d:/thapsang/backend')
import os
import json
from dotenv import load_dotenv

load_dotenv('d:/thapsang/backend/.env', override=True)

ai_prompt = """You are the Socratic AI Coach of Thapsang Mindset OS.
The user is at Week 1 of their 12-week Personal Roadmap.
Your goal is to deeply analyze their latest dialog history and recent reflective diaries to design EXACTLY 2 highly personalized, high-fidelity tasks for Week 1.
CRITICAL REQUIREMENT: You MUST generate EXACTLY 1 "core" task and EXACTLY 1 "supplementary" task. No more, no less. Do not generate two core tasks. Do not generate two supplementary tasks.

Here is their latest dialog history:
- Chat Session 1: test chat
- Chat Session 2: another test chat

Here are their recent diaries:
No recent diaries found.

Based on this latest actual context, update the tasks for Week 1 to specifically target their current cognitive bottlenecks, blindspots, or goals.
Provide a concise title and description for Week 1, and EXACTLY 2 tasks (the first MUST have type "core", the second MUST have type "supplementary"). Each task must have separate translations: "title_vi", "title_en", "type" (which is strictly "core" or "supplementary"), a personalized detailed Socratic Vietnamese "description_vi", a detailed English "description_en", and a customized "effort" in hours which is an integer from 1 to 4 based on task complexity. IMPORTANT: Inside the task descriptions, if there are numbered lists, steps or bullet points (such as 1), 2), or 1., 2.), you MUST format them on newlines using literal "\\n" so they render clean and beautiful!

You MUST respond with a single, valid JSON object conforming exactly to this JSON schema (do NOT wrap it in any Markdown codeblocks or other formatting, just return raw JSON):
{
  "title_vi": "Tiêu đề tiếng Việt Tuần 1",
  "title_en": "English Week 1 Title",
  "description_vi": "Mô tả tiếng Việt Tuần 1",
  "description_en": "English Week 1 Description",
  "tasks": [
    {
      "title_vi": "Tên nhiệm vụ cốt lõi tiếng Việt",
      "title_en": "Core Task English Title",
      "type": "core",
      "description_vi": "Mô tả chi tiết nhiệm vụ cốt lõi bằng tiếng Việt (xuống dòng cho các mục 1)\\n2))",
      "description_en": "Personalized Socratic core task detailed instruction in English (use newlines for lists or steps)",
      "effort": 3
    },
    {
      "title_vi": "Tên nhiệm vụ bổ trợ tiếng Việt",
      "title_en": "Supplementary Task English Title",
      "type": "supplementary",
      "description_vi": "Mô tả chi tiết nhiệm vụ bổ trợ bằng tiếng Việt",
      "description_en": "Personalized Socratic supplementary task detailed instruction in English",
      "effort": 2
    }
  ]
}
"""

try:
    from openai import OpenAI as _OpenAI
    _client = _OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1')
    )
    model_name = os.getenv('LLM_MODEL', 'thapsang').split(',')[0].strip()
    
    stream_response = _client.chat.completions.create(
        model=model_name,
        messages=[{'role': 'user', 'content': ai_prompt}],
        max_tokens=1024,
        temperature=0.3,
        top_p=0.95,
        stream=True
    )
    chunks = []
    for chunk in stream_response:
        if getattr(chunk, 'choices', None) and chunk.choices[0].delta.content:
            chunks.append(chunk.choices[0].delta.content)
            
    content = "".join(chunks).strip()
    print('Raw response content:', content)
    
    import re
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        content = json_match.group(0)
    
    parsed = json.loads(content)
    print('Successfully parsed JSON!')
except Exception as e:
    import traceback
    print('Failed:', traceback.format_exc())
