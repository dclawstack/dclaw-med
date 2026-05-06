# Common Issues

## App won't start

**Symptoms:** Pods in `CrashLoopBackOff` or `Error` state.

**Solutions:**

```bash
# Check logs
kubectl logs -n dclaw-med deployment/dclaw-med-backend

# Check events
kubectl get events -n dclaw-med --sort-by='.lastTimestamp'

# Verify database connection
kubectl exec -n dclaw-med deployment/dclaw-med-backend --   python -c "import asyncio; from sqlalchemy import text; ..."
```

## Database connection errors

**Symptoms:** Backend logs show `connection refused` or `timeout`.

**Solutions:**

1. Verify the database cluster is ready:
   ```bash
   kubectl get clusters -n dclaw-med
   ```

2. Check the connection string secret:
   ```bash
   kubectl get secret dclaw-med-db-credentials -n dclaw-med
   ```

## Frontend can't reach backend

**Symptoms:** Browser console shows CORS errors or 502 Bad Gateway.

**Solutions:**

1. Verify backend pod is running
2. Check ingress configuration
3. Verify `NEXT_PUBLIC_API_URL` is set correctly
