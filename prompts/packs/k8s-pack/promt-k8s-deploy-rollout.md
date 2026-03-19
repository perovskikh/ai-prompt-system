# K8s Deploy Rollout Prompt

**Version:** 1.0.0
**Pack:** k8s-pack
**Purpose:** Kubernetes deployment and rollout management

## Triggers
- "деплой", "deploy", "rollout", "выкатить"

## Workflow

1. **Validate manifests** - Check YAML syntax
2. **Check prerequisites** - Namespace exists, resources available
3. **Apply** - kubectl apply or helm upgrade
4. **Verify** - Check rollout status
5. **Monitor** - Watch for issues

## Example

```bash
# Deploy to staging
kubectl apply -f k8s/staging/

# Check rollout
kubectl rollout status deployment/my-app -n staging
```
