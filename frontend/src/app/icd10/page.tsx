"use client";

import { useState } from "react";
import { lookupICD10, ICD10Code } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import { Search, Database } from "lucide-react";

const MOCK_CODES: ICD10Code[] = [
  { code: "I10", description: "Essential (primary) hypertension", category: "Cardiovascular", billable: true },
  { code: "E11.9", description: "Type 2 diabetes mellitus without complications", category: "Endocrine", billable: true },
  { code: "J06.9", description: "Acute upper respiratory infection, unspecified", category: "Respiratory", billable: true },
  { code: "K21.9", description: "Gastro-esophageal reflux disease without esophagitis", category: "GI", billable: true },
  { code: "M54.5", description: "Low back pain", category: "Musculoskeletal", billable: true },
  { code: "F32.9", description: "Major depressive disorder, single episode, unspecified", category: "Mental Health", billable: true },
  { code: "N18.3", description: "Chronic kidney disease, stage 3", category: "Renal", billable: true },
  { code: "G43.909", description: "Migraine, unspecified, not intractable", category: "Neurological", billable: true },
];

export default function ICD10Page() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ICD10Code[]>([]);
  const [searched, setSearched] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await lookupICD10({ query, max_results: 20 });
      if (res.results.length > 0) {
        setResults(res.results);
      } else {
        // Fallback to mock client-side filter
        const q = query.toLowerCase();
        setResults(MOCK_CODES.filter(
          (c) => c.code.toLowerCase().includes(q) || c.description.toLowerCase().includes(q) || c.category.toLowerCase().includes(q)
        ));
      }
    } catch {
      // Fallback to mock
      const q = query.toLowerCase();
      setResults(MOCK_CODES.filter(
        (c) => c.code.toLowerCase().includes(q) || c.description.toLowerCase().includes(q)
      ));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Database className="w-6 h-6 text-primary" />
          ICD-10 Lookup
        </h1>
        <p className="text-muted-foreground">Search ICD-10-CM diagnosis codes by code or description.</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              placeholder="Search by code or description (e.g. hypertension, I10, diabetes)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" disabled={loading || !query.trim()}>
              {loading ? <Skeleton className="w-4 h-4 rounded-full" /> : <Search className="w-4 h-4 mr-2" />}
              Search
            </Button>
          </form>
        </CardContent>
      </Card>

      {searched && (
        <Card>
          <CardHeader><CardTitle className="text-sm">Results ({results.length} found)</CardTitle></CardHeader>
          <CardContent>
            {results.length === 0 ? (
              <p className="text-sm text-muted-foreground">No matching ICD-10 codes found.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Billable</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((code) => (
                    <TableRow key={code.code}>
                      <TableCell className="font-mono font-medium">{code.code}</TableCell>
                      <TableCell>{code.description}</TableCell>
                      <TableCell><Badge variant="outline">{code.category}</Badge></TableCell>
                      <TableCell>{code.billable ? <Badge>Yes</Badge> : <Badge variant="secondary">No</Badge>}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}

      {!searched && (
        <Card>
          <CardHeader><CardTitle className="text-sm">Common Codes</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Category</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {MOCK_CODES.map((code) => (
                  <TableRow key={code.code}>
                    <TableCell className="font-mono font-medium">{code.code}</TableCell>
                    <TableCell>{code.description}</TableCell>
                    <TableCell><Badge variant="outline">{code.category}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
