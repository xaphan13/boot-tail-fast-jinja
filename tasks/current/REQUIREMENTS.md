# Текущее задание — Порт блога flask-blog-1 на FastAPI + Jinja

Исходник: `templates_flaskblog/` (Flask 3.1 + Jinja, пример только для чтения — не редактировать).
Цель: полностью повторить блог на текущем проекте FastAPI — те же маршруты, тот же дизайн,
тот же рендер Markdown-статей. Ни одной «улучшательской» правки дизайна.

## Суть

Создать пакет `fastapi-application/md_articles/` с серверным рендерингом Jinja2: список статей из
YAML-реестра, страницы статей (Markdown → HTML), вход/регистрация/аккаунт с сессиями и
bcrypt, управление реестром статей, HTML-страницы ошибок 403/404/500. Шаблоны и статика
кладутся в корень приложения (`templates/`, `static/`), порт 1:1 из
`templates_flaskblog/templates/` и `templates_flaskblog/static/`.

Подтверждённые решения пользователя:

- Контент-статьи (`.md` в `content_art/`) команда **не создаёт** — их кладёт пользователь.
  Реестр `articles.yaml` переносится из шаблона как есть.
- Формы — чистый HTML + серверная Pydantic-валидация (без WTForms); для всех POST-форм —
  минимальный CSRF-токен в сессии.
- Таблицы блога `blog_user`/`blog_post` — отдельные модели + Alembic-миграция. Маршрут
  `/createDB` **не переносится**.
- Загрузка аватара с Pillow-миниатюрой 125×125 — включается.
- «Remember me» — чекбокс остаётся в разметке, поведение: фиксированный срок сессии
  14 дней.

## Результат

Пакет `md_articles/` плюс `templates/` и `static/` в корне приложения:

```
fastapi-application/
├── md_articles/
│   ├── __init__.py        # сборка роутеров + register-функции (middleware, static, errors)
│   ├── routes_main.py     # /, /home, /about
│   ├── routes_users.py    # /register, /login, /logout, /account
│   ├── routes_articles.py # /art_home, /art/{author}/{art_id}, /art_manage, /art_manage/add_all, /art_manage/meta
│   ├── schema_art.py      # ArticleLang + YAML-реестр (порт из new_articles/schema_art.py)
│   ├── models.py          # BlogUser / BlogPost (SQLAlchemy 2.0, стиль проекта)
│   ├── web_utils.py       # сессия, current_user, flash, CSRF, require_login, шаблоны Jinja2Templates
│   └── articles.yaml      # реестр статей (порт из шаблона)
├── templates/             # порт из templates_flaskblog/templates/ (16 файлов)
│   ├── content_art/       # ПУСТАЯ папка (+ .gitkeep) — статьи кладёт пользователь
│   └── includes/ errors/ new_art/ layout.html about.html login.html register.html account.html
└── static/
    ├── art_css/           # base.css, scripts.js — копия 1:1
    └── profile_pics/      # placeholder default.jpg 125×125 (сгенерировать) + загруженные аватары
```

## Вне рамок

- Не трогать: `api/`, `example_sql/`, `ex_order_product/`, `db_core/` (кроме реэкспорта
  моделей в `db_core/__init__.py`), существующие роуты и их поведение.
- Не переносить: `/createDB` (таблицы создаёт миграция), WTForms/Flask-зависимости,
  `waitress`, `ConfigLogger` (используется существующий `logF`).
- Не создавать контент-статьи и не править `templates_flaskblog/`.
- Дизайн не меняем: Bootstrap 5.3.8 + highlight.js с jsdelivr CDN + SRI остаются как есть.

## Что сделать

### 1. Инфраструктура (backend-dev)

1. Зависимости в `pyproject.toml`: `jinja2`, `python-multipart`, `markdown`, `pyyaml`,
   `bcrypt`, `pillow`, `itsdangerous` → `uv sync`.
2. `core/config.py`: поле `secret_key` (строка с dev-дефолтом, перекрытие через
   `APP__...`), встроить в существующую вложенную модель по месту.
3. `create_fastapi.py` — минимальные изменения: подключить `md_articles/` (роутеры, mount
   `/static` → `fastapi-application/static/`, `SessionMiddleware` с `secret_key`,
   обработчики ошибок). Вся логика подключения — функциями в `md_articles/__init__.py`,
   фабрика только вызывает их.

### 2. Модели и миграция (backend-dev)

