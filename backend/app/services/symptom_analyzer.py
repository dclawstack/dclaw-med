"""Symptom analysis service.

Primary path calls the LLM via :mod:`app.services.llm` and validates the
structured response against :class:`SymptomAnalysisResponse`. If the LLM is
unconfigured (no API key), mocked, returns malformed JSON, or fails Pydantic
validation, the service falls back to the embedded keyword matcher below so
the endpoint stays useful in dev / offline / outage scenarios.

The keyword fallback is intentionally narrow (5 symptom families) and is not
meant to be clinically reliable on its own — it exists so demos and tests
still return *something* shaped right when the LLM isn't around.
"""

import logging
from uuid import UUID

import structlog
from pydantic import ValidationError

from app.schemas.symptom import (
    DifferentialDiagnosis,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    TriageRequest,
    TriageResponse,
)
from app.services.llm import LLMUnavailable, json_completion

log = structlog.get_logger(__name__)

# Mock knowledge base for symptom pattern matching
SYMPTOM_PATTERNS = {
    "chest pain": {
        "diagnoses": [
            DifferentialDiagnosis(
                condition="Acute Coronary Syndrome",
                icd10_code="I24.9",
                confidence=0.78,
                reasoning="Chest pain with potential cardiac origin requires immediate ECG and troponins",
            ),
            DifferentialDiagnosis(
                condition="Stable Angina Pectoris",
                icd10_code="I20.9",
                confidence=0.65,
                reasoning="Exertional chest pain relieved by rest is classic for angina",
            ),
            DifferentialDiagnosis(
                condition="Costochondritis",
                icd10_code="M94.0",
                confidence=0.42,
                reasoning="Localized chest wall pain reproducible on palpation",
            ),
            DifferentialDiagnosis(
                condition="Gastroesophageal Reflux Disease",
                icd10_code="K21.9",
                confidence=0.38,
                reasoning="Burning epigastric/chest pain after meals or when supine",
            ),
            DifferentialDiagnosis(
                condition="Pulmonary Embolism",
                icd10_code="I26.9",
                confidence=0.55,
                reasoning="Pleuritic chest pain with dyspnea and risk factors",
            ),
        ],
        "tests": ["ECG", "Troponin I/T", "Chest X-ray", "D-dimer", "CT pulmonary angiography"],
        "urgency": "high",
        "department": "Emergency Department",
        "red_flags": [
            "Crushing or pressure-like pain",
            "Pain radiating to arm, jaw, or back",
            "Diaphoresis (cold sweat) or nausea",
            "Shortness of breath at rest",
            "Syncope or near-syncope",
        ],
    },
    "fever": {
        "diagnoses": [
            DifferentialDiagnosis(
                condition="Viral Upper Respiratory Infection",
                icd10_code="J06.9",
                confidence=0.72,
                reasoning="Low-grade fever with cough and rhinorrhea",
            ),
            DifferentialDiagnosis(
                condition="COVID-19",
                icd10_code="U07.1",
                confidence=0.55,
                reasoning="Fever with respiratory symptoms in endemic period",
            ),
            DifferentialDiagnosis(
                condition="Urinary Tract Infection",
                icd10_code="N39.0",
                confidence=0.48,
                reasoning="Fever with dysuria or urinary frequency",
            ),
            DifferentialDiagnosis(
                condition="Sepsis",
                icd10_code="R65.21",
                confidence=0.35,
                reasoning="High fever with tachycardia and hypotension requires workup",
            ),
        ],
        "tests": ["CBC with differential", "Blood cultures", "Urinalysis", "CRP", "Procalcitonin"],
        "urgency": "medium",
        "department": "Primary Care",
        "red_flags": [
            "Temperature ≥ 39.5°C / 103°F",
            "Stiff neck or photophobia",
            "Altered mental status",
            "Persistent fever > 5 days",
            "Rash, especially non-blanching",
        ],
    },
    "headache": {
        "diagnoses": [
            DifferentialDiagnosis(
                condition="Tension-Type Headache",
                icd10_code="G44.2",
                confidence=0.70,
                reasoning="Bilateral pressing quality, mild to moderate intensity",
            ),
            DifferentialDiagnosis(
                condition="Migraine without Aura",
                icd10_code="G43.909",
                confidence=0.62,
                reasoning="Unilateral throbbing pain with photophobia or phonophobia",
            ),
            DifferentialDiagnosis(
                condition="Subarachnoid Hemorrhage",
                icd10_code="I60.9",
                confidence=0.15,
                reasoning="Thunderclap headache is neurosurgical emergency",
            ),
            DifferentialDiagnosis(
                condition="Sinusitis",
                icd10_code="J32.9",
                confidence=0.40,
                reasoning="Facial pain with nasal congestion and purulent discharge",
            ),
        ],
        "tests": ["Non-contrast head CT", "CBC", "Erythrocyte sedimentation rate", " Neurological exam"],
        "urgency": "medium",
        "department": "Primary Care",
        "red_flags": [
            "Thunderclap onset (worst headache of life)",
            "Fever with neck stiffness",
            "Focal neurological deficits or seizure",
            "Recent head trauma",
            "Sudden change in vision",
        ],
    },
    "abdominal pain": {
        "diagnoses": [
            DifferentialDiagnosis(
                condition="Acute Appendicitis",
                icd10_code="K35.80",
                confidence=0.60,
                reasoning="Periumbilical pain migrating to RLQ with anorexia",
            ),
            DifferentialDiagnosis(
                condition="Gastroenteritis",
                icd10_code="K52.9",
                confidence=0.55,
                reasoning="Diffuse abdominal pain with diarrhea and/or vomiting",
            ),
            DifferentialDiagnosis(
                condition="Cholecystitis",
                icd10_code="K81.0",
                confidence=0.50,
                reasoning="RUQ pain after fatty meals with fever and leukocytosis",
            ),
            DifferentialDiagnosis(
                condition="Pancreatitis",
                icd10_code="K85.9",
                confidence=0.40,
                reasoning="Severe epigastric pain radiating to back with elevated lipase",
            ),
        ],
        "tests": ["CBC", "Comprehensive metabolic panel", "Lipase", "CT abdomen/pelvis", "Urinalysis"],
        "urgency": "high",
        "department": "Emergency Department",
        "red_flags": [
            "Rigid or board-like abdomen",
            "Severe pain unresponsive to position changes",
            "Blood in stool or vomit",
            "Persistent vomiting and inability to tolerate fluids",
            "Pain with high fever",
        ],
    },
    "shortness of breath": {
        "diagnoses": [
            DifferentialDiagnosis(
                condition="Acute Exacerbation of COPD",
                icd10_code="J44.1",
                confidence=0.65,
                reasoning="Increased dyspnea with cough and sputum in COPD patient",
            ),
            DifferentialDiagnosis(
                condition="Community-Acquired Pneumonia",
                icd10_code="J18.9",
                confidence=0.60,
                reasoning="Dyspnea with fever, cough, and focal consolidation on CXR",
            ),
            DifferentialDiagnosis(
                condition="Heart Failure Exacerbation",
                icd10_code="I50.9",
                confidence=0.55,
                reasoning="Dyspnea with orthopnea, JVD, and peripheral edema",
            ),
            DifferentialDiagnosis(
                condition="Asthma Exacerbation",
                icd10_code="J45.901",
                confidence=0.50,
                reasoning="Wheezing and dyspnea responsive to bronchodilators",
            ),
        ],
        "tests": ["ABG", "BNP", "Chest X-ray", "Spirometry", "Echocardiogram"],
        "urgency": "high",
        "department": "Emergency Department",
        "red_flags": [
            "Cyanosis (bluish lips or extremities)",
            "Difficulty speaking in full sentences",
            "Chest pain with dyspnea",
            "Severe or sudden onset",
            "Audible wheezing or stridor at rest",
        ],
    },
}

