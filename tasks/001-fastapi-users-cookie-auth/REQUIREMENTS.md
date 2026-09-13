# Перенос авторизации на fastapi-users с JWT в cookie

Текущая авторизация блога на session-cookie и ручной проверке `bcrypt` заменяется на адаптированный вариант из `template-jwt-auth`. Пользовательская таблица и существующие данные сохраняются; `fastapi-users` отвечает за хеширование, регистрацию, проверку пользователя и JWT, а JWT хранится в HttpOnly-cookie и используется SSR/Jinja2/HTMX-интерфейсом.

## Архитектурные решения

- **Границы задания:** входит только авторизация блога `md_articles`: модель пользователя, DI fastapi-users, регистрация/вход/выход, текущий пользователь, защищённый аккаунт, минимальная адаптация auth-шаблонов, миграция существующей таблицы и smoke-проверки. Старые демонстрационные API и домены `example_sql`/`ex_order_product` не изменяются.
- **Выбранный подход:** `fastapi-users[sqlalchemy]` версии `>=15,<16`, SQLAlchemy-адаптер на существующей модели `BlogUser` с целочисленным ID, `AuthenticationBackend` + `CookieTransport` + `JWTStrategy`. Такой вариант переносит проверенную реализацию из `template-jwt-auth`, но сохраняет текущую SQLite/PostgreSQL-конфигурацию, таблицу пользователей и SSR-cookie UX.
- **Состояние:** база данных остаётся источником пользователя и его флагов (`is_active`, `is_superuser`, `is_verified`); JWT не содержит роли и не заменяет БД. На защищённом запросе `fastapi-users` извлекает `sub` из JWT и загружает пользователя по ID.
- **Cookie-контракт:** имя, TTL, `Secure` и `SameSite` задаются в `Settings`, а не дублируются в роутерах. Значения по умолчанию пригодны для локального HTTP-dev (`Secure=False`), production обязан передать постоянный `APP__AUTH__SECRET_KEY` и `APP__AUTH__COOKIE_SECURE=true`. Cookie: `HttpOnly`, `Path=/`, `SameSite=Lax`, TTL cookie равен TTL JWT.
- **Сессия блога:** `SessionMiddleware` сохраняется только для CSRF и flash-сообщений. `request.session["user_id"]` больше не является источником авторизации и не используется для загрузки пользователя.
- **Источник текущего пользователя для SSR:** dependency-обёртка над `fastapi_users.current_user(optional=True)` записывает результат в `request.state.current_user`; `require_login` использует ту же dependency и выполняет существующий redirect на `/login?next=...`. Ручной JWT decode и второй криптографический контур не создаются.
- **Совместимость паролей:** существующее поле `password` переименовывается миграцией в `hashed_password` без изменения значений. Размер поля увеличивается до совместимого с Argon2; `fastapi-users` принимает существующие bcrypt-хеши и при успешном входе может автоматически обновить их до актуального хешера. Сырые пароли не мигрируются, не логируются и не возвращаются.
- **Маршруты:** сохраняются HTML-URL `/register`, `/login`, `/logout`, `/account` и их текущие имена `users.register`, `users.login`, `users.logout`, `users.account`. Добавляются машинные `/auth/cookie/login` и `/auth/cookie/logout` из `get_auth_router`; пользовательский API при необходимости публикуется под `/auth/users`, чтобы не конфликтовать с существующим `/users` домена `example_sql`.
- **Регистрация:** существующая form-data форма `/register` остаётся HTML-совместимой; backend преобразует `username`, `email`, `password` в расширенную `UserCreate` и вызывает `user_manager.create(..., safe=True)`. Поля привилегий из клиентского запроса игнорируются.
- **Вход:** auth-шаблон отправляет form-data на стандартный `/auth/cookie/login` (`username=<email>`, `password=...`), получает `204 + Set-Cookie` и делает обычный переход на `/art_home`. JSON/localStorage для JWT не используется.
- **Выход:** UI сохраняет существующий пользовательский `/logout` с redirect, но очищает cookie из единого cookie-контракта. JWT-сессия не отзывается на сервере до истечения TTL — это фиксированное ограничение JWT без blacklist; cookie браузера удаляется немедленно.
- **Отклонённые альтернативы:** самописный JWT/PyJWT, отдельный Bearer-токен, хранение JWT в localStorage, новая таблица сессий/Redis и полная замена SSR на SPA — не выбраны: пользователь указал `template-jwt-auth`/`fastapi-users`, а текущий проект использует Jinja2/HTMX и должен менять фронтенд минимально.
- **Новые зависимости/абстракции:** одна runtime-зависимость `fastapi-users[sqlalchemy]>=15.0,<16` с обновлением `uv.lock`; отдельные тестовые фреймворки не добавляются. Новые auth-модули повторяют границы донора (`core/users.py`, схемы, модель/manager), но используют проектные `Base`, `CurrentSession`, `Settings` и маршруты `md_articles`.
- **Миграции и старые сессии:** Alembic добавляет поля fastapi-users с безопасными значениями по умолчанию (`is_active=true`, `is_superuser=false`, `is_verified=false`) и переименовывает hash-колонку. Старые подписанные session-cookie не конвертируются в JWT: после релиза пользователь выполняет повторный вход; это не потеря записи пользователя или пароля.

