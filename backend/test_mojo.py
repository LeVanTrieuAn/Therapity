import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def f():
    url = 'https://mapi.mojo.vn/v2/api/status'
    poll_payload = {
        'platform': 'web',
        'index': 'gen-voice',
        'data': {
            'id': '20430010-3c1b-4069-9a68-8faf7f1aa090'
        }
    }
    client = httpx.AsyncClient()
    resp2 = await client.post(url, headers={'Authorization': 'Bearer ' + str(os.getenv('VOICE_GET_API_KEY')), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=poll_payload)
    print("Poll Status (/status):", resp2.status_code)
    print("Poll Response:", resp2.text)

    url2 = 'https://mapi.mojo.vn/v2/api/get'
    resp3 = await client.post(url2, headers={'Authorization': 'Bearer ' + str(os.getenv('VOICE_GET_API_KEY')), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=poll_payload)
    print("Poll Status (/get):", resp3.status_code)
    print("Poll Response:", resp3.text)

asyncio.run(f())
