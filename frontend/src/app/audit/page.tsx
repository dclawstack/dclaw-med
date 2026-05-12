"use client";

import { useEffect, useState } from "react";
import { AuditLog, listAuditLogs } from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
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
import { Lock, ShieldCheck } from "lucide-react";

const ENTITY_OPTIONS = [
  "patients",
  "symptoms",
  "diagnoses",
  "prescriptions",
  "notes",
  "icd10",
  "drug",
];
const ACTION_OPTIONS = ["create", "read", "update", "delete"];

export default function AuditPage() {
  const { user } = useAuth();
  const canView = can.viewAudit(user);

  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [entityType, setEntityType] = useState("");
  const [action, setAction] = useState("");
  const [userId, setUserId] = useState("");

  useEffect(() => {
    if (!canView) {
      setLoading(false);
      return;
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canView]);

  async function load() {
    setLoading(true);
    try {
      const data = await listAuditLogs({
        entity_type: entityType || undefined,
        action: action || undefined,
        user_id: userId || undefined,
        page_size: 100,
      });
      setLogs(data);
    } catch (err) {
      toast.error("Failed to load audit logs", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setLoading(false);
    }
  }

  if (!canView) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
            <Lock className="w-6 h-6" />
            Audit trail is restricted to administrators.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-primary" />
          Audit Trail
        </h1>
        <p className="text-muted-foreground">
          Append-only log of every authenticated medical-record access.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="space-y-1">
              <Label>Entity</Label>
              <Select
                value={entityType || "all"}
                onValueChange={(v) => setEntityType(!v || v === "all" ? "" : v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  {ENTITY_OPTIONS.map((e) => (
                    <SelectItem key={e} value={e}>
                      {e}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Action</Label>
              <Select
                value={action || "all"}
                onValueChange={(v) => setAction(!v || v === "all" ? "" : v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  {ACTION_OPTIONS.map((a) => (
                    <SelectItem key={a} value={a}>
                      {a}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>User ID</Label>
              <Input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="optional UUID"
              />
            </div>
            <div className="space-y-1 flex items-end">
              <Button onClick={load} className="w-full">
                Apply filters
              </Button>
            </div>
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
        ) : logs.length === 0 ? (
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            No matching audit records.
          </CardContent>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Entity</TableHead>
                <TableHead>Entity ID</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono text-xs">
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {log.user_id.slice(0, 8)}…
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        log.action === "delete"
                          ? "destructive"
                          : log.action === "create"
                          ? "default"
                          : "secondary"
                      }
                    >
                      {log.action}
                    </Badge>
                  </TableCell>
                  <TableCell className="capitalize">{log.entity_type}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {log.entity_id ? `${log.entity_id.slice(0, 8)}…` : "—"}
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