## Подтверждённые решения

- «в папке template-jwt-auth код из шаблона авторизации на fastapi-users».
- «нужно посмотреть документацию примера и использовать его».
- «нужно предусмотреть и database как сейчас и jwt стратегии в cookie».
- «фронтенд по минимуму менять только для авторизации».
- Spec-writer должен использовать документацию `template-jwt-auth/docs/` и индекс codebase-memory, а не читать весь текущий проект.
- Эта сессия создаёт и замораживает спецификацию; исполнение фаз запускается в отдельной сессии.

## Результат

После выполнения в репозитории должны существовать:

- зафиксированная зависимость `fastapi-users[sqlalchemy]` и обновлённый `uv.lock`;
- настройки `AUTH` с постоянным секретом, именем/TTL/флагами cookie;
- `fastapi-application/core/users.py` с `CookieTransport`, `JWTStrategy`, `AuthenticationBackend`, `fastapi_users` и единым helper очистки cookie;
- адаптированные `BlogUser`, `UserManager`, `get_user_db`, `get_user_manager`, схемы `UserRead`/`UserCreate`/`UserUpdate` и расширенные поля `username`/`image_file`;
- Alembic-миграция без потери существующих пользователей и bcrypt-хешей;
- стандартные `/auth/cookie/login` и `/auth/cookie/logout`, пользовательский `/auth/users` API без конфликта с `/users` старого домена;
- работающие HTML `/register`, `/login`, `/logout`, `/account`, где current user берётся через fastapi-users, а CSRF/flash продолжают работать через SessionMiddleware;
- минимально изменённые `templates/login.html`, `templates/register.html`, `templates/layout.html` только в частях action/method/имени поля и logout-навигации;
- проверяемый полный flow: миграция → регистрация → логин → cookie → защищённый `/account` → logout → отказ в доступе.

## Вне рамок

- Не переписывать `api/`, `example_sql/`, `ex_order_product/`, общие демонстрационные зависимости и их маршруты.
- Не переносить весь донор 1:1 и не копировать его тестовый проект, docs, шаблоны или архитектуру приложения.
- Не менять дизайн, тексты, layout и поведение блога вне auth-форм, auth-навигации и необходимого контекста `current_user`.
- Не добавлять OAuth-провайдеров, email delivery, reset-password/verify-email UI, refresh-token/blacklist, RBAC и админ-панель; флаги fastapi-users сохраняются для совместимости, но отдельные бизнес-права не расширяются.
- Не хранить JWT в URL, HTML, `localStorage` или логах; не принимать `is_superuser`, `is_active`, `is_verified` из публичной регистрации.
- Не удалять SessionMiddleware и CSRF-механизм: они нужны текущим POST-формам блога.
- Не чинить известные дефекты, не связанные с переносом авторизации, и не добавлять тестовые зависимости без отдельного решения.

## План фаз

Единица исполнения — фаза: одно делегирование, 1–3 файла, бюджет ~10–15 ходов. Следующая фаза стартует только после зелёного checkpoint и ревью диффа оркестратором. Прогресс фазы разработчик фиксирует в `tasks/current/dev/phaseNN_progress.md`.

