"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  AppointmentResponse,
  PatientResponse,
  Provider,
  createAppointment,
  deleteAppointment,
  listAppointments,
  listPatients,
  listProviders,
  updateAppointment,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Calendar, Plus, Trash2 } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-800 border-blue-300",
  completed: "bg-emerald-100 text-emerald-800 border-emerald-300",
  cancelled: "bg-gray-100 text-gray-700 border-gray-300",
  no_show: "bg-red-100 text-red-800 border-red-300",
};

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function AppointmentsPage() {
  const { user } = useAuth();
  const canWrite = can.writeAppointment(user);

  const [date, setDate] = useState(todayISO());
  const [appts, setAppts] = useState<AppointmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);

  const [open, setOpen] = useState(false);
  const [patientId, setPatientId] = useState("");
  const [providerId, setProviderId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [duration, setDuration] = useState("30");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([listPatients(), listProviders()])
      .then(([ps, prs]) => {
        setPatients(ps);
        setProviders(prs);
      })
      .catch((err) =>
        toast.error("Failed to load reference data", {
          description: err instanceof Error ? err.message : "",
        }),
      );
  }, []);

  useEffect(() => {
    setLoading(true);
    listAppointments({ date })
      .then(setAppts)
      .catch((err) =>
        toast.error("Failed to load appointments", {
          description: err instanceof Error ? err.message : "",
        }),
      )
      .finally(() => setLoading(false));
  }, [date]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const created = await createAppointment({
        patient_id: patientId,
        provider_id: providerId,
        scheduled_at: new Date(scheduledAt).toISOString(),
        duration_minutes: Number(duration),
        location: location || undefined,
        notes: notes || undefined,
      });
      // If the new appointment falls on the current date filter, prepend
      if (created.scheduled_at.startsWith(date)) {
        setAppts((prev) => [...prev, created].sort((a, b) =>
          a.scheduled_at.localeCompare(b.scheduled_at),
        ));
      }
      setOpen(false);
      setPatientId(""); setProviderId(""); setScheduledAt("");
      setDuration("30"); setLocation(""); setNotes("");
      toast.success("Appointment scheduled");
    } catch (err) {
      toast.error("Failed to schedule", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusChange(id: string, status: string) {
    try {
      const updated = await updateAppointment(id, { status });
      setAppts((prev) => prev.map((a) => (a.id === id ? updated : a)));
      toast.success(`Marked ${status.replace("_", " ")}`);
    } catch (err) {
      toast.error("Failed to update", {
        description: err instanceof Error ? err.message : "",
      });
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteAppointment(id);
      setAppts((prev) => prev.filter((a) => a.id !== id));
      toast.success("Appointment deleted");
    } catch (err) {
      toast.error("Failed to delete");
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Calendar className="w-6 h-6 text-primary" />
            Appointments
          </h1>
          <p className="text-muted-foreground">Schedule and view patient appointments.</p>
        </div>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Appointment
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Schedule Appointment</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-3 py-2">
                <div className="space-y-1">
                  <Label>Patient</Label>
                  <Select value={patientId} onValueChange={(v) => setPatientId(v ?? "")}>
                    <SelectTrigger><SelectValue placeholder="Select patient" /></SelectTrigger>
                    <SelectContent>
                      {patients.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.name} ({p.medical_record_number})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Provider</Label>
                  <Select value={providerId} onValueChange={(v) => setProviderId(v ?? "")}>
                    <SelectTrigger><SelectValue placeholder="Select provider" /></SelectTrigger>
                    <SelectContent>
                      {providers.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.full_name} · {p.role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label>Date & Time</Label>
                    <Input
                      type="datetime-local"
                      value={scheduledAt}
                      onChange={(e) => setScheduledAt(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Duration (min)</Label>
                    <Input
                      type="number"
                      min={5}
                      max={480}
                      value={duration}
                      onChange={(e) => setDuration(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label>Location</Label>
                  <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Clinic Room 1" />
                </div>
                <div className="space-y-1">
                  <Label>Notes</Label>
                  <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
                </div>
                <DialogFooter>
                  <Button
                    type="submit"
                    disabled={!patientId || !providerId || !scheduledAt || submitting}
                  >
                    {submitting ? "Scheduling…" : "Schedule"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-end gap-3">
            <div className="space-y-1">
              <Label>Date</Label>
              <Input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            <Button variant="outline" onClick={() => setDate(todayISO())}>
              Today
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        {loading ? (
          <CardContent className="p-6 space-y-2">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </CardContent>
        ) : appts.length === 0 ? (
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            No appointments scheduled for this day.
          </CardContent>
        ) : (
          <CardContent className="space-y-2 pt-6">
            {appts.map((a) => {
              const patient = patients.find((p) => p.id === a.patient_id);
              const provider = providers.find((p) => p.id === a.provider_id);
              const dt = new Date(a.scheduled_at);
              return (
                <div
                  key={a.id}
                  className="flex items-center justify-between border rounded-lg p-3"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium font-mono">
                        {dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <span className="text-sm">·</span>
                      <span className="text-sm font-medium">
                        {patient ? patient.name : `Patient ${a.patient_id.slice(0, 8)}…`}
                      </span>
                      <Badge className={STATUS_COLORS[a.status] || ""}>
                        {a.status.replace("_", " ")}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {provider ? provider.full_name : "—"} · {a.duration_minutes} min
                      {a.location ? ` · ${a.location}` : ""}
                    </p>
                    {a.notes && (
                      <p className="text-xs text-muted-foreground mt-1 italic">{a.notes}</p>
                    )}
                  </div>
                  {canWrite && (
                    <div className="flex items-center gap-1">
                      {a.status === "scheduled" && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(a.id, "completed")}
                          >
                            Complete
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(a.id, "no_show")}
                          >
                            No-show
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(a.id, "cancelled")}
                          >
                            Cancel
                          </Button>
                        </>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(a.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
