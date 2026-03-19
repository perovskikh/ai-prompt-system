# K8s Pod Debug Prompt

**Version:** 1.0.0
**Pack:** k8s-pack
**Purpose:** Debug Kubernetes pod issues (CrashLoopBackOff, Pending, etc.)

## Triggers
- "debug pod", "crashloop", "pending", "not ready"

## Workflow

1. **Get pod status** - kubectl get pods
2. **Check events** - kubectl describe pod
3. **Get logs** - kubectl logs (current & previous)
4. **Analyze** - Identify root cause
5. **Fix** - Apply solution

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| CrashLoopBackOff | App crash | Check logs, fix config |
| Pending | Resources | Request resources, scale down |
| ImagePullBackOff | Invalid image | Check image name, pull policy |
| NotReady | Liveness probe | Fix probe config |