| # | Фаза | Исполнитель | Файлы | Контракт | Checkpoint | Бюджет ходов |
|---|---|---|---|---|---|---|
| 1 | Зависимость и auth-настройки | backend-dev | `pyproject.toml`, `uv.lock`, `fastapi-application/core/config.py`, `fastapi-application/core/users.py` | `fastapi-users[sqlalchemy]>=15,<16`; `settings.auth.secret_key`, `cookie_name`, `cookie_max_age`, `cookie_secure`, `cookie_samesite`; `get_jwt_strategy()`, `auth_backend`, `fastapi_users`, `get_logout_cookie_value()` | `uv lock --check`; импорт `core.config` и `core.users` из `fastapi-application` без traceback | ~12 |
| 2 | Модель, manager и схемы | backend-dev | `fastapi-application/md_articles/models.py`, `fastapi-application/md_articles/schema_users.py`, `fastapi-application/db_core/__init__.py` | `BlogUser` наследует integer-вариант SQLAlchemy base fastapi-users; поля `hashed_password`, `is_active`, `is_superuser`, `is_verified`, `username`, `image_file`; `UserManager.validate_password`; `get_user_db`; `get_user_manager`; `UserRead/Create/Update` без `hashed_password` наружу; модели реэкспортированы для Alembic | `cd fastapi-application && ../.venv/bin/python -c "from db_core import Base; from md_articles.models import BlogUser; print(BlogUser.__tablename__, sorted(Base.metadata.tables['blog_user'].columns.keys()))"` показывает все обязательные колонки | ~14 |
| 3 | DI и сборка auth-роутеров | backend-dev | `fastapi-application/md_articles/web_utils.py`, `fastapi-application/md_articles/__init__.py`, `fastapi-application/md_articles/routes_users.py` | `get_current_user(request, user=Depends(fastapi_users.current_user(optional=True)))` записывает `request.state.current_user`; `require_login` использует его; SessionMiddleware/CSRF/flash остаются; подключены `/auth/cookie/*` и `/auth/users`; register/login/logout используют fastapi-users и сохраняют текущие HTML names/redirects | импорт `main_app`; список путей содержит `/auth/cookie/login`, `/auth/cookie/logout`, `/auth/users/me`, `/register`, `/login`, `/logout`, `/account`; `ruff check` для файлов фазы | ~15 |
| 4 | SSR-контекст защищённых и публичных страниц | backend-dev | `fastapi-application/md_articles/routes_main.py`, `fastapi-application/md_articles/routes_articles.py` | Все рендерящие blog handlers, которым нужен nav/context, получают `get_current_user`; protected handlers получают единый `require_login`; `request.state.current_user` больше не читается до выполнения dependency; статьи и редиректы сохраняют существующие URL/HTML | точечный Python import всех двух роутеров и smoke GET `/`, `/art_home`, `/art_manage` без пользователя; ожидаются прежние статусы/redirect и отсутствие traceback | ~12 |
| 5 | Миграция существующей БД | backend-dev | `fastapi-application/alembic/versions/<new>_fastapi_users_blog_user.py` | `upgrade`: rename `password` → `hashed_password` с длиной не менее 1024, добавить `is_active=true`, `is_superuser=false`, `is_verified=false`, сохранить username/email/image_file/posts; `downgrade` обратим настолько, насколько позволяет исходная схема; без удаления строк/хешей | `cd fastapi-application && ../.venv/bin/alembic upgrade heads`; затем инспекция `blog_user` и count пользователей; повторный `alembic upgrade heads` идемпотентен через версию миграции | ~10 |
| 6 | Минимальная адаптация auth UI | frontend-dev | `fastapi-application/templates/login.html`, `fastapi-application/templates/register.html`, `fastapi-application/templates/layout.html` | login form-data: `username=<email>`, `password` → `/auth/cookie/login`, успех `204` → `/art_home`; register остаётся `/register` с текущими username/email/password/confirm и CSRF; logout использует существующий `/logout` или явный POST-wrapper с redirect; никаких JWT в JS | просмотр шаблонов + запущенный smoke auth-flow; `curl` подтверждает `Set-Cookie` с `HttpOnly`, `SameSite=Lax`, нужным `Max-Age`, а при Secure-конфигурации — `Secure` | ~10 |
| 7 | QA и полный smoke | qa | `tasks/current/e2e/*.txt`, при дефекте `tasks/current/DEFECTS.md` | проверить миграцию, register/login/logout, invalid credentials, protected access, old-user bcrypt login, CSRF, регресс старых маршрутов; код продукта не менять | все критерии успеха ниже подтверждены сырыми выводами в `tasks/current/e2e/`; открытые дефекты заведены по формату | ~10 |

