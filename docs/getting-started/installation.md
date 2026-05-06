# Installation

## Via DPanel

1. Open DPanel at `https://panel.yourdomain.com`
2. Find **DClaw Med** in the app grid
3. Click **Install**
4. The DClaw Operator will provision:
   - Namespace: `dclaw-med`
   - Frontend deployment (Next.js)
   - Backend deployment (FastAPI)
   - PostgreSQL database (CloudNativePG)
   - Ingress with TLS

## Via kubectl

```bash
# Apply the DClawApp CRD
kubectl apply -f - <<EOF
apiVersion: platform.dclaw.io/v1
kind: DClawApp
metadata:
  name: med
spec:
  appId: med
  appName: DClaw Med
  version: 0.1.0
  category: healthcare
  enabled: true
  frontend:
    image: ghcr.io/dclawstack/dclaw-med:latest
    replicas: 2
  backend:
    image: ghcr.io/dclawstack/dclaw-med-backend:latest
    replicas: 2
  database:
    enabled: true
    storage: 10Gi
  ingress:
    enabled: true
    host: med.yourdomain.com
    tls: true
EOF
```

## Verify

```bash
kubectl get pods -n dclaw-med
kubectl get ingress -n dclaw-med
```
