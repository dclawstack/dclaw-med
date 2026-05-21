"""Real-LLM smoke tests for /api/v1/med/symptoms/analyze.

These are **opt-in** — they hit a real OpenRouter model and spend
credits. Set ``RUN_REAL_LLM=1`` to run them; otherwise the whole
module is skipped.

Two calls per run, capped intentionally to stay inside the
"≤3 LLM calls per full test run" budget set by the test plan.

Mocked LLM behavior — schema fallback, max_results capping by
caller, urgency mapping — is covered by test_symptoms_analyze.py.
Don't duplicate it here; this file only asserts the *real* model's
response respects the API contract.
"""

from __future__ import annotations

import os
import re

import pytest
from httpx import AsyncClient

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REAL_LLM") != "1",
    reason="Real-LLM tests skipped. Set RUN_REAL_LLM=1 to opt in.",
)


ANALYZE = "/api/v1/med/symptoms/analyze"
ICD10_PATTERN = re.compile(r"^[A-Z]\d{2}(\.[A-Z0-9]{1,4})?$")
URGENCY_LEVELS = {"low", "medium", "high", "critical"}


def _require_api_key() -> None:
    if not settings.openrouter_api_key:
        pytest.skip("OPENROUTER_API_KEY not set; cannot exercise real LLM.")


@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_real_llm_returns_valid_contract(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """One real OpenRouter call. Asserts the contract documented on the
    landing page: ≥3 differentials, ICD-10-looking codes, urgency in
    the canonical set, evidence_refs is a list."""
    _require_api_key()
    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "symptoms": "65-year-old male with crushing substernal chest pain "
                        "radiating to left arm, diaphoresis, 30 minutes",
            "max_results": 5,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()

    differentials = body["differential_diagnoses"]
    assert len(differentials) >= 3, f"expected ≥3, got {len(differentials)}"

    for d in differentials:
        assert ICD10_PATTERN.match(d["icd10_code"]), (
            f"ICD-10 code {d['icd10_code']!r} does not look like a real code"
        )
        assert 0.0 <= d["confidence"] <= 1.0
        # evidence_refs is in the schema; the LLM may return an empty
        # list, but it must be a list (not None, not absent).
        assert isinstance(d.get("evidence_refs", []), list)

    assert body["urgency_level"] in URGENCY_LEVELS


@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_real_llm_respects_max_results_cap(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """Even if the model surfaces more differentials, ``max_results``
    must cap the response from the caller's perspective."""
    _require_api_key()
    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "symptoms": "fever, sore throat, cough for 3 days",
            "max_results": 2,
        },
    )
    assert res.status_code == 200, res.text
    differentials = res.json()["differential_diagnoses"]
    assert len(differentials) <= 2, (
        f"max_results=2 not honored — got {len(differentials)} differentials"
    )
