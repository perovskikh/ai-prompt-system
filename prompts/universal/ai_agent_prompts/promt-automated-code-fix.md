system: Ты эксперт AI агент для автоматического исправления кода в p9i. Твоя задача - анализировать bottleneck-ы и автоматически генерировать исправления для критических проблем.

---

user: Исправь следующие bottleneck-ы и ошибки в коде:

**Analysis Results**: {{ analysis_results }}
**Code Changes**: {{ code_changes }}
**Reference Document**: docs/BOTTLENECKS_ANALYSIS.md

## Требования к исправлениям

1. **Используй docs/BOTTLENECKS_ANALYSIS.md как reference** для всех known bottleneck-ов
2. **Не изменяй структуру файлов**, только содержимое внутри функций
3. **Сохраняй существующие паттерны кода** и стиль форматирования
4. **Добавляй inline комментарии** для сложных изменений
5. **Приоритизируй критические проблемы безопасности и производительности**

## Auto-Fix Priorities

🔴 **Critical** (исправить немедленно, возможно auto-apply):
- Input sanitization vulnerabilities (path traversal, injection)
- Missing caching для горячих путей (latency >50ms)
- Security vulnerabilities (weak rate limiting, PII exposure)
- Direct file I/O в hot path без кэша
- Hardcoded secrets или API keys

🟡 **High** (исправить в этом PR, requires review):
- Architecture: Mixed concerns (server.py >500 строк)
- Integration: Fragile markdown parsing
- Performance: Sequential execution цепочек
- Security: Incomplete error handling

🟢 **Medium** (технический долг, future work):
- Code style improvements
- Deprecation warnings
- Legacy code removal
- Test coverage improvements

## Output Format

Обязательный JSON формат с полными исправлениями:

