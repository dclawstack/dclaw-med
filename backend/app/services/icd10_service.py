"""ICD-10 code lookup service with embedded dataset."""

from app.schemas.diagnosis import ICD10Code, ICD10LookupRequest, ICD10LookupResponse

ICD10_DATASET = [
    ICD10Code(code="A09", description="Infectious gastroenteritis and colitis, unspecified", category="Infectious"),
    ICD10Code(code="B34.9", description="Viral infection, unspecified", category="Infectious"),
    ICD10Code(code="E11.9", description="Type 2 diabetes mellitus without complications", category="Endocrine"),
    ICD10Code(code="E78.5", description="Hyperlipidemia, unspecified", category="Endocrine"),
    ICD10Code(code="F32.9", description="Major depressive disorder, single episode, unspecified", category="Mental Health"),
    ICD10Code(code="F41.9", description="Anxiety disorder, unspecified", category="Mental Health"),
    ICD10Code(code="G43.909", description="Migraine, unspecified, not intractable", category="Neurological"),
    ICD10Code(code="G44.2", description="Tension-type headache, unspecified", category="Neurological"),
    ICD10Code(code="I10", description="Essential (primary) hypertension", category="Cardiovascular"),
    ICD10Code(code="I20.9", description="Angina pectoris, unspecified", category="Cardiovascular"),
    ICD10Code(code="I21.9", description="Acute myocardial infarction, unspecified", category="Cardiovascular"),
    ICD10Code(code="I24.9", description="Acute ischemic heart disease, unspecified", category="Cardiovascular"),
    ICD10Code(code="I26.9", description="Pulmonary embolism without acute cor pulmonale", category="Cardiovascular"),
    ICD10Code(code="I50.9", description="Heart failure, unspecified", category="Cardiovascular"),
    ICD10Code(code="J06.9", description="Acute upper respiratory infection, unspecified", category="Respiratory"),
    ICD10Code(code="J18.9", description="Pneumonia, unspecified organism", category="Respiratory"),
    ICD10Code(code="J32.9", description="Chronic sinusitis, unspecified", category="Respiratory"),
    ICD10Code(code="J44.1", description="COPD with acute exacerbation", category="Respiratory"),
    ICD10Code(code="J45.901", description="Unspecified asthma with acute exacerbation", category="Respiratory"),
    ICD10Code(code="K21.9", description="Gastro-esophageal reflux disease without esophagitis", category="GI"),
    ICD10Code(code="K35.80", description="Acute appendicitis, unspecified", category="GI"),
    ICD10Code(code="K52.9", description="Noninfective gastroenteritis and colitis, unspecified", category="GI"),
    ICD10Code(code="K81.0", description="Acute cholecystitis", category="GI"),
    ICD10Code(code="K85.9", description="Acute pancreatitis, unspecified", category="GI"),
    ICD10Code(code="M25.50", description="Pain in unspecified joint", category="Musculoskeletal"),
    ICD10Code(code="M54.5", description="Low back pain", category="Musculoskeletal"),
    ICD10Code(code="M79.1", description="Myalgia", category="Musculoskeletal"),
    ICD10Code(code="M94.0", description="Chondrocostal junction syndrome [Tietze]", category="Musculoskeletal"),
    ICD10Code(code="N18.3", description="Chronic kidney disease, stage 3", category="Renal"),
    ICD10Code(code="N39.0", description="Urinary tract infection, site not specified", category="Renal"),
    ICD10Code(code="R50.9", description="Fever, unspecified", category="General"),
    ICD10Code(code="R51", description="Headache", category="General"),
    ICD10Code(code="R55", description="Syncope and collapse", category="General"),
    ICD10Code(code="R65.21", description="Severe sepsis with septic shock", category="General"),
    ICD10Code(code="R68.89", description="Other general symptoms and signs", category="General"),
    ICD10Code(code="U07.1", description="COVID-19", category="Infectious"),
    ICD10Code(code="Z51.11", description="Encounter for antineoplastic chemotherapy", category="Oncology"),
]


def lookup_icd10(request: ICD10LookupRequest) -> ICD10LookupResponse:
    """Search ICD-10 codes by query term."""
    query = request.query.lower()
    results = []

    for entry in ICD10_DATASET:
        if query in entry.code.lower() or query in entry.description.lower() or query in entry.category.lower():
            results.append(entry)

    return ICD10LookupResponse(
        query=request.query,
        results=results[: request.max_results],
        total_found=len(results),
    )
