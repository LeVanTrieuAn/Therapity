"""
Therapity — LLM Service
OpenRouter-only client with free Gemini model.
"""

import re
import json
from openai import OpenAI
import httpx
from app.config import get_settings

settings = get_settings()


class LLMService:
    """Manages LLM client via OpenRouter API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=httpx.Timeout(120.0),
            default_headers={
                "HTTP-Referer": "https://therapity.app",
                "X-Title": "Therapity",
            },
        )

        self.default_model = settings.LLM_MODEL
        self.models_to_try = [m.strip() for m in settings.LLM_MODEL.split(",")]

    def _clean_response(self, content: str) -> str:
        """Remove <think> tags and extract clean content."""
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content

    def _extract_json(self, content: str) -> dict | None:
        """Extract JSON from LLM response, handling markdown wrappers."""
        content = self._clean_response(content)
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    def chat_completion(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 3000,
    ) -> tuple[str, str, int]:
        """
        Send a chat completion request via OpenRouter.

        Returns: (content, model_used, tokens_used)
        """
        models = list(self.models_to_try)
        if model and model not in models:
            models.insert(0, model)

        content = ""
        last_error = None
        tokens_used = 0

        for m in models:
            try:
                response = self.client.chat.completions.create(
                    model=m,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                )
                if getattr(response, "choices", None) and len(response.choices) > 0:
                    content = response.choices[0].message.content or ""
                    if getattr(response, "usage", None):
                        tokens_used = response.usage.total_tokens

                if content:
                    return self._clean_response(content), m, tokens_used

            except Exception as e:
                last_error = e
                print(f"⚠️ OpenRouter model {m} failed: {e}")
                continue

        if last_error:
            print(f"❌ All LLM models failed. Last error: {last_error}")
        return "", models[0] if models else "unknown", 0

    def chat_completion_json(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.2,
        **kwargs
    ) -> tuple[dict | None, str, int]:
        """
        Chat completion that returns parsed JSON.

        Returns: (json_dict, model_used, tokens_used)
        """
        content, model_used, tokens = self.chat_completion(
            messages, model=model, temperature=temperature, **kwargs
        )
        if content:
            json_result = self._extract_json(content)
            return json_result, model_used, tokens
        return None, model_used, tokens


# Singleton instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get or create the singleton LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