### Фаза 1: Зависимость и auth-настройки

- **Файлы:** `pyproject.toml`, `uv.lock`, `fastapi-application/core/config.py`, `fastapi-application/core/users.py`.
- **Контракт:** версия fastapi-users закреплена диапазоном `>=15.0,<16`; `core.users` импортирует `FastAPIUsers`, `AuthenticationBackend`, `CookieTransport`, `JWTStrategy`, `User`, `get_user_manager`; TTL cookie и JWT один и тот же; cookie secure/samesite задаются явно.
- **Шаги:** добавить зависимость и обновить lock; добавить вложенный `AuthConfig`; создать auth wiring по образцу `template-jwt-auth/core/users.py`, адаптированный к текущим плоским импортам и Settings.
- **Checkpoint:** `uv lock --check` и `cd fastapi-application && ../.venv/bin/python -c "from core.users import auth_backend, fastapi_users; print(auth_backend.name, type(fastapi_users).__name__)"` завершаются с кодом 0.
- **Готовность фазы:** остальные модули могут импортировать единый `core.users` без самописной JWT-логики.

### Фаза 2: Модель, manager и схемы

- **Файлы:** `fastapi-application/md_articles/models.py`, `fastapi-application/md_articles/schema_users.py`, `fastapi-application/db_core/__init__.py`.
- **Контракт:** `BlogUser.id` остаётся `int`; `hashed_password` — строковое поле с запасом для Argon2; `UserCreate` принимает email/password и username, `UserRead` не содержит hash, `UserUpdate` не раскрывает hash; публичное создание только `safe=True`.
- **Шаги:** заменить ручной bcrypt-контракт на библиотечный hash field без изменения записей; добавить manager/DI; сохранить `BlogPost.author`, `username`, `image_file`, `is_authenticated` и Alembic re-export.
- **Checkpoint:** импорт metadata и проверка колонок; `uv run ruff check fastapi-application/md_articles/models.py fastapi-application/md_articles/schema_users.py fastapi-application/db_core/__init__.py`.
- **Готовность фазы:** можно создать `SQLAlchemyUserDatabase(session, BlogUser)` и получить `UserManager` с integer ID.

### Фаза 3: DI и сборка auth-роутеров

- **Файлы:** `fastapi-application/md_articles/web_utils.py`, `fastapi-application/md_articles/__init__.py`, `fastapi-application/md_articles/routes_users.py`.
- **Контракт:** только `fastapi_users.current_user(...)` проверяет JWT; `get_current_user` переносит результат в state для шаблонов; `require_login` возвращает `BlogUser` либо делает текущий 303 redirect; `POST /register` — form-data и HTML redirect; `/auth/cookie/login` — стандартный form-data роут fastapi-users; `/logout` очищает cookie через единый helper.
- **Шаги:** убрать session `user_id` из auth flow; оставить session только для CSRF/flash; подключить auth routers; сохранить сообщения/валидацию форм и account update, переведя user lookup на fastapi-users dependency.
- **Checkpoint:** `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; paths={getattr(r,'path',None) for r in main_app.routes}; required={'/auth/cookie/login','/auth/cookie/logout','/auth/users/me','/register','/login','/logout','/account'}; print(sorted(required & paths)); assert required <= paths"`.
- **Готовность фазы:** запрос с валидной JWT-cookie получает пользователя того же `BlogUser`, что используют account и article routes.

### Фаза 4: SSR-контекст защищённых и публичных страниц

