from fastapi.testclient import TestClient
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from backend.main import app

client = TestClient(app)

payload = {
    "username": "test_qa_runner",
    "messages": [
        {"role": "model", "content": "Welcome user. What is on your mind?"},
        {"role": "user", "content": "I am feeling stuck"}
    ]
}

response = client.post("/api/v1/chat", json=payload)
print(response.status_code)
print(response.text)
