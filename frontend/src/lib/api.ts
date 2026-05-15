import { clearToken, getToken } from "./auth-storage";

const RAW_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";
const API_BASE = RAW_BASE.replace(/\/$/, "");
const MED = `${API_BASE}/api/v1/med`;
const AUTH = `${API_BASE}/api/v1/auth`;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) ?? {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...init, headers, cache: "no-store" });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new ApiError(res.status, `${res.status} ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---------- Auth ----------

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: "doctor" | "nurse" | "admin" | "receptionist" | string;
  is_active: boolean;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${AUTH}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, `${res.status} ${detail}`);
  }
  return (await res.json()) as LoginResponse;
}

export function getCurrentUser(): Promise<CurrentUser> {
  return request<CurrentUser>(`${AUTH}/me`);
}

export interface Provider {
  id: string;
  full_name: string;
  role: string;
}

export function listProviders(): Promise<Provider[]> {
  return request<Provider[]>(`${AUTH}/providers`);
}

// ---------- Health ----------

export interface HealthResponse {
  status: string;
  version: string;
}

export function healthCheck(): Promise<HealthResponse> {
  return request<HealthResponse>(`${API_BASE}/health`);
}

// ---------- Patients ----------

export interface PatientCreate {
  name: string;
  date_of_birth: string;
  gender: string;
  medical_record_number: string;
  contact_info?: Record<string, unknown> | null;
}

export interface PatientUpdate {
  name?: string;
  date_of_birth?: string;
  gender?: string;
  contact_info?: Record<string, unknown> | null;
}

export interface PatientResponse extends PatientCreate {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface PatientFilters {
  q?: string;
  dob_from?: string;
  dob_to?: string;
  diagnosis_code?: string;
}

export function listPatients(
  page = 1,
  pageSize = 20,
  filters: PatientFilters = {},
): Promise<PatientResponse[]> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value);
  }
  return request<PatientResponse[]>(`${MED}/patients?${params.toString()}`);
}

export function getPatient(id: string): Promise<PatientResponse> {
  return request<PatientResponse>(`${MED}/patients/${id}`);
}

export function createPatient(data: PatientCreate): Promise<PatientResponse> {
  return request<PatientResponse>(`${MED}/patients`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updatePatient(
  id: string,
  data: PatientUpdate,
): Promise<PatientResponse> {
  return request<PatientResponse>(`${MED}/patients/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deletePatient(id: string): Promise<void> {
  return request<void>(`${MED}/patients/${id}`, { method: "DELETE" });
}

export async function fetchPatientReport(id: string): Promise<Blob> {
  const token = getToken();
  const res = await fetch(`${MED}/patients/${id}/report`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    cache: "no-store",
  });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new ApiError(res.status, `${res.status} ${detail}`);
  }
  return await res.blob();
}

// ---------- Symptoms ----------

export interface SymptomCreate {
  patient_id: string;
  description: string;
  onset_date?: string | null | undefined;
  severity?: number;
  body_system?: string | null | undefined;
  notes?: string | null | undefined;
}

