# Агентный режим — переносимый шаблон

Улучшенный комплект агентного режима для Qwen Code: оркестратор + команда специализированных агентов (spec-writer, backend-dev, frontend-dev, qa, adversary) для структурированной разработки.

## Что входит

```
agents_template_improved/
├── README.md                          <- этот файл (инструкция переноса)
├── QWEN_TEMPLATE.md                   <- шаблон контекста оркестратора
├── AGENTS_TEMPLATE.md                 <- шаблон правил команды
├── .qwen/
│   ├── agents/
│   │   ├── spec-writer.md             <- автор спецификаций (фаза 0)
│   │   ├── backend-dev.md             <- серверный код
│   │   ├── frontend-dev.md            <- UI-слой
│   │   ├── qa.md                      <- проверки, DEFECTS.md
│   │   └── adversary.md               <- враждебные прогоны
│   └── skills/
│       └── task-spec/
│           ├── SKILL.md               <- скилл оркестратора (фаза создания)
│           └── TEMPLATE.md            <- шаблон REQUIREMENTS.md
└── MIGRATION_GUIDE.md                 <- пошаговый перенос в новый проект
```

## Принципы

- **Переносимость:** один шаблон для любого проекта — Python/FastAPI, Node.js/React, Go, что угодно.
- **Адаптация через таблицу:** зоны файлов, команды проверки и запреты для каждого проекта определяются таблицей «Зоны и проверки» в AGENTS.md — агенты читают её и подстраиваются автоматически.
- **Экономия токенов:** короткие фазы (1–3 файла, ~10–15 ходов), прогресс-файлы для восстановления, сырые выводы в файл.
- **Доказательства:** каждое утверждение подтверждается артефактом (e2e/, DEFECTS.md, лог).

## Быстрый старт

1. Скопируй `.qwen/` в корень своего проекта.
2. Создай `QWEN.md` и `AGENTS.md` по шаблонам `*_TEMPLATE.md` — замени блоки `{{...}}` на контекст своего проекта.
3. Заполни таблицу «Зоны и проверки» в AGENTS.md для своих технологий.
4. Создай `tasks/current/REQUIREMENTS.md` с сырой идей задания (2–10 строк).
5. Запусти оркестратора — он использует скилл `task-spec` для создания спеки.

Подробнее — в [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

## Модели по умолчанию

Каждый агент имеет `model:` в frontmatter своего `.md` — меняй в одном месте:

- **spec-writer:** `nordrouter/moonshotai/kimi-k2.7-code` — сильная модель для архитектурного планирования
- **backend-dev / frontend-dev:** `nordrouter/minimax/minimax-m3` — баланс скорость/качество для кода
- **qa / adversary:** `nordrouter/xiaomi/mimo-v2.5` — быстрая модель для проверок

Модели должны быть объявлены в `~/.qwen/settings.json`.

## Ключевые улучшения

### spec-writer
- Архитектурное мышление: разбор зависимостей, bounded contexts, контракты между модулями
- Защита от оверинжиниринга: "Do you really need that abstraction?"
- Шаблоны типовых архитектурных решений (CRUD + auth, event sourcing, микросервисы)

### backend-dev
- Best practices стека: FastAPI (async/DI/middleware), SQLAlchemy 2.0 (relationship strategies), React (hooks/performance)
- Типовые ловушки и решения (N+1 queries, race conditions, memory leaks)
- Безопасность по умолчанию (parameterized queries, XSS escaping, rate limiting)

### frontend-dev
- Accessibility checklist (ARIA, keyboard nav, color contrast)
- Performance patterns (lazy loading, memoization, bundle splitting)
- Типовые UI компоненты (forms, tables, modals)

### qa
- Расширенный чек-лист проверок (безопасность, производительность, граничные случаи)
- Playwright-шаблоны для UI

### Общее
- Прогресс-файлы для каждой фазы — дешёвое восстановление после сбоя
- Сырые выводы в `tasks/current/dev/` и `tasks/current/e2e/` — экономия контекста
- Стоп-правила: две неудачи подряд → доклад оркестратору

## Лицензия

MIT — используй где угодно, как угодно.
