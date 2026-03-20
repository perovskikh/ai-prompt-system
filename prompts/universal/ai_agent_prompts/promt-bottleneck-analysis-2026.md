# AI Agent Prompt: Bottleneck Analysis 2026

**Version:** 1.0
**Date:** 2026-03-20
**Purpose:** Исследование узких мест системы с генерацией документации по стандартам 2026

---

## 2026 Documentation Standards (ОБЯЗАТЕЛЬНО)

При исследовании bottleneck-ов ты ДОЛЖЕН создавать документацию в формате:

### 1. Diátaxis Framework (ОБЯЗАТЕЛЬНО)
| Тип | Директория | Когда использовать |
|-----|------------|-------------------|
| **Tutorials** | `docs/tutorials/` | Обучение "как работает" |
| **How-to** | `docs/how-to/` | Конкретные шаги "как сделать" |
| **Reference** | `docs/reference/` | API/команды (AUTO-GENERATED) |
| **Explanation** | `docs/explanation/` | Концепции + ADR |

### 2. Living Documentation Pattern
- Все reference docs генерируются автоматически
- Используй `make docs-build` для обновления
- НЕ создавай reference docs вручную

### 3. Output Structure

Для каждого найденного bottleneck создай:

```markdown
## Bottleneck: [Название]

### Категория
- Security / Performance / Architecture / Code Quality

### Диátaxis Решение
- Если требует объяснения → docs/explanation/adr/ADR-NNN-{slug}.md
- Если требует how-to → docs/how-to/bottleneck-fix-{name}.md
- Если это концепция → docs/explanation/bottleneck-{name}.md

### severity
🔴 Critical / 🟡 High / 🟢 Medium

### Рекомендуемое действие
[AUTO-APPLY / PR / Backlog]

### Anti-Patterns Detection
Проверь что НЕ создаёшь:
- PHASE_*.md, *_COMPLETE.md, *_SUMMARY.md, *_REPORT.md
- docs/reports/, docs/plans/, docs/artifacts/
```

---

## Исследование

ТЫ ДОЛЖЕН:

1. **Найди все bottleneck-ы** в коде системы:
   - `src/api/server.py` — анализ размера (>500 строк = mixed concerns)
   - `src/services/` — проверь latency горячих путей
   - `src/storage/` — проверь кэширование

2. **Классифицируй по категориям**:
   - Security (уязвимости, rate limiting)
   - Performance (latency, кэш, I/O)
   - Architecture (связанность, разделение)
   - Code Quality (технический долг)

3. **Примени Diátaxis к каждому**:
   - Нужен how-to? → `docs/how-to/fix-{bottleneck}.md`
   - Нужен ADR? → `docs/explanation/adr/ADR-NNN-{slug}.md`
   - Нужен explanation? → `docs/explanation/{topic}.md`

4. **Создай план исправлений**:
   - Critical → Auto-fix возможно
   - High → Требует PR review
   - Medium → Backlog

---

## Команды для анализа

```bash
# Структура проекта
find src -name "*.py" | head -20

# Размер файлов (potential architecture issues)
wc -l src/api/server.py src/services/*.py src/storage/*.py

# Поиск паттернов bottleneck
grep -r "TODO\|FIXME\|XXX" src/ --include="*.py"
grep -r "time.sleep\|requests\." src/ --include="*.py"

# Проверка кэширования
grep -r "cache\|lru_cache\|redis" src/ --include="*.py"
```

---

## Output Format

Верни результат в формате:

```markdown
# Bottleneck Analysis Report

## Summary
- Total bottlenecks found: N
- Critical: N
- High: N
- Medium: N

## Findings

### 🔴 Critical: [Name]
- **File**: `src/...`
- **Category**: Security/Performance/Architecture/CodeQuality
- **Diátaxis Solution**: docs/how-to/fix-xxx.md
- **Auto-apply**: Yes/No

### 🟡 High: [Name]
...

## Action Plan

| Priority | Bottleneck | Solution | Output |
|----------|------------|----------|--------|
| P0 | Security vuln | Fix code | - |
| P1 | Missing cache | docs/how-to/ + code | docs/how-to/xxx.md |
| P2 | Architecture | ADR | docs/explanation/adr/ADR-NNN.md |

## Anti-Patterns Created?
- [ ] PHASE_*.md?
- [ ] *_SUMMARY.md?
- [ ] docs/reports/?

Если есть — удали и пересоздай в правильной Diátaxis структуре.
```

---

user:
Проведи исследование всех узких мест в системе и создай документацию по стандартам 2026.