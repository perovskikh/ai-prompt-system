# K8s Helm Upgrade Prompt

**Version:** 1.0.0
**Pack:** k8s-pack
**Purpose:** Helm chart upgrades and rollbacks

## Triggers
- "helm", "upgrade", "rollback", "release"

## Workflow

1. **Backup current** - helm get values
2. **Dry run** - helm upgrade --dry-run
3. **Upgrade** - helm upgrade
4. **Verify** - helm status
5. **Rollback if needed** - helm rollback

## Commands

```bash
# Dry run first
helm upgrade my-app ./chart --dry-run --debug -n namespace

# Upgrade
helm upgrade my-app ./chart -f values.yaml -n namespace

# Rollback
helm rollback my-app 1 -n namespace
```
