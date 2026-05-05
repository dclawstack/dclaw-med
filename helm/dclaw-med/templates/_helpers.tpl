{{/* Generate chart name */}}
{{- define "dclaw-med.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Create fullname */}}
{{- define "dclaw-med.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels */}}
{{- define "dclaw-med.labels" -}}
helm.sh/chart: {{ include "dclaw-med.name" . }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "dclaw-med.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels */}}
{{- define "dclaw-med.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dclaw-med.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
