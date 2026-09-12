# Ключевые улучшения агентного режима

Краткая сводка изменений относительно оригинала из `boot-tail-fast-jinja/.qwen/`.

## Архитектурное мышление (spec-writer)

**Добавлено:**
- **Bounded Context Analysis**: определение границ модуля, зависимостей, интеграционных контрактов
- **Complexity Assessment**: честная оценка объёма файлов (CRUD ~8–10, порт 300+ строк ~15–20 ходов)
- **Architectural Patterns**: типовые решения для CRUD+Auth, Event-driven, Microservices, Frontend
- **Anti-Patterns защита**: "Do you really need that abstraction?" — явное обоснование каждой новой зависимости/абстракции
- **Security & Performance by Default**: чек-листы встроены в процесс, не постфактум
- **Архитектурные шаблоны**: готовые разбивки на фазы для FastAPI CRUD, React Component, Database Migration

**Цель:** spec-writer не просто нарезает файлы, а продумывает решение архитектурно и режет на фазы исходя из реальной сложности.

## Best Practices по стекам (backend-dev, frontend-dev)

**Добавлено:**

### Backend-dev:
- **Python/FastAPI**: async всегда, DI через Depends, parameterized queries, security patterns
- **SQLAlchemy 2.0**: typed columns, relationships strategies, N+1 решения, migrations checklist
- **Node.js/Express**: async/await, middleware порядок, connection pooling, prepared statements
- **Типовые ловушки с решениями**: N+1 query (selectinload), race conditions (atomic updates), memory leaks

### Frontend-dev:
- **React/TypeScript**: component structure, hooks rules, state management выбор, performance patterns
- **HTML & CSS**: semantic HTML, BEM/CSS Modules, mobile-first, CSS variables
- **Accessibility чек-лист**: keyboard nav, ARIA attributes, images alt, color contrast, forms labels
- **Performance**: lazy loading, memoization guidelines, bundle optimization
- **Playwright шаблон**: программная проверка через `p.locator()`, не только PNG

**Цель:** разработчики пишут правильный код сразу, а не "код + исправление qa + новый код".

## Расширенные проверки (qa)

**Добавлено:**
- **Функциональные проверки**: happy path, граничные значения, невалидный ввод, permissions, idempotency
- **Безопасность (smoke-level)**: SQL injection, XSS, path traversal, CORS, sensitive data leaks
- **Производительность (smoke-level)**: response time < 500ms, N+1 queries в логах, memory leaks
- **Регресс чек-лист**: соседние endpoints, документация API

**Пример пачки curl**:
```bash
cat > tasks/current/e2e/smoke_test.sh << 'EOF'
echo "=== Health check ==="
curl -sw "\nStatus: %{http_code}\n" $BASE/health
echo -e "\n=== Create user ==="
curl -sw "\nStatus: %{http_code}\n" -X POST $BASE/users -d '{"name":"Alice"}'
...
EOF
bash tasks/current/e2e/smoke_test.sh > tasks/current/e2e/smoke_results.txt 2>&1
```

**Цель:** qa находит проблемы до adversary, экономит проходы "qa → дефект → фикс → ретест".

## Adversarial методология (adversary)

**Добавлено:**
- **Input Fuzzing**: экстремумы, Unicode/encoding, injection attempts (SQL/XSS/command/path traversal)
- **State & Sequencing Attacks**: race conditions, invalid state transitions, stale references
- **Authentication & Authorization**: bypass attempts, session attacks, privilege escalation
- **Protocol & API Abuse**: HTTP method confusion, content-type confusion, large payloads, billion laughs
- **Rate Limiting & DoS**: burst requests, slowloris
- **UI-Specific**: browser exploits, navigation attacks

**Примеры готовых команд**:
```bash
# SQL Injection
curl -X POST /users -d '{"name":"admin'\'' OR '\''1'\''='\''1"}'

# Race condition
for i in {1..10}; do curl -X POST /orders -d '{"product_id":1}' & done; wait

# Large payload
python3 -c "print('{\"data\":\"' + 'A'*10000000 + '\"}')" | curl -X POST /api/data -d @-
```

