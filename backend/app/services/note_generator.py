"""Clinical note generation service (mock)."""

from uuid import UUID

from app.schemas.clinical_note import NoteGenerateRequest, NoteGenerateResponse

NOTE_TEMPLATES = {
    "progress": """PROGRESS NOTE

Date: {timestamp}
Patient ID: {patient_id}

SUBJECTIVE:
{context}

OBJECTIVE:
Vital signs stable. Physical examination within normal limits unless otherwise noted.

ASSESSMENT:
Patient presenting with above symptoms. Differential diagnosis broad.

PLAN:
1. Continue current management
2. Monitor for changes in clinical status
3. Follow up as indicated
4. Patient education provided

Signed: AI Assistant
""",
    "admission": """ADMISSION NOTE

Date: {timestamp}
Patient ID: {patient_id}

CHIEF COMPLAINT:
{context}

HISTORY OF PRESENT ILLNESS:
Patient presents with above complaints. Detailed history obtained.

REVIEW OF SYSTEMS:
General: No fever, chills, or weight changes
Cardiovascular: No chest pain or palpitations
Respiratory: No dyspnea or cough
GI: No nausea, vomiting, or changes in bowel habits
Other systems unremarkable

PHYSICAL EXAMINATION:
General: Alert and oriented, in no acute distress
Vitals: Stable
HEENT: Normocephalic, atraumatic
Cardiovascular: Regular rate and rhythm
Respiratory: Clear to auscultation bilaterally
Abdomen: Soft, non-tender, non-distended
Extremities: No edema

IMPRESSION:
Admission for further evaluation and management of presenting condition.

PLAN:
1. Admit to general medicine service
2. Diagnostic workup as indicated
3. Symptomatic management
4. Consultations as needed

Signed: AI Assistant
""",
    "discharge": """DISCHARGE SUMMARY

Date: {timestamp}
Patient ID: {patient_id}

ADMISSION DIAGNOSIS:
{context}

HOSPITAL COURSE:
Patient admitted for evaluation and treatment. Hospital course uncomplicated.
Diagnostic workup completed. Treatment plan initiated with good response.

DISCHARGE DIAGNOSIS:
Primary condition treated during admission.

DISCHARGE CONDITION:
Stable. Patient tolerating diet and medications.

DISCHARGE MEDICATIONS:
As prescribed in discharge medication list.

DISCHARGE INSTRUCTIONS:
1. Take all medications as prescribed
2. Follow up with primary care physician within 1 week
3. Return to ER if symptoms worsen
4. Activity as tolerated
5. Diet: Regular

Signed: AI Assistant
""",
    "procedure": """PROCEDURE NOTE

Date: {timestamp}
Patient ID: {patient_id}

PROCEDURE:
{context}

INDICATION:
Clinical indication for procedure as documented above.

CONSENT:
Informed consent obtained. Risks, benefits, and alternatives discussed.

DESCRIPTION:
Procedure performed under standard sterile technique.
Patient tolerated procedure well without immediate complications.

ESTIMATED BLOOD LOSS:
Minimal.

SPECIMENS:
As indicated sent to appropriate laboratory services.

POST-PROCEDURE PLAN:
1. Monitor vital signs per protocol
2. Watch for procedure-specific complications
3. Activity restrictions as indicated
4. Follow up results with patient

Signed: AI Assistant
""",
}


async def generate_note(request: NoteGenerateRequest) -> NoteGenerateResponse:
    """Generate a clinical note from context."""
    from datetime import datetime, timezone

    template = NOTE_TEMPLATES.get(request.note_type, NOTE_TEMPLATES["progress"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    content = template.format(
        patient_id=str(request.patient_id),
        context=request.context,
        timestamp=now,
    )

    return NoteGenerateResponse(
        patient_id=request.patient_id,
        note_type=request.note_type,
        generated_content=content,
        generated_by="ai",
        template_used=request.note_type,
        word_count=len(content.split()),
    )
