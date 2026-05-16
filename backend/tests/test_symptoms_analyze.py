"""Tests for /api/v1/med/symptoms/analyze.

Covers both code paths in :mod:`app.services.symptom_analyzer`:
- The LLM happy path (with a monkeypatched ``json_completion``).
- The fallback to the keyword matcher when the LLM is unavailable or
  returns unusable output.

Network is never hit — ``app.services.llm.json_completion`` is monkeypatched
in every test that exercises the LLM path. The fallback tests rely on the
default behavior of ``json_completion`` raising ``LLMUnavailable`` when no
``OPENROUTER_API_KEY`` is set (which is the case in CI).
"""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

ANALYZE = "/api/v1/med/symptoms/analyze"


def _llm_payload(*, n: int = 3) -> dict[str, Any]:
    """Build a well-formed structured LLM response with ``n`` differentials."""
    return {
        "differential_diagnoses": [
            {
                "condition": f"LLM-Suggested Condition {i}",
                "icd10_code": f"Z00.{i}",
                "confidence": round(0.9 - 0.1 * i, 2),
                "reasoning": f"LLM reasoning for condition {i}.",
                "evidence_refs": [
                    {"source": "patient-symptoms", "excerpt": "(quoted user input)"},
                ],
            }
            for i in range(n)
        ],
        "recommended_tests": ["CBC", "BMP"],
        "urgency_level": "medium",
    }


@pytest.mark.asyncio
async def test_analyze_uses_llm_when_available(
    monkeypatch: pytest.MonkeyPatch,
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """When ``json_completion`` returns a valid payload, the endpoint
    surfaces the LLM output (not the keyword fallback)."""
    payload = _llm_payload(n=4)

    async def fake_json_completion(**_: Any) -> dict[str, Any]:
        return payload

    # Patch where the analyzer imports it, not at the source module — the
    # analyzer imports the symbol into its own namespace at module load.
    monkeypatch.setattr(
        "app.services.symptom_analyzer.json_completion",
        fake_json_completion,
    )

    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "symptoms": "abdominal pain",  # would hit a keyword match if fallback fired
            "max_results": 5,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    # Must be the LLM payload, not the keyword fixture for "abdominal pain"
    # (which uses real-world conditions like "Acute Appendicitis").
    conditions = [d["condition"] for d in body["differential_diagnoses"]]
    assert all(c.startswith("LLM-Suggested Condition") for c in conditions)
    assert len(conditions) == 4
    assert body["urgency_level"] == "medium"
    assert body["recommended_tests"] == ["CBC", "BMP"]
    # Evidence refs round-trip through the schema.
    assert body["differential_diagnoses"][0]["evidence_refs"][0]["source"] == "patient-symptoms"


@pytest.mark.asyncio
async def test_analyze_respects_max_results(
    monkeypatch: pytest.MonkeyPatch,
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """Caller's ``max_results`` caps the LLM output even if the model
    returns more diagnoses than requested."""
    payload = _llm_payload(n=6)

    async def fake_json_completion(**_: Any) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(
        "app.services.symptom_analyzer.json_completion",
        fake_json_completion,
    )

    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={"patient_id": patient_id, "symptoms": "headache", "max_results": 2},
    )
    assert res.status_code == 200
    assert len(res.json()["differential_diagnoses"]) == 2


@pytest.mark.asyncio
async def test_analyze_falls_back_when_llm_unavailable(
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """With no API key set (the default in tests), the LLM is mocked-as-
    unavailable and the keyword matcher serves the request."""
    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={
            "patient_id": patient_id,
            "symptoms": "chest pain radiating to left arm",
            "max_results": 3,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    # Keyword fixture for "chest pain" includes Acute Coronary Syndrome.
    conditions = [d["condition"] for d in body["differential_diagnoses"]]
    assert any("Acute Coronary Syndrome" in c for c in conditions)
    assert body["urgency_level"] == "high"


@pytest.mark.asyncio
async def test_analyze_falls_back_when_llm_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """If the LLM returns zero differentials, the service treats the
    response as unusable and falls back to the keyword matcher."""

    async def empty_completion(**_: Any) -> dict[str, Any]:
        return {"differential_diagnoses": [], "recommended_tests": [], "urgency_level": "low"}

    monkeypatch.setattr(
        "app.services.symptom_analyzer.json_completion",
        empty_completion,
    )

    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={"patient_id": patient_id, "symptoms": "fever", "max_results": 3},
    )
    assert res.status_code == 200
    # "fever" keyword fixture includes a viral URI as the top differential.
    body = res.json()
    assert len(body["differential_diagnoses"]) >= 1
    conditions = [d["condition"].lower() for d in body["differential_diagnoses"]]
    assert any("respiratory" in c or "viral" in c or "infection" in c for c in conditions)


@pytest.mark.asyncio
async def test_analyze_falls_back_when_llm_payload_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    client: AsyncClient,
    doctor_headers: dict[str, str],
    patient_id: str,
) -> None:
    """Schema-invalid LLM output (e.g. missing required fields) → fallback,
    not a 5xx."""

    async def bad_completion(**_: Any) -> dict[str, Any]:
        return {
            "differential_diagnoses": [
                # Missing icd10_code and confidence — should fail Pydantic.
                {"condition": "X", "reasoning": "Y"},
            ],
            "recommended_tests": [],
            "urgency_level": "low",
        }

    monkeypatch.setattr(
        "app.services.symptom_analyzer.json_completion",
        bad_completion,
    )

    res = await client.post(
        ANALYZE,
        headers=doctor_headers,
        json={"patient_id": patient_id, "symptoms": "headache", "max_results": 3},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    # Should be the keyword fixture for "headache", not a 500.
    conditions = [d["condition"] for d in body["differential_diagnoses"]]
    assert any("Headache" in c or "Migraine" in c for c in conditions)
