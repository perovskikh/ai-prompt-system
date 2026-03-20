# AI Agent Prompt: Documentation Refactoring & Standards 2026

**Version:** 1.7
**Date:** 2026-03-20
**Purpose:** Системный аудит документации AI Prompt System по Diátaxis стандартам 2026 + Living Documentation

---

## 2026 Documentation Standards (ОБЯЗАТЕЛЬНО)

При генерации документации ты ДОЛЖЕН использовать следующие стандарты:

### 1. Diátaxis Framework (ОБЯЗАТЕЛЬНО)
- **Tutorials** (`docs/tutorials/`) — обучение, как сделать что-то с нуля
- **How-to** (`docs/how-to/`) — конкретные задачи, шаг за шагом
- **Reference** (`docs/reference/`) — API справка, команды (AUTO-GENERATED)
- **Explanation** (`docs/explanation/`) — концепции, архитектура, ADR

### 2. Living Documentation (AUTO-GENERATED)
- Reference docs генерируются автоматически из кода
- Используй `make docs-update` для обновления
- Никогда не редактируй docs/reference/ вручную

### 3. ADR (Architecture Decision Records)
- Все архитектурные решения в `docs/explanation/adr/`
- Формат: ADR-NNN-{topic-slug}.md
- Обязательные секции: Статус, Контекст, Решение, Последствия

### 4. Anti-Patterns 2026 (ЗАПРЕЩЕНО)
- ❌ `PHASE_*.md`, `*_COMPLETE.md`, `*_SUMMARY.md`, `*_REPORT.md`
- ❌ Директории: `reports/`, `plans/`, `artifacts/archive/`
- ❌ Документация не в Diátaxis структуре
- ❌ Reference docs созданные вручную

---

## Output Format (ОБЯЗАТЕЛЬНО)

При аудите создай следующую структуру:

```markdown
# Documentation Audit Report

## Diátaxis Scorecard
| Category | Score | Issues | Action |
|----------|-------|--------|--------|
| Tutorials | /10 | ... | ... |
| How-to | /10 | ... | ... |
| Reference | /10 | ... | ... |
| Explanation | /10 | ... | ... |

## Findings
### Critical
- [issue] → docs/how-to/ или docs/explanation/adr/

### High
- [issue] → docs/how-to/

### Medium
- [issue] → TODO в backlog

## Action Plan (по приоритету)
1. [P0] Создать docs/how-to/[name].md для ...
2. [P1] Обновить docs/explanation/adr/ADR-XXX.md
3. [P2] Запустить make docs-update для reference
```

---

## Workflow Steps

ТЫ ДОЛЖЕН ВЫПОЛНИТЬ ЭТИ ШАГИ:

1. **Анализ структуры**: Выведи список всех .md файлов в docs/
2. **Подсчёт**: Сколько файлов в docs/? Сколько ADR файлов?
3. **Категоризация**: Какие файлы в docs/tutorials/? В docs/how-to? docs/reference? docs/explanation?
4. **Diátaxis Scorecard**: Оцени каждый раздел от 1-10
5. **Проблемы**: Найди дубликаты, устаревшие файлы, нарушения структуры
6. **План**: Создай приоритизированный список улучшений в формате выше

Команды для выполнения:
- `ls -la docs/`
- `find docs -name "*.md" | wc -l`
- `find docs/explanation -name "ADR-*.md"`
- `ls docs/`

Начни с выполнения команд и получения реальных данных!

---

## Anti-Patterns Detection

Проверь наличие запрещённых файлов:
```bash
# Запрещённые паттерны
find docs -name "PHASE_*.md" -o -name "*_COMPLETE.md" -o -name "*_SUMMARY.md" -o -name "*_REPORT.md"
find docs -type d -name "reports" -o -name "plans" -o -name "artifacts"
```

Если найдены — пометь как "требуют миграции в Diátaxis структуру".

---

user:
Проведи аудит документации проекта AI Prompt System по Diátaxis стандартам 2026.
