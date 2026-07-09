from openai.resources.chat.completions import AsyncCompletions, Completions
from openai import AsyncOpenAI, OpenAI
from cms_helper import get_active_llm_config, sync_active_model_to_cms
import asyncio
import os
import threading
import httpx
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

_original_async_create = AsyncCompletions.create
_original_sync_create = Completions.create

# Khởi tạo client riêng cho OpenRouter nếu có API Key
or_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_sync_client = None
openrouter_async_client = None
if or_api_key:
    openrouter_sync_client = OpenAI(
        api_key=or_api_key,
        base_url="https://openrouter.ai/api/v1",
        timeout=httpx.Timeout(500.0)
    )
    openrouter_async_client = AsyncOpenAI(
        api_key=or_api_key,
        base_url="https://openrouter.ai/api/v1",
        timeout=httpx.Timeout(500.0)
    )

# Gán cứng model ở đây
ACTIVE_MODEL = "thapsang_2"

def _sync_cms():
    sync_active_model_to_cms(ACTIVE_MODEL)
threading.Thread(target=_sync_cms).start()

def _apply_dynamic_kwargs(kwargs):
    config = get_active_llm_config()

    kwargs["model"] = ACTIVE_MODEL
        
    if config.get("max_tokens") is not None:
        kwargs["max_tokens"] = config["max_tokens"]
    if config.get("temperature") is not None:
        kwargs["temperature"] = config["temperature"]
    if config.get("top_p") is not None:
        kwargs["top_p"] = config["top_p"]
    if config.get("top_k"):
        extra = kwargs.get("extra_body", {})
        extra["top_k"] = config["top_k"]
        kwargs["extra_body"] = extra
    if config.get("stream") is not None:
        if "stream" in kwargs:
            kwargs["stream"] = config["stream"]
            
    if ACTIVE_MODEL == "thapsang":
        kwargs.pop("reasoning_effort", None)

    return kwargs

class FakeMessage:
    def __init__(self, content):
        self.content = content

class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)

class FakeChatCompletion:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]

async def patched_async_create(self, *args, **kwargs):
    kwargs = _apply_dynamic_kwargs(kwargs)
    model = kwargs.get("model", "").lower()
    
    if ("nex" in model or "openrouter" in model) and openrouter_async_client:
        target_client = openrouter_async_client.chat.completions
    else:
        target_client = self

    original_stream = kwargs.get("stream", False)
    if "thapsang_2" in model:
        kwargs["stream"] = True

    try:
        resp = await _original_async_create(target_client, *args, **kwargs)
        
        if kwargs.get("stream") and not original_stream:
            content_parts = []
            reasoning_parts = []
            async for chunk in resp:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    r_c = getattr(delta, 'reasoning_content', None)
                    c_c = getattr(delta, 'content', None)
                    if r_c: reasoning_parts.append(r_c)
                    if c_c: content_parts.append(c_c)
            final_content = ""
            if reasoning_parts:
                final_content += f"<think>\n{''.join(reasoning_parts)}\n</think>\n"
            final_content += "".join(content_parts)
            return FakeChatCompletion(final_content)
            
        return resp
    except Exception as e:
        status_code = getattr(e, 'status_code', None)
        if status_code and status_code >= 500 and kwargs.get("model") == "thapsang_2":
            print(f"[LLM_PATCHER] Error {status_code}. Falling back to thapsang...")
            fallback_kwargs = kwargs.copy()
            fallback_kwargs["model"] = "thapsang"
            fallback_kwargs.pop("reasoning_effort", None)
            fallback_kwargs["stream"] = original_stream # Revert stream flag for fallback
            return await _original_async_create(target_client, *args, **fallback_kwargs)
        raise e

def patched_sync_create(self, *args, **kwargs):
    kwargs = _apply_dynamic_kwargs(kwargs)
    model = kwargs.get("model", "").lower()
    
    if ("nex" in model or "openrouter" in model) and openrouter_sync_client:
        target_client = openrouter_sync_client.chat.completions
    else:
        target_client = self

    original_stream = kwargs.get("stream", False)
    if "thapsang_2" in model:
        kwargs["stream"] = True

    try:
        resp = _original_sync_create(target_client, *args, **kwargs)
        
        if kwargs.get("stream") and not original_stream:
            content_parts = []
            reasoning_parts = []
            for chunk in resp:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    r_c = getattr(delta, 'reasoning_content', None)
                    c_c = getattr(delta, 'content', None)
                    if r_c: reasoning_parts.append(r_c)
                    if c_c: content_parts.append(c_c)
            final_content = ""
            if reasoning_parts:
                final_content += f"<think>\n{''.join(reasoning_parts)}\n</think>\n"
            final_content += "".join(content_parts)
            return FakeChatCompletion(final_content)
            
        return resp
    except Exception as e:
        status_code = getattr(e, 'status_code', None)
        if status_code and status_code >= 500 and kwargs.get("model") == "thapsang_2":
            print(f"[LLM_PATCHER] Error {status_code}. Falling back")
            fallback_kwargs = kwargs.copy()
            fallback_kwargs["model"] = "thapsang"
            fallback_kwargs.pop("reasoning_effort", None)
            fallback_kwargs["stream"] = original_stream # Revert stream flag for fallback
            return _original_sync_create(target_client, *args, **fallback_kwargs)
        raise e

# Apply patches
AsyncCompletions.create = patched_async_create
Completions.create = patched_sync_create

print("[LLM_PATCHER] OpenAI Completions classes patched to use dynamic CMS configuration.")
