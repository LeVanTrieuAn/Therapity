import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("backend/.env")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
)

try:
    print("Testing 'thapsang' model...")
    response = client.chat.completions.create(
        model="thapsang",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.2
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()