1. `md_articles/models.py`: `BlogUser` (id, username unique String(20) not null, email
   unique String(120) not null, image_file String(20) default `'default.jpg'`, password
   String(60) not null, relationship posts) и `BlogPost` (id, title String(100) not
   null, date_posted DateTime not null, content Text not null, user_id FK → blog_user.id).
   Таблицы `blog_user`, `blog_post`; типы колонок из `db_core/type_for_models.py`.
2. Реэкспорт обеих моделей в `db_core/__init__.py` (обязателен для Alembic).
3. Alembic-ревизия `--autogenerate` (третья по счёту), применяется
   `alembic upgrade heads` на активном SQLite-профиле (`two.env`).

### 3. Web-утилиты (backend-dev, `md_articles/web_utils.py`)

1. `Jinja2Templates` (каталог `fastapi-application/templates/`), в контексте шаблонов: `request`,
   `current_user`, `csrf_token`; Jinja-global `get_flashed_messages` (через
   `pass_context`, категории flash как во Flask).
2. Сессии: `session["user_id"]`; `current_user` — dependency (select по id, None если
   нет); срок жизни 14 дней.
3. `flash(category, message)` → список `("_flashes")` в сессии; чтение с очисткой.
4. CSRF: токен в сессии (secrets), скрытое поле `csrf_token` во всех POST-формах;
   несовпадение → HTTP 403.
5. `require_login(request)` — редирект на `/login?next=<path>` + flash (аналог
   Flask-Login), для `/art_manage*` и `/account`.
6. Аутентификация: `bcrypt` хеш/проверка пароля; `next`-редирект после входа (только
   относительные пути).

### 4. Маршруты (backend-dev)

Порт логики из `templates_flaskblog/users/routes_users.py`, `main/routes_main.py`,
`new_articles/routes_articles.py` на async SQLAlchemy + `CurrentSession` из `db_core`.
Валидация форм — Pydantic-схемы; ошибки валидации рендерятся в тех же классах Bootstrap
(`is-invalid`, `invalid-feedback`), тексты ошибок как в WTForms-шаблоне.

### 5. Шаблоны и статика (frontend-dev)

1. Перенести все 16 HTML-файлов в `fastapi-application/templates/` (layout, about, login,
   register, account, errors/403, 404, 500, includes/×8, new_art/×3) с адаптациями
   (см. ниже), стиль и классы — без изменений.
2. Адаптации шаблонов:
   - `url_for('static', filename=X)` → `url_for('static', path=X)`;
   - WTForms-поля → чистый HTML: `name`/`id`/`class="form-label"`/`class="form-control"`,
     ошибки — `is-invalid` + `invalid-feedback` (макрос `_form_macro.html` переписать
     под простые поля, внешний вид сохранить);
   - `form.hidden_tag()` → `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">`;
   - `url_for('users.login')` и прочие — работают через контракт имён (таблица ниже);
   - `get_flashed_messages(with_categories=true)` — как во Flask.
3. Статика в `fastapi-application/static/`: `art_css/base.css`, `art_css/scripts.js` —
   копия 1:1; сгенерировать placeholder `profile_pics/default.jpg` 125×125.
4. `content_art/` — пустая папка с `.gitkeep`.

### 6. Обработчики ошибок (backend-dev)

403 / 404 / 500 → соответствующие шаблоны `errors/*.html` (HTML-ответ, не JSON).
Проверить: `/art/<author>/<несуществующий_id>` → 404 HTML.

### 7. Документация (оркестратор)

Новый `docs/11_md_articles.md` (архитектура `md_articles/`, маршруты, отличия от
Flask-версии); обновить таблицы маршрутов и счётчик маршрутов в `README.md`, `QWEN.md`,
`AGENTS.md` (включая таблицу «Зоны и проверки»: зона frontend-dev расширяется до
`fastapi-application/templates/` + `fastapi-application/static/`).

## Контракт имён роутов (обязателен для backend-dev и frontend-dev)

`name=` в `APIRouter`/декораторах = Flask-имя эндпоинта — шаблоны продолжают работать
с `url_for` без массовой правки:

| Маршрут | Методы | name | Логин |
|---|---|---|---|
| `/`, `/home` | GET | `main.home` | — |
| `/about` | GET | `main.about` | — |
| `/art_home` | GET | `art_main.art_home` | — |
| `/art/{author}/{art_id}` | GET | `art_main.art_author` | — |
| `/art_manage` | GET | `art_main.art_manage` | да |
| `/art_manage/add_all` | POST | `art_main.art_manage_add_all` | да |
| `/art_manage/meta` | POST | `art_main.art_manage_meta` | да |
| `/register` | GET, POST | `users.register` | — |
| `/login` | GET, POST | `users.login` | — |
| `/logout` | GET | `users.logout` | — |
| `/account` | GET, POST | `users.account` | да |

