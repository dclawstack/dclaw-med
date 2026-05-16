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

_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_TIMEOUT = 30.0
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
    timeout: float = _DEFAULT_TIMEOUT,
) -> str:
    """Plain text completion. Raises ``LLMUnavailable`` if mocked/unconfigured."""
    if _mocked():
        raise LLMUnavailable("LLM is mocked or unconfigured")

    payload = {
        "model": model or settings.llm_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://dclaw-med.local",
        "X-Title": "DClaw Med",
    }

    last_exc: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{_BASE_URL}/chat/completions",
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

    raise LLMUnavailable(f"OpenRouter call failed after {_MAX_ATTEMPTS} attempts: {last_exc}")


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
    """
    full_system = system
    if schema_hint:
        full_system = (
            f"{system}\n\nReturn ONLY a valid JSON object matching this schema:\n"
            f"{schema_hint}\nNo prose, no markdown fences."
        )
    raw = await complete(system=full_system, user=user, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMUnavailable(f"LLM returned invalid JSON: {exc}; raw={raw[:200]!r}") from exc