DEFAULT_RESPONSE = {
    "diagnoses": [
        DifferentialDiagnosis(
            condition="Unspecified Symptom Complex",
            icd10_code="R68.89",
            confidence=0.30,
            reasoning="Insufficient symptom specificity for targeted differential",
        ),
        DifferentialDiagnosis(
            condition="Viral Syndrome",
            icd10_code="B34.9",
            confidence=0.45,
            reasoning="Nonspecific symptoms may represent viral illness",
        ),
        DifferentialDiagnosis(
            condition="Anxiety-Related Symptoms",
            icd10_code="F41.9",
            confidence=0.25,
            reasoning="Consider psychosomatic causes in absence of organic findings",
        ),
    ],
    "tests": ["CBC", "Comprehensive metabolic panel", "Physical examination"],
    "urgency": "low",
    "department": "Primary Care",
    "red_flags": [
        "Symptoms persist beyond two weeks",
        "Unexplained weight loss",
        "Worsening trajectory despite rest",
    ],
}


_URGENCY_GUIDANCE = {
    "critical": (
        "Call emergency services or go to the nearest emergency department "
        "immediately."
    ),
    "high": (
        "Seek urgent care today. If symptoms worsen or any red flag appears, "
        "go to the emergency department."
    ),
    "medium": (
        "Schedule a visit with your primary-care clinician within the next "
        "few days. Watch for the red flags listed above."
    ),
    "low": (
        "Schedule a routine appointment when convenient. Self-care and "
        "monitoring are reasonable in the interim."
    ),
}


def _match_pattern(symptoms: str) -> dict:
    """Find the first pattern that mentions one of our keyword fragments,
    or fall back to the default response."""
    text = symptoms.lower()
    for keyword, data in SYMPTOM_PATTERNS.items():
        if keyword in text:
            return data
    return DEFAULT_RESPONSE


