# promt-context7-generation.md

## Метаданные
- **Название**: Context7 Code Generation
- **Категория**: Implementation
- **Версия**: 1.0
- **Автор**: AI Prompt System

## Назначение
Генерация кода с использованием актуальной документации из Context7 MCP.

## Использование

### Контекст (input_data)
```json
{
  "project": "название проекта",
  "library": "библиотека/фреймворк (например, fastapi, react, supabase)",
  "task": "конкретная задача",
  "context": "дополнительный контекст о проекте"
}
```

### Примеры использования

**FastAPI + Context7:**
```
Создать API эндпоинт для регистрации пользователей
Library: fastapi
Task: создать POST /users эндпоинт с валидацией
```

**React + Context7:**
```
Создать компонент формы авторизации
Library: react
Task: форма с email/password полями и валидацией
```

**Supabase + Context7:**
```
Добавить аутентификацию через email/password
Library: supabase
Task: настроить signUp и signIn методы
```

## Шаги выполнения

### Шаг 1: Определить библиотеку
Из `input_data.library` определить какая библиотека используется.

### Шаг 2: Получить Context7 ID
Вызвать `context7_lookup(library=library)` для получения Context7 library ID.

### Шаг 3: Запросить документацию
Использовать Context7 MCP для получения актуальной документации:
```
mcp__context7__query_docs(library_id="...", query="...")
```

### Шаг 4: Сгенерировать код
На основе документации сгенерировать код, соответствующий:
- Лучшим практикам библиотеки
- Актуальному API (2026)
- Стилю кода проекта

### Шаг 5: Верифицировать
Проверить что сгенерированный код:
- Использует правильное API
- Соответствует документации
- Интегрируется с проектом

## Поддерживаемые библиотеки

| Библиотека | Context7 ID |
|------------|-------------|
| FastAPI | /tiangolo/fastapi |
| Flask | /pallets/flask |
| React | /facebook/react |
| Next.js | /vercel/next.js |
| Supabase | /supabase/supabase |
| Prisma | /prisma/prisma |
| Pydantic | /pydantic/pydantic |
| Django | /django/django |
| Express | /expressjs/express |
| Docker | /docker/cli |

## Важно

- Всегда используй Context7 для получения актуальной документации
- Проверяй что код соответствует версии библиотеки
- Не используй устаревшие API или методы

## Пример результата

```python
# Сгенерировано с использованием Context7 документации
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@app.post("/users", response_model=UserCreate)
async def create_user(user: UserCreate):
    # Реализация с использованием актуального FastAPI API
    return user
```