- **Файлы:** `fastapi-application/md_articles/routes_main.py`, `fastapi-application/md_articles/routes_articles.py`.
- **Контракт:** рендерящие обработчики используют `get_current_user` до вызова `render_template`; защищённые обработчики используют `require_login`; шаблоны по-прежнему получают глобальный `current_user`; URL и существующие ответы блога не меняются.
- **Шаги:** добавить dependency-параметры только в нужные handlers; убрать зависимость от middleware-загрузки `session['user_id']`; не менять article registry, markdown, CSRF и дизайн.
- **Checkpoint:** импорт роутеров и smoke `GET /`, `GET /art_home`, `GET /art_manage` без cookie; ожидаются существующие redirect/403/HTML-ответы.
- **Готовность фазы:** навигация и guards работают с JWT-cookie, а анонимный пользователь не получает 500 или SQLAlchemy detached object.

### Фаза 5: Миграция существующей БД

- **Файл:** новый `fastapi-application/alembic/versions/<revision>_fastapi_users_blog_user.py`.
- **Контракт:** миграция не теряет строки и существующие значения hash; defaults для старых пользователей: active=true, superuser=false, verified=false; downgrade восстанавливает имя `password` и исходные auth-флаги/размер настолько, насколько позволяет SQLite/PostgreSQL dialect.
- **Шаги:** написать ревизию с текущим `down_revision`; использовать batch alter для SQLite при необходимости; проверить схему и количество строк до/после; не запускать `create_all` вместо Alembic.
- **Checkpoint:** `alembic upgrade heads`, повторный `alembic upgrade heads`, SQLAlchemy inspector по `blog_user` и count пользователей.
- **Готовность фазы:** существующий пользователь с bcrypt hash может войти после миграции, а новый пользователь получает hash fastapi-users.

### Фаза 6: Минимальная адаптация auth UI

- **Файлы:** `fastapi-application/templates/login.html`, `fastapi-application/templates/register.html`, `fastapi-application/templates/layout.html`.
- **Контракт:** меняются только auth action/method/field names, обработка ответа login и logout action; все прочие Bootstrap-разметка, тексты и навигация сохраняются. Login не использует `json-enc`, JWT не доступен JavaScript.
- **Шаги:** направить login на `/auth/cookie/login`, переименовать email-поле в `username` только для OAuth2 form contract; сохранить register form/CSRF; обновить logout control на cookie-clearing route.
- **Checkpoint:** ручной просмотр diff шаблонов и curl/browser smoke; cookie имеет HttpOnly/SameSite/TTL, а успешный login приводит на `/art_home`.
- **Готовность фазы:** пользователь может пройти auth flow без ручного копирования токена и без изменения не-auth страниц.

### Фаза 7: QA и полный smoke

- **Файлы:** только `tasks/current/e2e/` и при необходимости `tasks/current/DEFECTS.md`.
- **Контракт:** QA не меняет product code; сырой вывод каждой пачки команд сохраняется в e2e; любой дефект имеет шаги воспроизведения и статус по AGENTS.md.
- **Шаги:** проверить чистую БД/миграцию, регистрацию, login cookie, account, logout, неверный пароль, старого bcrypt-пользователя, CSRF и регресс.
- **Checkpoint:** все критерии успеха ниже имеют PASS и ссылку на e2e-файл; OPEN-дефектов нет либо они переданы разработчику по процессу.
- **Готовность фазы:** QA подтверждает полный flow и отсутствие оставленного тестового сервера после завершения задания.

## Критерии успеха

Проверяются qa по завершении всех фаз; сырые выводы — в `tasks/current/e2e/`.

