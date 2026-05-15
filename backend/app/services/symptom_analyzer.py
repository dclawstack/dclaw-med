"""Symptom analysis service with mock differential diagnosis."""

from uuid import UUID

from app.schemas.symptom import (
    DifferentialDiagnosis,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    TriageRequest,
    TriageResponse,
)

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


async def analyze_symptoms(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Analyze symptoms and return differential diagnoses."""
    matched = _match_pattern(request.symptoms)
    diagnoses = matched["diagnoses"][: request.max_results]

    return SymptomAnalysisResponse(
        patient_id=request.patient_id,
        primary_symptoms=[s.strip() for s in request.symptoms.split(",") if s.strip()],
        differential_diagnoses=diagnoses,
        recommended_tests=matched["tests"],
        urgency_level=matched["urgency"],
    )


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
