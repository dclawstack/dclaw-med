"""LLMService — thin async client over OpenRouter.

Surface-area scaffold for the v1.3 "real AI" features (symptom analyzer, SOAP
note generator, triage). Concrete prompts live in ``app.prompts.*`` once they
land; this module just provides the transport.

Behavior:
- If ``settings.openrouter_api_key`` is empty OR env ``MOCK_LLM`` is truthy,
  ``complete()`` / ``json_completion()`` raise ``LLMUnavailable`` so callers
  can fall back to their existing static behavior gracefully.
- Otherwise: POST to OpenRouter chat-completions with timeout + bounded retry.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import httpx

from app.core.config import settings

# Provider URL is overridable via settings.llm_base_url so a local Ollama
# (or any other OpenAI-compatible server) drops in without code changes.
_MAX_ATTEMPTS = 2


class LLMUnavailable(RuntimeError):
    """Raised when the LLM is unconfigured, mocked, or unreachable."""


def _mocked() -> bool:
    if not settings.openrouter_api_key:
        return True
    flag = os.environ.get("MOCK_LLM", "").lower()
    return flag in {"1", "true", "yes", "on"}


async def complete(
    *,
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    timeout: float | None = None,
    response_format: dict[str, Any] | None = None,
) -> str:
    """Plain text completion. Raises ``LLMUnavailable`` if mocked/unconfigured.

    ``response_format`` is passed through to the provider — ``{"type":
    "json_object"}`` constrains the model to emit valid JSON. Supported
    natively by Ollama's OpenAI-compatible endpoint and by most cloud
    providers; ignored harmlessly by ones that don't.
    """
    if _mocked():
        raise LLMUnavailable("LLM is mocked or unconfigured")

    payload: dict[str, Any] = {
        "model": model or settings.llm_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://dclaw-med.local",
        "X-Title": "DClaw Med",
    }

    base_url = settings.llm_base_url.rstrip("/")
    effective_timeout = timeout if timeout is not None else settings.llm_timeout_seconds
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with httpx.AsyncClient(timeout=effective_timeout) as client:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
            last_exc = exc
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(0.5 * attempt)

    raise LLMUnavailable(f"LLM call to {base_url} failed after {_MAX_ATTEMPTS} attempts: {last_exc}")


async def json_completion(
    *,
    system: str,
    user: str,
    schema_hint: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Completion that parses the model's response as JSON.

    ``schema_hint`` is appended to the system prompt so the model knows the
    exact shape we expect. Caller is responsible for validating the parsed
    object against a Pydantic schema.

    Forces provider-native JSON mode via ``response_format``. Caller can
    override by passing ``response_format=None`` (e.g. for providers that
    reject the field) or ``response_format={"type": "..."}``.
    """
    full_system = system
    if schema_hint:
        full_system = (
            f"{system}\n\nReturn ONLY a valid JSON object matching this schema:\n"
            f"{schema_hint}\nNo prose, no markdown fences."
        )
    kwargs.setdefault("response_format", {"type": "json_object"})
    raw = await complete(system=full_system, user=user, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMUnavailable(f"LLM returned invalid JSON: {exc}; raw={raw[:200]!r}") from exc