**Цель:** adversary знает, что искать, а не просто "попробую разное".

## Переносимость

**Структура:**
```
agents_template_improved/
├── README.md                    <- обзор + быстрый старт
├── QWEN_TEMPLATE.md             <- контекст оркестратора, {{плейсхолдеры}}
├── AGENTS_TEMPLATE.md           <- правила команды, {{плейсхолдеры}}
├── MIGRATION_GUIDE.md           <- пошаговая инструкция переноса
├── .qwen/agents/                <- универсальные определения ролей
└── .qwen/skills/task-spec/      <- скилл фазы создания
```

**Адаптация = замена {{плейсхолдеров}} + заполнение таблицы «Зоны и проверки».**

Таблица — единственная привязка к конкретному проекту: агенты читают из неё зону файлов,
команды проверки и запреты. Сами `.qwen/agents/*.md` универсальны (Python/Node/React/Go).

## Экономия токенов — явные правила

**Добавлено в каждого агента:**
- Минимум чтений: AGENTS.md и REQUIREMENTS.md один раз, не перечитывать
- Пачки команд: один shell-вызов, несколько curl/проверок
- Сырые выводы сразу в файл (`tasks/current/e2e/`, `tasks/current/dev/`), в чат — вердикты
- Стоп-правило: две неудачи подряд → доклад оркестратору
- Прогресс-файлы для восстановления: `tasks/current/dev/phaseNN_progress.md`

**Оркестратор:**
- Главный расход — backend-dev/frontend-dev, экономия делается ДО запуска (спека с фазами)
- Три уровня защиты: (1) spec-writer режет фазы заранее, (2) короткие фазы 1–3 файла,
  (3) дисциплина внутри фазы (план файлов → write_file → edit → прогресс → smoke)
- Восстановление упавшего прогона: свежий узкий запуск по прогресс-файлу + `git diff`,
  никогда не пересказ истории

**Урок 001-md-articles-blog**: монолитный прогон backend-dev на весь бэкенд стоил ~25 млн
токенов, qa/adversary уложились дёшево. Решение: режь фазы жёстче на этапе спеки.

## Контрольный список перед использованием

- [ ] `.qwen/agents/` скопирована в новый проект
- [ ] `QWEN_TEMPLATE.md` → `QWEN.md`, все `{{...}}` заполнены контекстом проекта
- [ ] `AGENTS_TEMPLATE.md` → `AGENTS.md`, все `{{...}}` заполнены
- [ ] Таблица «Зоны и проверки» в AGENTS.md заполнена для твоего стека
- [ ] `tasks/current/REQUIREMENTS.md` создан (заглушка или первое задание)
- [ ] Модели агентов объявлены в `~/.qwen/settings.json`
- [ ] (Опционально) `model:` в `.qwen/agents/*.md` заменены на доступные модели
- [ ] Первый прогон: сырая идея → скилл `task-spec` → ревью → подтверждение → исполнение

## Что НЕ менять при переносе

- `.qwen/agents/*.md` — универсальны для любого стека (только `model:` если надо)
- `.qwen/skills/task-spec/` — тоже универсален
- Формат DEFECTS.md, ADVERSARIAL_REVIEW.md — ровно как в AGENTS.md
- Жизненный цикл задания (current/ → NNN-<slug>/)
- Роли команды (spec-writer, backend-dev, frontend-dev, qa, adversary) — если только
  не удаляешь роль (например frontend-dev в API-only проекте)

## Итог улучшений одним предложением

spec-writer стал архитектором с честной оценкой, разработчики получили встроенные
best-practices и чек-листы безопасности/производительности, qa расширен до smoke-security,
adversary получил методологию атак, всё переносимо через плейсхолдеры и таблицу «Зоны».