def _primary_symptoms(symptoms: str) -> list[str]:
    return [s.strip() for s in symptoms.split(",") if s.strip()]


def _keyword_analyze(request: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
    """Static keyword-matcher fallback. See module docstring."""
    matched = _match_pattern(request.symptoms)
    diagnoses = matched["diagnoses"][: request.max_results]
    return SymptomAnalysisResponse(
        patient_id=request.patient_id,
        primary_symptoms=_primary_symptoms(request.symptoms),
        differential_diagnoses=diagnoses,
        recommended_tests=matched["tests"],
        urgency_level=matched["urgency"],
    )


_ANALYZER_SYSTEM_PROMPT = """\
You are a clinical decision support model assisting US physicians.

NON-NEGOTIABLE RULES:
1. Return JSON only. No prose, no markdown fences.
2. Always provide AT LEAST 3 differential diagnoses, ordered most-likely first.
   Never return a single diagnosis — primary-care reasoning is differential.
3. Each diagnosis must include a real ICD-10-CM code. If unsure, use the
   closest valid parent code; never invent a code.
4. confidence is a float in [0.0, 1.0]:
   ~0.3 = plausible, ~0.6 = likely, ~0.85 = highly likely.
5. urgency_level is exactly one of: "low", "medium", "high", "critical".
   - critical: life-threatening, EMS now (STEMI, anaphylaxis, severe SOB).
   - high: needs ED today.
   - medium: primary care within the week.
   - low: self-care, watch.
6. reasoning is 1-2 sentences that cite the specific symptom evidence
   from the user's input.
7. evidence_refs is a list of {source, excerpt}. ``source`` should be
   "patient-symptoms" when quoting the user's input, or a literature
   handle like "uptodate"/"pubmed". If a claim cannot be grounded,
   omit the diagnosis rather than fabricate a citation.
8. recommended_tests is a list of short test names actionable in a
   typical US outpatient or ED setting (e.g. "ECG", "CBC with diff").
"""

_ANALYZER_SCHEMA_HINT = """\
{
  "differential_diagnoses": [
    {
      "condition": "string",
      "icd10_code": "string",
      "confidence": 0.0,
      "reasoning": "string",
      "evidence_refs": [{"source": "string", "excerpt": "string"}]
    }
  ],
  "recommended_tests": ["string"],
  "urgency_level": "low|medium|high|critical"
}
"""


async def _llm_analyze(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Call the LLM, validate the structured response, return it.

    Raises :class:`LLMUnavailable` if the LLM is mocked/unconfigured or if
    the response fails schema validation — the caller turns that into a
    fallback to the keyword matcher.
    """
    user_prompt = (
        f"Patient ID: {request.patient_id}\n"
        f"Symptoms (free text): {request.symptoms}\n"
        f"Return at most {request.max_results} differentials."
    )
    raw = await json_completion(
        system=_ANALYZER_SYSTEM_PROMPT,
        user=user_prompt,
        schema_hint=_ANALYZER_SCHEMA_HINT,
    )
    try:
        diagnoses = [
            DifferentialDiagnosis.model_validate(d)
            for d in raw.get("differential_diagnoses", [])
        ][: request.max_results]
        urgency = raw.get("urgency_level", "low")
        tests = raw.get("recommended_tests", []) or []
    except ValidationError as exc:
        raise LLMUnavailable(f"LLM output failed schema validation: {exc}") from exc

    if len(diagnoses) < 1:
        # Guardrail: the prompt requires >=3; if the model returns 0 we
        # treat the response as unusable and let the caller fall back.
        raise LLMUnavailable("LLM returned no differentials")

    return SymptomAnalysisResponse(
        patient_id=request.patient_id,
        primary_symptoms=_primary_symptoms(request.symptoms),
        differential_diagnoses=diagnoses,
        recommended_tests=list(tests),
        urgency_level=urgency,
    )


async def analyze_symptoms(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Analyze symptoms and return differential diagnoses.

    Tries the LLM first; falls back to the keyword matcher if the LLM is
    unavailable or its output is unusable.
    """
    try:
        return await _llm_analyze(request)
    except LLMUnavailable as exc:
        log.info("symptom_analyzer.fallback", reason=str(exc))
        return _keyword_analyze(request)


async def triage(request: TriageRequest) -> TriageResponse:
    """Triage a free-text symptom description.

    The output is a routing recommendation (urgency + department + red flags)
    rather than a clinical diagnosis. Returns the top 3 differentials so the
    caller has some context for the recommendation without burying them in a
    full diagnostic list.
    """
    matched = _match_pattern(request.symptoms)
    summary = _URGENCY_GUIDANCE.get(matched["urgency"], _URGENCY_GUIDANCE["low"])
    return TriageResponse(
        urgency_level=matched["urgency"],
        suggested_department=matched["department"],
        recommended_tests=matched["tests"],
        red_flags=matched["red_flags"],
        differential_diagnoses=matched["diagnoses"][:3],
        summary=summary,
    )
