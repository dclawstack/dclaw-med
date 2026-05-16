"""Live OpenRouter smoke test for the symptom analyzer.

Runs three real calls against the LLM path, prints sanitized results.
The API key is read from settings (env / .env); it's never printed.

Usage from backend/:
    python -m scripts.smoke_llm_analyzer
"""

from __future__ import annotations

import asyncio
import time
from uuid import uuid4

from app.core.config import settings
from app.schemas.symptom import SymptomAnalysisRequest
from app.services.llm import _mocked
from app.services.symptom_analyzer import _llm_analyze, analyze_symptoms


def _redact(s: str) -> str:
    # Belt-and-braces: never echo a token even if one slipped into a field.
    return "<redacted-token>" if isinstance(s, str) and s.startswith("sk-") else s


async def _run(name: str, symptoms: str, *, max_results: int = 5) -> None:
    req = SymptomAnalysisRequest(
        patient_id=uuid4(),
        symptoms=symptoms,
        max_results=max_results,
    )
    print(f"\n=== {name} ===")
    print(f"  symptoms: {symptoms!r} (max_results={max_results})")
    t0 = time.perf_counter()
    res = await analyze_symptoms(req)
    elapsed = time.perf_counter() - t0
    print(f"  latency: {elapsed:.2f}s")
    print(f"  urgency_level: {res.urgency_level}")
    print(f"  recommended_tests: {res.recommended_tests}")
    print(f"  #differentials: {len(res.differential_diagnoses)}")
    for i, dx in enumerate(res.differential_diagnoses, 1):
        evi_summary = (
            ", ".join(f"{e.source}" for e in dx.evidence_refs) or "(none)"
        )
        print(
            f"   {i}. {_redact(dx.condition)}  "
            f"({dx.icd10_code}, conf={dx.confidence:.2f})"
        )
        print(f"      reasoning: {_redact(dx.reasoning)}")
        print(f"      evidence_refs: {evi_summary}")


async def main() -> None:
    print(f"model: {settings.llm_model}")
    print(f"mock mode active? {_mocked()}")
    if _mocked():
        print("WARN: LLM is mocked or unconfigured — these calls will fall back.")

    await _run("scenario 1: chest pain", "Crushing chest pain radiating to left arm, diaphoresis")
    await _run("scenario 2: mild headache", "Mild headache for 3 days, no red flags")
    await _run("scenario 3: cap-honored", "abdominal pain", max_results=2)


if __name__ == "__main__":
    asyncio.run(main())