`articles.yaml` и `content_art` резолвятся от `BASE_DIR` (не от cwd): контент —
`fastapi-application/templates/content_art`, реестр — `md_articles/articles.yaml`.

## Критерии успеха

Запуск: `cd fastapi-application && ../.venv/bin/uvicorn main:main_app --port 8000`.
Все curl — с сохранением cookie: `-s -c /tmp/jar -b /tmp/jar`. Сырые выводы — в
`tasks/current/e2e/`.

| # | Критерий | Проверка | Ожидание |
|---|---|---|---|
| 1 | Приложение собирается, счётчик маршрутов | `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"` | 38 (25 старых + 12 блога + 1 mount `/static`); фактическое число фиксируется, расхождение объяснить |
| 2 | Миграция создаёт таблицы | `../.venv/bin/alembic upgrade heads`, затем регистрация из критерия 6 | без ошибок; вход работает |
| 3 | Редирект главной | `curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://127.0.0.1:8000/` | `307` → `/art_home` |
| 4 | Список статей | `curl -s http://127.0.0.1:8000/art_home` | 200, HTML содержит «Статьи» и заголовки записей из `articles.yaml` |
| 5 | Статья: Markdown-рендер | `curl -s http://127.0.0.1:8000/art/Max/1787932544` при существующем файле записи; если пользователь ещё не положил `.md` — qa временно кладёт тестовый `.md` в `content_art`, добавляет запись через `/art_manage/meta`, проверяет и убирает тестовые файл/запись | 200; тело статьи — HTML из Markdown (`<h2>` вместо `<h1>`, `<pre><code>` для fenced-блоков, `<table>` для таблиц); дубликаты nickname и пр. — не влияет |
| 6 | Регистрация | `CSRF=$(curl -s -c jar http://127.0.0.1:8000/register \| grep -oP 'name="csrf_token" value="\K[^"]+')`; POST `/register` (`username=e2e_user`, уникальные email/password) с csrf | 307 → `/login`; повторная регистрация того же username — 200 с ошибкой валидации в HTML |
| 7 | Вход/выход | POST `/login` (email+password из п.6, csrf), затем GET `/account`, затем GET `/logout` | вход: 307 → `/art_home`; `/account`: 200 и `e2e_user` в HTML; `/logout`: 307 |
| 8 | Защита роутов | без сессии: `curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://127.0.0.1:8000/art_manage` | 307 → `/login?next=/art_manage` |
| 9 | Управление реестром | с сессией: GET `/art_manage`; POST `/art_manage/meta` (csrf + валидные поля) для существующей записи | 200 «Управление статьями»; POST → 307 и flash «Обновлена запись …» на следующем GET |
| 10 | CSRF | POST `/login` с неверным csrf | 403 |
| 11 | Статика | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/static/art_css/base.css` | 200 |
| 12 | 404 HTML | `curl -s http://127.0.0.1:8000/art/x/999999` | 404, HTML по шаблону errors/404.html (не JSON) |
| 13 | Регресс старых эндпоинтов | `curl -s -o /dev/null -w "%{http_code}"` для `/docs`, `/users/get_all_users`, `/orders/get_all_orders`, `/api/v1/dep_examples/single-direct-dependency` | все 200 |
| 14 | Линтер | `uv run ruff check .` | без ошибок |

## Финальные критерии

1. Каждый критерий успеха подтверждён доказательством: сырой curl-вывод или лог в
   `tasks/current/e2e/`, ссылка на DEFECTS.md/ADVERSARIAL_REVIEW.md.
2. `tasks/current/DEFECTS.md` существует только если найдены дефекты; все записи не OPEN.
3. Adversarial-прогон выполнен (акцент: `/account` и `/art_manage*` без сессии, POST без
   CSRF, path traversal в `file_name`, порча `articles.yaml` → last-good-state), ни одна
   запись ADVERSARIAL_REVIEW.md не PENDING.
4. Дизайн портирован 1:1 (сравнение с `templates_flaskblog/templates/` при ревью).
5. Документация обновлена (`docs/11_md_articles.md`, README, QWEN.md, AGENTS.md).