| # | Критерий | Проверка | Ожидание |
|---|---|---|---|
| 1 | Зависимость и lock согласованы | `uv lock --check && uv run ruff check .` | код 0; fastapi-users найден как runtime dependency; ruff без ошибок |
| 2 | Приложение импортируется и auth routes зарегистрированы | `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; paths={getattr(r,'path',None) for r in main_app.routes}; required={'/auth/cookie/login','/auth/cookie/logout','/auth/users/me','/register','/login','/logout','/account'}; print(len(main_app.routes)); assert required <= paths"` | код 0, все пути присутствуют, старые основные маршруты не исчезли |
| 3 | Схема БД мигрирована без потери пользователей | `cd fastapi-application && ../.venv/bin/alembic upgrade heads` + inspector/count script | код 0; `blog_user` имеет `hashed_password`, `is_active`, `is_superuser`, `is_verified`; count и email/username существующих пользователей сохранены |
| 4 | Регистрация работает через существующую HTML-форму | `curl` с cookie jar на `GET /register`, затем POST form-data `username/email/password/confirm_password` и CSRF | новый пользователь создан один раз; redirect 303 на `/login`; повторный email даёт штатную ошибку без 500 |
| 5 | Login выдаёт JWT в cookie и не отдаёт токен в body | `curl -i -c /tmp/auth.jar -X POST http://127.0.0.1:8000/auth/cookie/login -H 'Content-Type: application/x-www-form-urlencoded' --data 'username=...&password=...'` | `204`; `Set-Cookie` содержит настроенное имя, `HttpOnly`, `SameSite=Lax`, `Max-Age`; JWT отсутствует в response body/HTML |
| 6 | JWT-cookie открывает защищённые страницы | `curl -i -b /tmp/auth.jar http://127.0.0.1:8000/account` и запрос к защищённому `/art_manage` | `200` HTML для валидной cookie; без cookie — текущий redirect на `/login?next=...`, не 500 |
| 7 | Неверный/просроченный/подделанный JWT fail-closed | curl с изменённым значением cookie и без cookie | защищённые routes не показывают аккаунт, не возвращают 500; происходит redirect/unauthorized согласно текущему HTML-контракту |
| 8 | Logout удаляет cookie | `curl -i -b /tmp/auth.jar -c /tmp/auth.jar http://127.0.0.1:8000/logout` и повторный запрос `/account` | redirect на `/art_home`; `Set-Cookie` обнуляет то же имя/path; следующий `/account` требует login |
| 9 | Существующий bcrypt-пользователь совместим | после миграции login старым bcrypt-хешем через `/auth/cookie/login` | вход успешен; пароль не изменяется на plaintext; при поддержке библиотеки hash может быть обновлён после успешной проверки |
| 10 | Серверная парольная политика работает | регистрация/смена пароля с длиной менее 8 и с несовпадающим confirm | отказ 400/HTML-ошибка; пользователь не создан и старый пароль не изменён |
| 11 | CSRF текущего блога сохранён | POST `/register`/`/account` без token и с неверным token | `403`, данные не меняются; валидный token продолжает работать |
| 12 | Регресс текущего проекта отсутствует | пачка curl: `/docs`, `/users/get_all_users`, `/orders/get_all_orders`, `/api/v1/dep_examples/single-direct-dependency`, `/art_home`, `/static/art_css/base.css` | статусы/тела соответствуют существующему контракту; приложение стартует из `fastapi-application` |
| 13 | Фронтенд изменён только для auth | `git diff --stat` и просмотр diff трёх auth-шаблонов | нет изменений дизайна/статических страниц вне auth action, field name, login response и logout control |

## Финальные критерии

1. Каждый критерий успеха подтверждён выводом в `tasks/current/e2e/`.
2. `tasks/current/DEFECTS.md` существует только если найдены дефекты; к закрытию нет записей со статусом OPEN.
3. Adversarial-прогон не входит в это задание, если пользователь отдельно не добавит его в контракт; `ADVERSARIAL_REVIEW.md` не создаётся автоматически.
4. После QA тестовый `uvicorn` остановлен, порт 8000 свободен.

## Открытые вопросы

Нет. Если в ходе реализации выяснится несовместимость integer-модели fastapi-users, разработчик обязан сохранить integer ID и существующие данные, выбрать соответствующий generic SQLAlchemy base из установленной версии и зафиксировать решение в progress-файле, не переходя на UUID или новую таблицу без отдельного изменения контракта.

---

# Отчёт о выполнении

- Дата закрытия: 2026-09-13
- Коммит: не создавался

## Итог
Авторизация блога перенесена на `fastapi-users` с JWT в HttpOnly-cookie, сохранены integer ID, существующие пользователи и bcrypt-совместимость; миграция, полный auth-flow, CSRF, fail-closed проверки и регресс подтверждены артефактами [`e2e/phase07_preflight.txt`](e2e/phase07_preflight.txt), [`e2e/phase07_runtime_auth.txt`](e2e/phase07_runtime_auth.txt) и [`e2e/phase07_completion.txt`](e2e/phase07_completion.txt).
