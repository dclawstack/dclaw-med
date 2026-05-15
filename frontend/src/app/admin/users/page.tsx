"use client";

import { useEffect, useState } from "react";
import {
  CurrentUser,
  PatientResponse,
  ApiError,
  listUsers,
  listPatients,
  linkUserToPatient,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import { Lock, Users, Link2, Link2Off } from "lucide-react";

export default function AdminUsersPage() {
  const { user } = useAuth();
  const isAdmin = can.viewAudit(user); // admin-only flag already defined
  const [users, setUsers] = useState<CurrentUser[]>([]);
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [linkOpenFor, setLinkOpenFor] = useState<CurrentUser | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<string>("");

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
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Users className="w-6 h-6 text-primary" />
          Patient accounts
        </h1>
        <p className="text-sm text-muted-foreground">
          Link each patient-role login to its corresponding patient record so
          the portal can show their data.
        </p>
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
