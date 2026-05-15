# DClaw Med — v1.2 Feature Roadmap

> **For coding agents:** Pick features from this list, implement them fully, and update this doc with a checkmark.
> **Do NOT change the basic stack.** See `AGENTS.md` for architecture lock.

## Pre-Flight Checklist — Do This First

Before implementing any v1.2 feature, verify:

- [ ] `frontend/package-lock.json` is committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed (required for Next.js TypeScript builds)
- [ ] `frontend/.gitignore` excludes `node_modules/` and `.next/`
- [ ] `docker-compose.yml` healthchecks use `python urllib.request.urlopen()` (backend) and `wget -q --spider` (frontend)
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [x] Patient CRUD (name, DOB, gender, MRN, contact)
- [x] Symptom CRUD + AI differential diagnosis analyzer
- [x] Diagnosis CRUD (ICD-10, confidence, status)
- [x] Prescription CRUD (medication, dosage, frequency, route)
- [x] Clinical Note CRUD + AI note generator
- [x] Drug interaction checker
- [x] ICD-10 lookup
- [x] Patient detail page with tabs (symptoms/diagnoses/prescriptions/notes)
- [x] Docker + Helm deployment
- [x] Alembic migrations

---

## v1.2 Roadmap

### P0 — Must Have

#### 1. Authentication & RBAC
**Description:** Role-based access control (doctor, nurse, admin, receptionist).
- **Backend:** Integrate with platform Identity service (Logto) or implement JWT-based auth. Add `User` and `Role` models. Protect all routes with `Depends(require_role(...))`. Add `created_by`, `updated_by` audit fields to all medical records.
- **Frontend:** Login page. Route guards based on role. Show/hide actions per role (e.g., nurses can view but not prescribe).
- **Files to touch:** `backend/app/core/auth.py`, `backend/app/models/user.py`, `frontend/src/app/login/page.tsx`, all routers

#### 2. Audit Logging (HIPAA Compliance) ✅
**Description:** Every read/write of patient data is logged immutably.
- **Backend:** Add `AuditLog` model (`id`, `user_id`, `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `timestamp`). Create `AuditLogRepository`. Middleware or dependency that logs all patient-related requests.
- **Frontend:** Admin-only "Audit Trail" page to view logs.
- **Files to touch:** `backend/app/models/audit_log.py`, `backend/app/repositories/audit_log_repo.py`, `backend/app/core/audit_middleware.py`, `frontend/src/app/audit/page.tsx`

#### 3. Lab Results Integration
**Description:** Store and display laboratory test results per patient.
- **Backend:** Add `LabResult` model (`id`, `patient_id`, `test_name`, `test_category`, `result_value`, `unit`, `reference_range`, `status`, `ordered_at`, `resulted_at`). Full CRUD endpoints.
- **Frontend:** Lab Results tab on patient detail. Table with color-coded out-of-range values. Trend charts for repeated tests.
- **Files to touch:** `backend/app/models/lab_result.py`, `backend/app/repositories/lab_result_repo.py`, `backend/app/api/v1/med/lab_results.py`, `frontend/src/app/patients/[id]/LabResultsTab.tsx`

#### 4. Appointment Scheduling
**Description:** Schedule patient appointments with doctors.
- **Backend:** Add `Appointment` model (`id`, `patient_id`, `provider_id`, `scheduled_at`, `duration_minutes`, `status`, `notes`, `location`). Prevent double-booking with unique constraints. `GET /appointments?date=YYYY-MM-DD` for calendar view.
- **Frontend:** Calendar view (week/month). Appointment cards. Color-coded by status (scheduled, completed, cancelled, no-show).
- **Files to touch:** `backend/app/models/appointment.py`, `backend/app/repositories/appointment_repo.py`, `backend/app/api/v1/med/appointments.py`, `frontend/src/app/appointments/page.tsx`

### P1 — Should Have

#### 5. Patient Portal (Read-Only) ✅
**Description:** Patients can log in and view their own records (but not edit).
- **Backend:** Separate router `/api/v1/patient-portal/` that filters by `current_user.patient_id`. Returns only own data.
- **Frontend:** Simplified patient-facing UI showing medications, appointments, lab results, and doctor's notes.
- **Files to touch:** `backend/app/api/v1/patient_portal.py`, `frontend/src/app/patient-portal/page.tsx`

#### 6. Drug Allergy Alerts ✅
**Description:** Alert when prescribing a medication the patient is allergic to.
- **Backend:** Add `Allergy` model (`id`, `patient_id`, `allergen`, `severity`, `reaction`). When creating a prescription, check patient's allergies against the medication name. Return warning in response if match found.
- **Frontend:** Red alert banner in prescription dialog if allergy detected.
- **Files to touch:** `backend/app/models/allergy.py`, `backend/app/repositories/allergy_repo.py`, `backend/app/api/v1/med/prescriptions.py`, `frontend/src/app/patients/[id]/PrescriptionTab.tsx`

#### 7. Medical Report Generation (PDF) ✅
**Description:** Generate printable medical reports for patients.
- **Backend:** Use `jinja2` templates + `weasyprint` or HTML-to-PDF to generate PDFs. `GET /api/v1/med/patients/{id}/report` returns PDF.
- **Frontend:** "Generate Report" button on patient detail. Opens PDF in new tab.
- **Files to touch:** `backend/app/services/report_service.py`, `backend/app/templates/patient_report.html`, `backend/app/api/v1/med/patients.py`

#### 8. Advanced Patient Search ✅
**Description:** Search patients by name, MRN, DOB range, or diagnosis.
- **Backend:** PostgreSQL `tsvector` on patient name. Composite search endpoint with filters.
- **Frontend:** Search bar with filter dropdowns on patients page.
- **Files to touch:** `backend/app/api/v1/med/patients.py`, `frontend/src/app/patients/page.tsx`

### P2 — Could Have

#### 9. HL7 FHIR Data Export ✅
**Description:** Export patient data in FHIR R4 format for interoperability.
- **Backend:** FHIR resource mappers for Patient, Condition, MedicationRequest, Observation. `GET /api/v1/med/fhir/Patient/{id}` etc.
- **Files to touch:** `backend/app/services/fhir_mapper.py`, `backend/app/api/v1/med/fhir.py`

#### 10. AI Triage Assistant ✅
**Description:** Patient describes symptoms via chat; AI suggests urgency level and department.
- **Backend:** Extend `symptom_analyzer.py` with triage logic. Return `urgency_level`, `suggested_department`, `recommended_tests`.
- **Frontend:** Triage widget on dashboard.

---

## Implementation Priority

1. Authentication & RBAC (security foundation)
2. Audit Logging (compliance requirement)
3. Lab Results (core clinical feature)
4. Appointment Scheduling (workflow)
5. Drug Allergy Alerts (patient safety)
6. Advanced Patient Search (daily utility)
7. Medical Report Generation (output)
8. Patient Portal (patient engagement)
9. HL7 FHIR Export (integration)
10. AI Triage Assistant (AI differentiation)
