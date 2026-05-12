"use client";

import { useEffect, useState } from "react";
import { listPrescriptions, deletePrescription, PrescriptionResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Pill, Trash2 } from "lucide-react";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";

export default function PrescriptionsPage() {
  const { user } = useAuth();
  const canWrite = can.writePrescription(user);
  const [prescriptions, setPrescriptions] = useState<PrescriptionResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await listPrescriptions();
      setPrescriptions(data);
    } catch (err) {
      toast.error("Failed to load prescriptions", { description: err instanceof Error ? err.message : "" });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deletePrescription(id);
      setPrescriptions((prev) => prev.filter((p) => p.id !== id));
      toast.success("Prescription deleted");
    } catch (err) {
      toast.error("Failed to delete prescription");
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Pill className="w-6 h-6 text-primary" />
          Prescriptions
        </h1>
        <p className="text-muted-foreground">View and manage all prescriptions.</p>
      </div>

      <Card>
        {loading ? (
          <CardContent className="p-6 space-y-2"><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /></CardContent>
        ) : prescriptions.length === 0 ? (
          <CardContent className="p-8 text-center text-sm text-muted-foreground">No prescriptions yet. Add prescriptions from a patient record.</CardContent>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Medication</TableHead>
                <TableHead>Dosage</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {prescriptions.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.medication_name}</TableCell>
                  <TableCell>{p.dosage}</TableCell>
                  <TableCell>{p.frequency}</TableCell>
                  <TableCell className="capitalize">{p.route}</TableCell>
                  <TableCell><Badge variant={p.status === "active" ? "default" : "secondary"}>{p.status}</Badge></TableCell>
                  <TableCell>
                    {canWrite && (
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
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