export interface SymptomResponse {
  id: string;
  patient_id: string;
  description: string;
  onset_date: string | null;
  severity: number;
  body_system: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DifferentialDiagnosis {
  condition: string;
  icd10_code: string;
  confidence: number;
  reasoning: string;
}

export interface SymptomAnalysisRequest {
  patient_id: string;
  symptoms: string;
  include_differential?: boolean;
  max_results?: number;
}

export interface SymptomAnalysisResponse {
  patient_id: string;
  primary_symptoms: string[];
  differential_diagnoses: DifferentialDiagnosis[];
  recommended_tests: string[];
  urgency_level: string;
  disclaimer: string;
}

export function listSymptoms(patientId?: string): Promise<SymptomResponse[]> {
  const q = patientId ? `?patient_id=${patientId}` : "";
  return request<SymptomResponse[]>(`${MED}/symptoms${q}`);
}

export function createSymptom(data: SymptomCreate): Promise<SymptomResponse> {
  return request<SymptomResponse>(`${MED}/symptoms`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteSymptom(id: string): Promise<void> {
  return request<void>(`${MED}/symptoms/${id}`, { method: "DELETE" });
}

export function analyzeSymptoms(
  data: SymptomAnalysisRequest,
): Promise<SymptomAnalysisResponse> {
  return request<SymptomAnalysisResponse>(`${MED}/symptoms/analyze`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------- Diagnoses ----------

export interface DiagnosisCreate {
  patient_id: string;
  icd10_code: string;
  name: string;
  description?: string | null;
  confidence?: number;
  status?: string;
  differential?: Record<string, unknown>[] | null;
}

export interface DiagnosisResponse {
  id: string;
  patient_id: string;
  icd10_code: string;
  name: string;
  description: string | null;
  confidence: number;
  status: string;
  differential: Record<string, unknown>[] | null;
  created_at: string;
  updated_at: string;
}

export function listDiagnoses(patientId?: string): Promise<DiagnosisResponse[]> {
  const q = patientId ? `?patient_id=${patientId}` : "";
  return request<DiagnosisResponse[]>(`${MED}/diagnoses${q}`);
}

export function createDiagnosis(data: DiagnosisCreate): Promise<DiagnosisResponse> {
  return request<DiagnosisResponse>(`${MED}/diagnoses`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteDiagnosis(id: string): Promise<void> {
  return request<void>(`${MED}/diagnoses/${id}`, { method: "DELETE" });
}

// ---------- Prescriptions ----------

export interface PrescriptionCreate {
  patient_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date?: string | null;
  instructions?: string | null;
  status?: string;
}

export interface PrescriptionResponse {
  id: string;
  patient_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date: string | null;
  instructions: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export function listPrescriptions(
  patientId?: string,
): Promise<PrescriptionResponse[]> {
  const q = patientId ? `?patient_id=${patientId}` : "";
  return request<PrescriptionResponse[]>(`${MED}/prescriptions${q}`);
}

export interface AllergyWarning {
  allergy_id: string;
  allergen: string;
  severity: string;
  reaction: string | null;
}

export interface PrescriptionCreateResponse extends PrescriptionResponse {
  allergy_warnings: AllergyWarning[];
}

export function createPrescription(
  data: PrescriptionCreate,
): Promise<PrescriptionCreateResponse> {
  return request<PrescriptionCreateResponse>(`${MED}/prescriptions`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deletePrescription(id: string): Promise<void> {
  return request<void>(`${MED}/prescriptions/${id}`, { method: "DELETE" });
}

// ---------- Allergies ----------

export interface AllergyResponse {
  id: string;
  patient_id: string;
  allergen: string;
  severity: string;
  reaction: string | null;
  created_at: string;
  updated_at: string;
}

export interface AllergyCreate {
  patient_id: string;
  allergen: string;
  severity: string;
  reaction?: string | null;
}

export function listAllergies(patientId: string): Promise<AllergyResponse[]> {
  return request<AllergyResponse[]>(
    `${MED}/allergies?patient_id=${patientId}`,
  );
}

export function createAllergy(
  data: AllergyCreate,
): Promise<AllergyResponse> {
  return request<AllergyResponse>(`${MED}/allergies`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteAllergy(id: string): Promise<void> {
  return request<void>(`${MED}/allergies/${id}`, { method: "DELETE" });
}

// ---------- Clinical Notes ----------

export interface ClinicalNoteCreate {
  patient_id: string;
  note_type: string;
  content: string;
  generated_by?: string;
  template_used?: string | null;
}

export interface ClinicalNoteResponse {
  id: string;
  patient_id: string;
  note_type: string;
  content: string;
  generated_by: string;
  template_used: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteGenerateRequest {
  patient_id: string;
  note_type: string;
  context: string;
  include_history?: boolean;
}

export interface NoteGenerateResponse {
  patient_id: string;
  note_type: string;
  generated_content: string;
  generated_by: string;
  template_used: string | null;
  word_count: number;
  disclaimer: string;
}

export function listNotes(patientId?: string): Promise<ClinicalNoteResponse[]> {
  const q = patientId ? `?patient_id=${patientId}` : "";
  return request<ClinicalNoteResponse[]>(`${MED}/notes${q}`);
}

export function createNote(data: ClinicalNoteCreate): Promise<ClinicalNoteResponse> {
  return request<ClinicalNoteResponse>(`${MED}/notes`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteNote(id: string): Promise<void> {
  return request<void>(`${MED}/notes/${id}`, { method: "DELETE" });
}

export function generateNote(
  data: NoteGenerateRequest,
): Promise<NoteGenerateResponse> {
  return request<NoteGenerateResponse>(`${MED}/notes/generate`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------- ICD-10 ----------

export interface ICD10Code {
  code: string;
  description: string;
  category: string;
  billable: boolean;
}

export interface ICD10LookupResponse {
  query: string;
  results: ICD10Code[];
  total_found: number;
}

export interface ICD10LookupRequest {
  query: string;
  max_results?: number;
}

export function lookupICD10(
  req: ICD10LookupRequest,
): Promise<ICD10LookupResponse> {
  return request<ICD10LookupResponse>(`${MED}/icd10/lookup`, {
    method: "POST",
    body: JSON.stringify({ query: req.query, max_results: req.max_results ?? 10 }),
  });
}

// ---------- Lab Results ----------

export interface LabResultCreate {
  patient_id: string;
  test_name: string;
  test_category: string;
  result_value: string;
  unit?: string | null;
  reference_range?: string | null;
  status?: string;
  ordered_at: string;
  resulted_at?: string | null;
  notes?: string | null;
}

export interface LabResultResponse {
  id: string;
  patient_id: string;
  test_name: string;
  test_category: string;
  result_value: string;
  unit: string | null;
  reference_range: string | null;
  status: string;
  ordered_at: string;
  resulted_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export function listLabResults(patientId?: string): Promise<LabResultResponse[]> {
  const q = patientId ? `?patient_id=${patientId}` : "";
  return request<LabResultResponse[]>(`${MED}/lab-results${q}`);
}

export function createLabResult(
  data: LabResultCreate,
): Promise<LabResultResponse> {
  return request<LabResultResponse>(`${MED}/lab-results`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteLabResult(id: string): Promise<void> {
  return request<void>(`${MED}/lab-results/${id}`, { method: "DELETE" });
}

// ---------- Appointments ----------

export interface AppointmentCreate {
  patient_id: string;
  provider_id: string;
  scheduled_at: string;
  duration_minutes?: number;
  status?: string;
  location?: string | null;
  notes?: string | null;
}

export interface AppointmentResponse {
  id: string;
  patient_id: string;
  provider_id: string;
  scheduled_at: string;
  duration_minutes: number;
  status: string;
  location: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentUpdate {
  scheduled_at?: string;
  duration_minutes?: number;
  status?: string;
  location?: string | null;
  notes?: string | null;
  provider_id?: string;
}

export function listAppointments(
  filters: {
    date?: string;
    patient_id?: string;
    provider_id?: string;
  } = {},
): Promise<AppointmentResponse[]> {
  const q = new URLSearchParams();
  if (filters.date) q.set("date", filters.date);
  if (filters.patient_id) q.set("patient_id", filters.patient_id);
  if (filters.provider_id) q.set("provider_id", filters.provider_id);
  const qs = q.toString();
  return request<AppointmentResponse[]>(
    `${MED}/appointments${qs ? `?${qs}` : ""}`,
  );
}

export function createAppointment(
  data: AppointmentCreate,
): Promise<AppointmentResponse> {
  return request<AppointmentResponse>(`${MED}/appointments`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateAppointment(
  id: string,
  data: AppointmentUpdate,
): Promise<AppointmentResponse> {
  return request<AppointmentResponse>(`${MED}/appointments/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteAppointment(id: string): Promise<void> {
  return request<void>(`${MED}/appointments/${id}`, { method: "DELETE" });
}

// ---------- Audit Logs (admin only) ----------

export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  timestamp: string;
}

export interface AuditLogFilters {
  user_id?: string;
  entity_type?: string;
  action?: string;
  page?: number;
  page_size?: number;
}

export function listAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLog[]> {
  const q = new URLSearchParams();
  if (filters.user_id) q.set("user_id", filters.user_id);
  if (filters.entity_type) q.set("entity_type", filters.entity_type);
  if (filters.action) q.set("action", filters.action);
  if (filters.page) q.set("page", String(filters.page));
  if (filters.page_size) q.set("page_size", String(filters.page_size));
  const qs = q.toString();
  return request<AuditLog[]>(
    `${API_BASE}/api/v1/audit${qs ? `?${qs}` : ""}`,
  );
}