```json
{
  "summary": {
    "total_bottlenecks": 15,
    "critical": 3,
    "high": 8,
    "medium": 4,
    "auto_applied": 2,
    "requires_review": 13
  },
  "fixes": [
    {
      "file": "src/api/server.py",
      "line": 240,
      "function": "load_prompt",
      "issue": "No input sanitization - path traversal vulnerability (OWASP LLM Top 10 #2)",
      "severity": "critical",
      "bottleneck_category": "security",
      "can_auto_apply": true,
      "before_code": "def load_prompt(prompt_name: str) -> dict:\n    prompt_file = PROMPTS_DIR / f\"{prompt_name}.md\"\n    if prompt_file.exists():\n        content = prompt_file.read_text()\n        return {\"name\": prompt_name, \"file\": prompt_file.name, \"content\": content}",
      "after_code": "import re\nfrom pathlib import PurePosixPath\n\ndef sanitize_prompt_name(prompt_name: str) -> str:\n    \"\"\"Sanitize prompt name to prevent path traversal attacks.\"\"\"\n    sanitized = prompt_name.replace(\"..\", \"\").replace(\"/\", \"\").replace(\"\\\\\", \"\")\n    if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized):\n        raise ValueError(f\"Invalid prompt name: {prompt_name}\")\n    if PurePosixPath(sanitized).is_absolute():\n        raise ValueError(\"Absolute paths not allowed\")\n    return sanitized\n\ndef load_prompt(prompt_name: str) -> dict:\n    prompt_name_sanitized = sanitize_prompt_name(prompt_name)\n    prompt_file = PROMPTS_DIR / f\"{prompt_name_sanitized}.md\"\n    if prompt_file.exists():\n        content = prompt_file.read_text()\n        return {\"name\": prompt_name, \"file\": prompt_file.name, \"content\": content}\n    raise FileNotFoundError(f\"Prompt not found: {prompt_name_sanitized}\")",
      "diff": "+import re\n+from pathlib import PurePosixPath\n+\n+def sanitize_prompt_name(prompt_name: str) -> str:\n+    \"\"\"Sanitize prompt name to prevent path traversal attacks.\"\"\"\n+    sanitized = prompt_name.replace(\"..\", \"\").replace(\"/\", \"\").replace(\"\\\\\", \"\")\n+    if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized):\n+        raise ValueError(f\"Invalid prompt name: {prompt_name}\")\n+    if PurePosixPath(sanitized).is_absolute():\n+        raise ValueError(\"Absolute paths not allowed\")\n+    return sanitized",
      "reasoning": "Путь traversal атака позволяет злоумышленнику читать системные файлы. OWASP LLM Top 10 #2. Добавлена валидация с regex и проверка на абсолютные пути."
    },
    {
      "file": "src/storage/prompts.py",
      "line": 45,
      "function": "load_prompt",
      "issue": "Missing caching - File I/O on every request (50-100ms latency)",
      "severity": "critical",
      "bottleneck_category": "performance",
      "can_auto_apply": true,
      "before_code": "def load_prompt(self, name: str) -> dict:\n    prompt_file = self.prompts_dir / f\"{name}.md\"\n    content = prompt_file.read_text()\n    return {\"name\": name, \"content\": content}",
      "after_code": "from functools import lru_cache\n\n@lru_cache(maxsize=256)\ndef load_prompt(self, name: str) -> dict:\n    prompt_file = self.prompts_dir / f\"{name}.md\"\n    content = prompt_file.read_text()\n    return {\"name\": name, \"content\": content}",
      "diff": "+from functools import lru_cache\n+@lru_cache(maxsize=256)",
      "reasoning": "Без кэша каждый запрос вызывает File I/O. С @lru_cache(maxsize=256) первый запрос 50ms, последующие ~0ms. Потенциальный выигрыш: 50-100x."
    },
    {
      "file": "src/api/server.py",
      "line": 65,
      "function": "APIKeyManager._check_rate_limit",
      "issue": "Weak rate limiting - In-memory tracking, no distributed protection (DoS vulnerability)",
      "severity": "high",
      "bottleneck_category": "security",
      "can_auto_apply": false,
      "before_code": "def _check_rate_limit(self, api_key: str, limit: int) -> bool:\n    now = time.time()\n    key_data = self._rate_limits.get(api_key)\n    if key_data is None:\n        self._rate_limits[api_key] = [1, now]\n        return True",
      "after_code": "# Requires Redis for distributed rate limiting\n# Migration needed: see docs/BOTTLENECKS_ANALYSIS.md section 4.2\ndef _check_rate_limit(self, api_key: str, limit: int) -> bool:\n    now = time.time()\n    key_data = self._rate_limits.get(api_key)\n    # TODO: Migrate to Redis-based distributed rate limiting\n    # See: docs/BOTTLENECKS_ANALYSIS.md section 4.2\n    if key_data is None:\n        self._rate_limits[api_key] = [1, now]\n        return True",
      "diff": "+# TODO: Migrate to Redis-based distributed rate limiting\n+# See: docs/BOTTLENECKS_ANALYSIS.md section 4.2",
      "reasoning": "In-memory rate limiting уязвим к distributed DoS атакам. Требует миграции на Redis. Высокий приоритет, но требует инфраструктурных изменений."
    }
  ],
  "recommendations": [
    "Обновить prompts/registry.json с добавлением promt-automated-code-fix.md",
    "Интегрировать ai-code-review job в .github/workflows/adr-check.yml",
    "Настроить auto-apply для critical severity fixes",
    "Создать monitoring dashboard для bottleneck tracking"
  ],
  "next_steps": [
    "Применить critical fixes автоматически",
    "Создать PR для high priority fixes",
    "Добавить в backlog medium priority items",
    "Обновить docs/BOTTLENECKS_ANALYSIS.md после применения fixes"
  ]
}
```

## Важные правила

1. **Только critical severity** может быть применено автоматически (`can_auto_apply: true`)
2. **High и medium severity** всегда требует review (`can_auto_apply: false`)
3. **Обязательно предоставлять before_code и after_code** для каждого fix
4. **Добавлять reasoning** объясняющее почему это исправление необходимо
5. **Указывать bottleneck_category** для группировки
6. **Включать references** на docs/BOTTLENECKS_ANALYSIS.md для контекста

## Auto-Apply Decision Logic

```python
if fix["severity"] == "critical" and fix["can_auto_apply"]:
    # Автоматически применить
    apply_fix(fix)
elif fix["severity"] == "high" and fix["can_auto_apply"]:
    # Предложить в PR comment, но не применять
    suggest_fix(fix)
else:
    # Добавить в backlog
    backlog_add(fix)
```

## Конечный результат

После анализа верни JSON который содержит:
- Полные исправления с before/after кодом
- Критичность и возможность auto-apply
- Дифф для каждого изменения
- Приоритезованный список next steps
- Связи с docs/BOTTLENECKS_ANALYSIS.md

Этот JSON будет использоваться GitHub Actions для автоматического применения critical fixes и создания PR для остальных.