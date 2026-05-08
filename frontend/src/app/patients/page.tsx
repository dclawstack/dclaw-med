"use client";

import { useEffect, useState } from "react";
import {
  listPatients,
  createPatient,
  deletePatient,
  PatientResponse,
  PatientCreate,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import Link from "next/link";
import { Database, Plus, Trash2, Users, Eye } from "lucide-react";

export default function PatientsPage() {
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [gender, setGender] = useState("male");
  const [mrn, setMrn] = useState("");
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await listPatients();
      setPatients(data);
    } catch (err) {
      toast.error("Failed to load patients", { description: err instanceof Error ? err.message : "" });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !dob || !mrn.trim()) return;
    setCreating(true);
    try {
      const created = await createPatient({
        name: name.trim(),
        date_of_birth: dob,
        gender: gender as "male" | "female" | "other" | "unknown",
        medical_record_number: mrn.trim(),
      });
      setPatients((prev) => [...prev, created]);
      toast.success("Patient created", { description: created.name });
      setName(""); setDob(""); setMrn(""); setGender("male"); setDialogOpen(false);
    } catch (err) {
      toast.error("Failed to create patient", { description: err instanceof Error ? err.message : "" });
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deletePatient(id);
      setPatients((prev) => prev.filter((p) => p.id !== id));
      toast.success("Patient deleted");
    } catch (err) {
      toast.error("Failed to delete patient");
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-primary" />
            Patients
          </h1>
          <p className="text-muted-foreground">Manage patient records and medical history.</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger>
            <Button><Plus className="w-4 h-4 mr-2" />New Patient</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Patient</DialogTitle>
              <DialogDescription>Register a new patient in the system.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-3 py-3">
              <div className="space-y-1">
                <Label htmlFor="p-name">Full Name</Label>
                <Input id="p-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" required />
              </div>
              <div className="space-y-1">
                <Label htmlFor="p-dob">Date of Birth</Label>
                <Input id="p-dob" type="date" value={dob} onChange={(e) => setDob(e.target.value)} required />
              </div>
              <div className="space-y-1">
                <Label>Gender</Label>
                <Select value={gender} onValueChange={(v) => setGender(v ?? "male")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="unknown">Unknown</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label htmlFor="p-mrn">Medical Record Number</Label>
                <Input id="p-mrn" value={mrn} onChange={(e) => setMrn(e.target.value)} placeholder="MRN-2026-0001" required />
              </div>
              <DialogFooter>
                <Button type="submit" disabled={creating}>{creating ? "Creating..." : "Create"}</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        {loading ? (
          <CardContent className="p-6 space-y-2"><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /></CardContent>
        ) : patients.length === 0 ? (
          <CardContent className="p-8 text-center space-y-3">
            <Users className="w-10 h-10 text-muted-foreground mx-auto" />
            <p className="text-sm text-muted-foreground">No patients yet. Create your first patient.</p>
            <Button onClick={() => setDialogOpen(true)}><Plus className="w-4 h-4 mr-2" />Create Patient</Button>
          </CardContent>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>MRN</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Gender</TableHead>
                <TableHead>Date of Birth</TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patients.map((p) => (
                <TableRow key={p.id}>
                  <TableCell><Badge variant="secondary">{p.medical_record_number}</Badge></TableCell>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell className="capitalize">{p.gender}</TableCell>
                  <TableCell>{p.date_of_birth}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Link href={`/patients/${p.id}`}>
                        <Button variant="ghost" size="icon"><Eye className="w-4 h-4" /></Button>
                      </Link>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)}>
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
