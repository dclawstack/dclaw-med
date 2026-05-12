"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  getPatient, updatePatient,
  listSymptoms, createSymptom, deleteSymptom,
  listDiagnoses, createDiagnosis, deleteDiagnosis,
  listPrescriptions, createPrescription, deletePrescription,
  listNotes, createNote, deleteNote,
  listLabResults, createLabResult, deleteLabResult,
  PatientResponse, SymptomResponse, DiagnosisResponse, PrescriptionResponse, ClinicalNoteResponse, LabResultResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ArrowLeft, Plus, Trash2, Save, User, Calendar, Stethoscope, Pill, FileText, ClipboardList, FlaskConical } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";

export default function PatientDetailPage() {
  const { user } = useAuth();
  const canWritePatient = can.writePatient(user);
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<PatientResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDob, setEditDob] = useState("");
  const [editGender, setEditGender] = useState("");

  const [symptoms, setSymptoms] = useState<SymptomResponse[]>([]);
  const [diagnoses, setDiagnoses] = useState<DiagnosisResponse[]>([]);
  const [prescriptions, setPrescriptions] = useState<PrescriptionResponse[]>([]);
  const [notes, setNotes] = useState<ClinicalNoteResponse[]>([]);
  const [labResults, setLabResults] = useState<LabResultResponse[]>([]);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      getPatient(id),
      listSymptoms(id),
      listDiagnoses(id),
      listPrescriptions(id),
      listNotes(id),
      listLabResults(id),
    ])
      .then(([p, s, d, rx, n, l]) => {
        setPatient(p);
        setEditName(p.name);
        setEditDob(p.date_of_birth);
        setEditGender(p.gender);
        setSymptoms(s);
        setDiagnoses(d);
        setPrescriptions(rx);
        setNotes(n);
        setLabResults(l);
      })
      .catch((err) => toast.error("Failed to load patient", { description: err.message }))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSave() {
    if (!patient) return;
    try {
      const updated = await updatePatient(patient.id, {
        name: editName,
        date_of_birth: editDob,
        gender: editGender,
      });
      setPatient(updated);
      setEditMode(false);
      toast.success("Patient updated");
    } catch (err) {
      toast.error("Update failed", { description: err instanceof Error ? err.message : "" });
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <p className="text-muted-foreground">Patient not found.</p>
        <Link href="/patients"><Button variant="outline"><ArrowLeft className="w-4 h-4 mr-2" />Back to Patients</Button></Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/patients">
            <Button variant="outline" size="icon"><ArrowLeft className="w-4 h-4" /></Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <User className="w-6 h-6 text-primary" />
              {patient.name}
            </h1>
            <p className="text-sm text-muted-foreground">{patient.medical_record_number} · {patient.gender} · DOB {patient.date_of_birth}</p>
          </div>
        </div>
        {canWritePatient && (
          <Button variant="outline" onClick={() => setEditMode((v) => !v)}>{editMode ? "Cancel" : "Edit"}</Button>
        )}
      </div>

      {editMode && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <Label>Name</Label>
                <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Date of Birth</Label>
                <Input type="date" value={editDob} onChange={(e) => setEditDob(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Gender</Label>
                <Select value={editGender} onValueChange={(v) => setEditGender(v ?? "")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="unknown">Unknown</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleSave}><Save className="w-4 h-4 mr-2" />Save</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="symptoms">
        <TabsList>
          <TabsTrigger value="symptoms"><Stethoscope className="w-3 h-3 mr-1" />Symptoms ({symptoms.length})</TabsTrigger>
          <TabsTrigger value="diagnoses"><ClipboardList className="w-3 h-3 mr-1" />Diagnoses ({diagnoses.length})</TabsTrigger>
          <TabsTrigger value="prescriptions"><Pill className="w-3 h-3 mr-1" />Prescriptions ({prescriptions.length})</TabsTrigger>
          <TabsTrigger value="notes"><FileText className="w-3 h-3 mr-1" />Notes ({notes.length})</TabsTrigger>
          <TabsTrigger value="labs"><FlaskConical className="w-3 h-3 mr-1" />Lab Results ({labResults.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="symptoms" className="space-y-4">
          <SymptomTab patientId={patient.id} symptoms={symptoms} onChange={setSymptoms} />
        </TabsContent>
        <TabsContent value="diagnoses" className="space-y-4">
          <DiagnosisTab patientId={patient.id} diagnoses={diagnoses} onChange={setDiagnoses} />
        </TabsContent>
        <TabsContent value="prescriptions" className="space-y-4">
          <PrescriptionTab patientId={patient.id} prescriptions={prescriptions} onChange={setPrescriptions} />
        </TabsContent>
        <TabsContent value="notes" className="space-y-4">
          <NoteTab patientId={patient.id} notes={notes} onChange={setNotes} />
        </TabsContent>
        <TabsContent value="labs" className="space-y-4">
          <LabResultsTab patientId={patient.id} labResults={labResults} onChange={setLabResults} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─── Symptom Tab ─────────────────────────────────────────

function SymptomTab({ patientId, symptoms, onChange }: { patientId: string; symptoms: SymptomResponse[]; onChange: (s: SymptomResponse[]) => void }) {
  const { user } = useAuth();
  const canWrite = can.writeSymptom(user);
  const [open, setOpen] = useState(false);
  const [desc, setDesc] = useState("");
  const [severity, setSeverity] = useState("5");
  const [system, setSystem] = useState("");

  async function handleAdd() {
    try {
      const created = await createSymptom({ patient_id: patientId, description: desc, severity: Number(severity), body_system: system || undefined });
      onChange([created, ...symptoms]);
      setOpen(false); setDesc(""); setSeverity("5"); setSystem("");
      toast.success("Symptom added");
    } catch (err) {
      toast.error("Failed to add symptom", { description: err instanceof Error ? err.message : "" });
    }
  }

  async function handleDelete(sid: string) {
    try { await deleteSymptom(sid); onChange(symptoms.filter((s) => s.id !== sid)); toast.success("Symptom removed"); }
    catch (err) { toast.error("Failed to remove symptom"); }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Symptoms</CardTitle>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger><Button size="sm"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Symptom</DialogTitle></DialogHeader>
              <div className="space-y-3 py-2">
                <div className="space-y-1"><Label>Description</Label><Textarea value={desc} onChange={(e) => setDesc(e.target.value)} rows={2} /></div>
                <div className="space-y-1"><Label>Severity (1-10)</Label><Input type="number" min={1} max={10} value={severity} onChange={(e) => setSeverity(e.target.value)} /></div>
                <div className="space-y-1"><Label>Body System</Label><Input value={system} onChange={(e) => setSystem(e.target.value)} placeholder="e.g. Cardiovascular" /></div>
              </div>
              <DialogFooter><Button onClick={handleAdd} disabled={!desc.trim()}>Add</Button></DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {symptoms.length === 0 ? <p className="text-sm text-muted-foreground">No symptoms recorded.</p> : symptoms.map((s) => (
          <div key={s.id} className="flex items-center justify-between border rounded-lg p-3">
            <div>
              <p className="text-sm font-medium">{s.description}</p>
              <p className="text-xs text-muted-foreground">Severity {s.severity}/10 {s.body_system ? `· ${s.body_system}` : ""}</p>
            </div>
            {canWrite && (
              <Button variant="ghost" size="icon" onClick={() => handleDelete(s.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─── Diagnosis Tab ───────────────────────────────────────

function DiagnosisTab({ patientId, diagnoses, onChange }: { patientId: string; diagnoses: DiagnosisResponse[]; onChange: (d: DiagnosisResponse[]) => void }) {
  const { user } = useAuth();
  const canWrite = can.writeDiagnosis(user);
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState("provisional");

  async function handleAdd() {
    try {
      const created = await createDiagnosis({ patient_id: patientId, icd10_code: code, name, status });
      onChange([created, ...diagnoses]);
      setOpen(false); setCode(""); setName(""); setStatus("provisional");
      toast.success("Diagnosis added");
    } catch (err) {
      toast.error("Failed to add diagnosis", { description: err instanceof Error ? err.message : "" });
    }
  }

  async function handleDelete(did: string) {
    try { await deleteDiagnosis(did); onChange(diagnoses.filter((d) => d.id !== did)); toast.success("Diagnosis removed"); }
    catch (err) { toast.error("Failed to remove diagnosis"); }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Diagnoses</CardTitle>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger><Button size="sm"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Diagnosis</DialogTitle></DialogHeader>
              <div className="space-y-3 py-2">
                <div className="space-y-1"><Label>ICD-10 Code</Label><Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="I10" /></div>
                <div className="space-y-1"><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Hypertension" /></div>
                <div className="space-y-1"><Label>Status</Label>
                  <Select value={status} onValueChange={(v) => setStatus(v ?? "provisional")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="provisional">Provisional</SelectItem>
                      <SelectItem value="confirmed">Confirmed</SelectItem>
                      <SelectItem value="ruled_out">Ruled Out</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter><Button onClick={handleAdd} disabled={!code.trim() || !name.trim()}>Add</Button></DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {diagnoses.length === 0 ? <p className="text-sm text-muted-foreground">No diagnoses recorded.</p> : diagnoses.map((d) => (
          <div key={d.id} className="flex items-center justify-between border rounded-lg p-3">
            <div>
              <p className="text-sm font-medium">{d.name} <Badge variant="outline" className="ml-1">{d.icd10_code}</Badge></p>
              <p className="text-xs text-muted-foreground">Status: {d.status}</p>
            </div>
            {canWrite && (
              <Button variant="ghost" size="icon" onClick={() => handleDelete(d.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─── Prescription Tab ────────────────────────────────────

function PrescriptionTab({ patientId, prescriptions, onChange }: { patientId: string; prescriptions: PrescriptionResponse[]; onChange: (p: PrescriptionResponse[]) => void }) {
  const { user } = useAuth();
  const canWrite = can.writePrescription(user);
  const [open, setOpen] = useState(false);
  const [med, setMed] = useState("");
  const [dosage, setDosage] = useState("");
  const [freq, setFreq] = useState("");
  const [route, setRoute] = useState("oral");

  async function handleAdd() {
    try {
      const created = await createPrescription({
        patient_id: patientId, medication_name: med, dosage, frequency: freq, route,
        start_date: new Date().toISOString().split("T")[0],
      });
      onChange([created, ...prescriptions]);
      setOpen(false); setMed(""); setDosage(""); setFreq(""); setRoute("oral");
      toast.success("Prescription added");
    } catch (err) {
      toast.error("Failed to add prescription", { description: err instanceof Error ? err.message : "" });
    }
  }

  async function handleDelete(pid: string) {
    try { await deletePrescription(pid); onChange(prescriptions.filter((p) => p.id !== pid)); toast.success("Prescription removed"); }
    catch (err) { toast.error("Failed to remove prescription"); }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Prescriptions</CardTitle>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger><Button size="sm"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Prescription</DialogTitle></DialogHeader>
              <div className="space-y-3 py-2">
                <div className="space-y-1"><Label>Medication</Label><Input value={med} onChange={(e) => setMed(e.target.value)} placeholder="Lisinopril" /></div>
                <div className="space-y-1"><Label>Dosage</Label><Input value={dosage} onChange={(e) => setDosage(e.target.value)} placeholder="10 mg" /></div>
                <div className="space-y-1"><Label>Frequency</Label><Input value={freq} onChange={(e) => setFreq(e.target.value)} placeholder="Once daily" /></div>
                <div className="space-y-1"><Label>Route</Label>
                  <Select value={route} onValueChange={(v) => setRoute(v ?? "oral")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="oral">Oral</SelectItem>
                      <SelectItem value="iv">IV</SelectItem>
                      <SelectItem value="im">IM</SelectItem>
                      <SelectItem value="subcutaneous">Subcutaneous</SelectItem>
                      <SelectItem value="topical">Topical</SelectItem>
                      <SelectItem value="inhalation">Inhalation</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter><Button onClick={handleAdd} disabled={!med.trim() || !dosage.trim() || !freq.trim()}>Add</Button></DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {prescriptions.length === 0 ? <p className="text-sm text-muted-foreground">No prescriptions recorded.</p> : prescriptions.map((p) => (
          <div key={p.id} className="flex items-center justify-between border rounded-lg p-3">
            <div>
              <p className="text-sm font-medium">{p.medication_name} <Badge variant="outline" className="ml-1">{p.status}</Badge></p>
              <p className="text-xs text-muted-foreground">{p.dosage} · {p.frequency} · {p.route}</p>
            </div>
            {canWrite && (
              <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─── Note Tab ────────────────────────────────────────────

function NoteTab({ patientId, notes, onChange }: { patientId: string; notes: ClinicalNoteResponse[]; onChange: (n: ClinicalNoteResponse[]) => void }) {
  const { user } = useAuth();
  const canWrite = can.writeNote(user);
  const [open, setOpen] = useState(false);
  const [noteType, setNoteType] = useState("progress");
  const [content, setContent] = useState("");

  async function handleAdd() {
    try {
      const created = await createNote({ patient_id: patientId, note_type: noteType, content });
      onChange([created, ...notes]);
      setOpen(false); setNoteType("progress"); setContent("");
      toast.success("Note added");
    } catch (err) {
      toast.error("Failed to add note", { description: err instanceof Error ? err.message : "" });
    }
  }

  async function handleDelete(nid: string) {
    try { await deleteNote(nid); onChange(notes.filter((n) => n.id !== nid)); toast.success("Note removed"); }
    catch (err) { toast.error("Failed to remove note"); }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Clinical Notes</CardTitle>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger><Button size="sm"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Clinical Note</DialogTitle></DialogHeader>
              <div className="space-y-3 py-2">
                <div className="space-y-1"><Label>Note Type</Label>
                  <Select value={noteType} onValueChange={(v) => setNoteType(v ?? "progress")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="progress">Progress</SelectItem>
                      <SelectItem value="admission">Admission</SelectItem>
                      <SelectItem value="discharge">Discharge</SelectItem>
                      <SelectItem value="procedure">Procedure</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1"><Label>Content</Label><Textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} /></div>
              </div>
              <DialogFooter><Button onClick={handleAdd} disabled={!content.trim()}>Add</Button></DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {notes.length === 0 ? <p className="text-sm text-muted-foreground">No notes recorded.</p> : notes.map((n) => (
          <div key={n.id} className="flex items-start justify-between border rounded-lg p-3">
            <div className="flex-1">
              <p className="text-sm font-medium flex items-center gap-2">
                <Badge variant="outline">{n.note_type}</Badge>
                <span className="text-xs text-muted-foreground">{new Date(n.created_at).toLocaleDateString()}</span>
              </p>
              <p className="text-sm text-muted-foreground mt-1 whitespace-pre-wrap">{n.content}</p>
            </div>
            {canWrite && (
              <Button variant="ghost" size="icon" onClick={() => handleDelete(n.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─── Lab Results Tab ─────────────────────────────────────

function isAbnormal(value: string, range: string | null): boolean {
  if (!range) return false;
  const num = Number(value);
  if (!Number.isFinite(num)) return false;
  // Common reference-range formats: "70-110", "<6.5", ">40"
  const dash = range.match(/^([\d.]+)\s*-\s*([\d.]+)$/);
  if (dash) {
    return num < Number(dash[1]) || num > Number(dash[2]);
  }
  const lt = range.match(/^<\s*([\d.]+)$/);
  if (lt) return num >= Number(lt[1]);
  const gt = range.match(/^>\s*([\d.]+)$/);
  if (gt) return num <= Number(gt[1]);
  return false;
}

function LabResultsTab({
  patientId,
  labResults,
  onChange,
}: {
  patientId: string;
  labResults: LabResultResponse[];
  onChange: (l: LabResultResponse[]) => void;
}) {
  const { user } = useAuth();
  const canWrite = can.writeLabResult(user);
  const [open, setOpen] = useState(false);
  const [testName, setTestName] = useState("");
  const [category, setCategory] = useState("Chemistry");
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("");
  const [range, setRange] = useState("");
  const [status, setStatus] = useState("final");

  async function handleAdd() {
    try {
      const now = new Date().toISOString();
      const created = await createLabResult({
        patient_id: patientId,
        test_name: testName,
        test_category: category,
        result_value: value,
        unit: unit || undefined,
        reference_range: range || undefined,
        status,
        ordered_at: now,
        resulted_at: status === "pending" ? undefined : now,
      });
      onChange([created, ...labResults]);
      setOpen(false);
      setTestName(""); setValue(""); setUnit(""); setRange("");
      setCategory("Chemistry"); setStatus("final");
      toast.success("Lab result added");
    } catch (err) {
      toast.error("Failed to add lab result", {
        description: err instanceof Error ? err.message : "",
      });
    }
  }

  async function handleDelete(lid: string) {
    try {
      await deleteLabResult(lid);
      onChange(labResults.filter((l) => l.id !== lid));
      toast.success("Lab result removed");
    } catch (err) {
      toast.error("Failed to remove lab result");
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Lab Results</CardTitle>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger><Button size="sm"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Add Lab Result</DialogTitle></DialogHeader>
              <div className="space-y-3 py-2">
                <div className="space-y-1"><Label>Test Name</Label><Input value={testName} onChange={(e) => setTestName(e.target.value)} placeholder="Hemoglobin A1c" /></div>
                <div className="space-y-1"><Label>Category</Label>
                  <Select value={category} onValueChange={(v) => setCategory(v ?? "Chemistry")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Chemistry">Chemistry</SelectItem>
                      <SelectItem value="Hematology">Hematology</SelectItem>
                      <SelectItem value="Microbiology">Microbiology</SelectItem>
                      <SelectItem value="Immunology">Immunology</SelectItem>
                      <SelectItem value="Urinalysis">Urinalysis</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1"><Label>Result</Label><Input value={value} onChange={(e) => setValue(e.target.value)} placeholder="7.2" /></div>
                  <div className="space-y-1"><Label>Unit</Label><Input value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="%" /></div>
                </div>
                <div className="space-y-1"><Label>Reference Range</Label><Input value={range} onChange={(e) => setRange(e.target.value)} placeholder="70-110 or <6.5" /></div>
                <div className="space-y-1"><Label>Status</Label>
                  <Select value={status} onValueChange={(v) => setStatus(v ?? "final")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="preliminary">Preliminary</SelectItem>
                      <SelectItem value="final">Final</SelectItem>
                      <SelectItem value="corrected">Corrected</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter><Button onClick={handleAdd} disabled={!testName.trim() || !value.trim()}>Add</Button></DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {labResults.length === 0 ? (
          <p className="text-sm text-muted-foreground">No lab results recorded.</p>
        ) : (
          labResults.map((l) => {
            const abnormal = isAbnormal(l.result_value, l.reference_range);
            return (
              <div key={l.id} className="flex items-center justify-between border rounded-lg p-3">
                <div className="flex-1">
                  <p className="text-sm font-medium flex items-center gap-2">
                    {l.test_name}
                    <Badge variant="outline">{l.test_category}</Badge>
                    <Badge variant={l.status === "final" ? "default" : "secondary"}>{l.status}</Badge>
                  </p>
                  <p className={`text-sm mt-1 ${abnormal ? "text-destructive font-semibold" : "text-muted-foreground"}`}>
                    {l.result_value}{l.unit ? ` ${l.unit}` : ""}
                    {l.reference_range && (
                      <span className="text-xs ml-2">(ref: {l.reference_range})</span>
                    )}
                    {abnormal && <span className="text-xs ml-2 uppercase">⚠ out of range</span>}
                  </p>
                </div>
                {canWrite && (
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(l.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
                )}
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
