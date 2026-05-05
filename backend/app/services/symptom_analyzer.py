"""Symptom analysis service with mock differential diagnosis."""

from uuid import UUID

from app.schemas.symptom import (
    DifferentialDiagnosis,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
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
}


async def analyze_symptoms(
    request: SymptomAnalysisRequest,
) -> SymptomAnalysisResponse:
    """Analyze symptoms and return differential diagnoses."""
    symptoms_lower = request.symptoms.lower()

    matched = None
    for keyword, data in SYMPTOM_PATTERNS.items():
        if keyword in symptoms_lower:
            matched = data
            break

    if matched is None:
        matched = DEFAULT_RESPONSE

    diagnoses = matched["diagnoses"][: request.max_results]
    urgency = matched["urgency"]

    return SymptomAnalysisResponse(
        patient_id=request.patient_id,
        primary_symptoms=[s.strip() for s in request.symptoms.split(",") if s.strip()],
        differential_diagnoses=diagnoses,
        recommended_tests=matched["tests"],
        urgency_level=urgency,
    )
