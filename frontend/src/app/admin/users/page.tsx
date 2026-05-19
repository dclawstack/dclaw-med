"use client";

import { useEffect, useState } from "react";
import {
  CurrentUser,
  PatientResponse,
  ApiError,
  UserCreateInput,
  listUsers,
  listPatients,
  linkUserToPatient,
  registerUser,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { Lock, Users, Link2, Link2Off, UserPlus } from "lucide-react";

type Role = UserCreateInput["role"];
const ROLES: Role[] = ["doctor", "nurse", "admin", "receptionist", "patient"];

interface NewUserDraft {
  email: string;
  password: string;
  full_name: string;
  role: Role;
  patient_id: string;
}

const EMPTY_DRAFT: NewUserDraft = {
  email: "",
  password: "",
  full_name: "",
  role: "doctor",
  patient_id: "",
};

export default function AdminUsersPage() {
  const { user } = useAuth();
  const isAdmin = can.viewAudit(user); // admin-only flag already defined
  const [users, setUsers] = useState<CurrentUser[]>([]);
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [linkOpenFor, setLinkOpenFor] = useState<CurrentUser | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<string>("");
  const [createOpen, setCreateOpen] = useState(false);
  const [draft, setDraft] = useState<NewUserDraft>(EMPTY_DRAFT);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  async function reload() {
    setLoading(true);
    try {
      const [u, p] = await Promise.all([
        listUsers("patient"),
        listPatients(1, 200),
      ]);
      setUsers(u);
      setPatients(p);
    } catch (err) {
      toast.error("Failed to load admin data", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleLink() {
    if (!linkOpenFor || !selectedPatient) return;
    try {
      await linkUserToPatient(linkOpenFor.id, selectedPatient);
      toast.success("Linked");
      setLinkOpenFor(null);
      setSelectedPatient("");
      reload();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Link failed", { description: msg });
    }
  }

  async function handleUnlink(u: CurrentUser) {
    try {
      await linkUserToPatient(u.id, null);
      toast.success("Unlinked");
      reload();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Unlink failed", { description: msg });
    }
  }

  function draftIsValid(d: NewUserDraft): boolean {
    if (!d.email.trim() || !d.password || !d.full_name.trim()) return false;
    if (d.role === "patient" && !d.patient_id) return false;
    return true;
  }

  async function handleCreate() {
    if (!draftIsValid(draft)) return;
    setCreating(true);
    try {
      const payload: UserCreateInput = {
        email: draft.email.trim(),
        password: draft.password,
        full_name: draft.full_name.trim(),
        role: draft.role,
        // Backend requires patient_id only for role=patient; omit otherwise.
        patient_id: draft.role === "patient" ? draft.patient_id : undefined,
      };
      const created = await registerUser(payload);
      toast.success("User created", {
        description: `${created.full_name} · ${created.role}`,
      });
      setCreateOpen(false);
      setDraft(EMPTY_DRAFT);
      // Reload so any new patient-role account appears in the linked table.
      reload();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Could not create user", { description: msg });
    } finally {
      setCreating(false);
    }
  }

  if (!isAdmin) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
            <Lock className="w-6 h-6" />
            Admin only.
          </CardContent>
        </Card>
      </div>
    );
  }

  function patientLabel(id: string | null): string {
    if (!id) return "—";
    const p = patients.find((x) => x.id === id);
    return p ? `${p.name} · ${p.medical_record_number}` : id.slice(0, 8) + "…";
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Users className="w-6 h-6 text-primary" />
            User accounts
          </h1>
          <p className="text-sm text-muted-foreground">
            Create clinician or patient logins. Patient-role accounts can also
            be linked to a chart from the table below.
          </p>
        </div>
        <Dialog
          open={createOpen}
          onOpenChange={(open) => {
            setCreateOpen(open);
            if (!open) setDraft(EMPTY_DRAFT);
          }}
        >
          <DialogTrigger>
            <Button size="sm">
              <UserPlus className="w-4 h-4 mr-2" />
              Add user
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create a new user</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-1.5">
                <Label htmlFor="new-user-email">Email</Label>
                <Input
                  id="new-user-email"
                  type="email"
                  autoComplete="off"
                  placeholder="clinician@clinic.example"
                  value={draft.email}
                  onChange={(e) =>
                    setDraft({ ...draft, email: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="new-user-name">Full name</Label>
                <Input
                  id="new-user-name"
                  autoComplete="off"
                  placeholder="Dr. Jane Stone"
                  value={draft.full_name}
                  onChange={(e) =>
                    setDraft({ ...draft, full_name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="new-user-password">Temporary password</Label>
                <Input
                  id="new-user-password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="At least 8 characters"
                  value={draft.password}
                  onChange={(e) =>
                    setDraft({ ...draft, password: e.target.value })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Share this with the user securely. Self-serve password reset
                  is on the v1.3 roadmap.
                </p>
              </div>
              <div className="space-y-1.5">
                <Label>Role</Label>
                <Select
                  value={draft.role}
                  onValueChange={(v) =>
                    setDraft({
                      ...draft,
                      role: v as Role,
                      patient_id: v === "patient" ? draft.patient_id : "",
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLES.map((r) => (
                      <SelectItem key={r} value={r}>
                        {r}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {draft.role === "patient" && (
                <div className="space-y-1.5">
                  <Label>Linked patient chart</Label>
                  <Select
                    value={draft.patient_id}
                    onValueChange={(v) =>
                      setDraft({ ...draft, patient_id: v ?? "" })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a patient…" />
                    </SelectTrigger>
                    <SelectContent>
                      {patients.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.name} · {p.medical_record_number}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    Patient logins are scoped to their own chart; this field is
                    required and validated by the backend.
                  </p>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button
                variant="ghost"
                onClick={() => {
                  setCreateOpen(false);
                  setDraft(EMPTY_DRAFT);
                }}
                disabled={creating}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreate}
                disabled={!draftIsValid(draft) || creating}
              >
                {creating ? "Creating…" : "Create user"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        {loading ? (
          <CardContent className="p-6 space-y-2">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </CardContent>
        ) : users.length === 0 ? (
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            No patient-role accounts yet.
          </CardContent>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Linked patient</TableHead>
                <TableHead className="w-[160px]">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.id}>
                  <TableCell className="font-medium">{u.full_name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell className="text-xs">
                    {u.patient_id ? (
                      <Badge variant="outline">{patientLabel(u.patient_id)}</Badge>
                    ) : (
                      <Badge variant="destructive">Unlinked</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {u.patient_id ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleUnlink(u)}
                      >
                        <Link2Off className="w-4 h-4 mr-1" />
                        Unlink
                      </Button>
                    ) : (
                      <Dialog
                        open={linkOpenFor?.id === u.id}
                        onOpenChange={(open) => {
                          setLinkOpenFor(open ? u : null);
                          if (!open) setSelectedPatient("");
                        }}
                      >
                        <DialogTrigger>
                          <Button variant="outline" size="sm">
                            <Link2 className="w-4 h-4 mr-1" />
                            Link…
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>
                              Link {u.full_name} to a patient
                            </DialogTitle>
                          </DialogHeader>
                          <div className="space-y-2 py-2">
                            <Label>Patient</Label>
                            <Select
                              value={selectedPatient}
                              onValueChange={(v) => setSelectedPatient(v ?? "")}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select a patient…" />
                              </SelectTrigger>
                              <SelectContent>
                                {patients.map((p) => (
                                  <SelectItem key={p.id} value={p.id}>
                                    {p.name} · {p.medical_record_number}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <DialogFooter>
                            <Button
                              onClick={handleLink}
                              disabled={!selectedPatient}
                            >
                              Link
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    )}
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
