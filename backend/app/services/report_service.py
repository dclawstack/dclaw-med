"""Patient report PDF generation."""

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.models.patient import Patient

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


def render_patient_pdf(patient: Patient) -> bytes:
    """Render a full patient report as a PDF byte string.

    The caller is responsible for loading the patient with its related
    collections (allergies, diagnoses, prescriptions, lab_results, clinical_notes).
    """
    template = _env.get_template("patient_report.html")
    # Stable ordering for the report: most recent first.
    diagnoses = sorted(patient.diagnoses, key=lambda d: d.created_at, reverse=True)
    prescriptions = sorted(
        patient.prescriptions, key=lambda p: p.created_at, reverse=True
    )
    lab_results = sorted(
        patient.lab_results, key=lambda l: l.ordered_at, reverse=True
    )
    clinical_notes = sorted(
        patient.clinical_notes, key=lambda n: n.created_at, reverse=True
    )
    allergies = sorted(patient.allergies, key=lambda a: a.created_at, reverse=True)

    html = template.render(
        patient=patient,
        allergies=allergies,
        diagnoses=diagnoses,
        prescriptions=prescriptions,
        lab_results=lab_results,
        clinical_notes=clinical_notes,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    return HTML(string=html).write_pdf()
