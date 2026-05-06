# Troubleshooting

Common issues and solutions for DClaw Med.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-med

# Check logs
kubectl logs -n dclaw-med deployment/dclaw-med-backend

# Check database
kubectl get clusters -n dclaw-med
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
