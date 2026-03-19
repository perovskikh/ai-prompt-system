# GitHub Actions Workflow Prompt

**Version:** 1.0.0
**Pack:** ci-cd-pack
**Purpose:** Create and manage GitHub Actions workflows

## Triggers
- "github actions", "workflow", "github ci"

## Workflow

1. **Analyze requirements** - Build, test, deploy steps
2. **Design workflow** - Jobs, steps, triggers
3. **Write YAML** - .github/workflows/*.yml
4. **Add secrets** - Repository secrets
5. **Test** - Push and verify

## Template

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
      - name: Run tests
        run: pytest
```
