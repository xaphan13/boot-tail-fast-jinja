# 01. Карта проекта

> Часть 1 из 4. См. также: [02_architecture.md](02_architecture.md), [03_execution_flow.md](03_execution_flow.md), [04_code_quality.md](04_code_quality.md)

## Назначение

`one-fastApi` — **учебно-демонстрационный проект на FastAPI 0.111+ / Python 3.12**, построенный как исполняемый каталог приёмов, а не как продуктовый сервис. Основная масса кода существует, чтобы показать варианты одного и того же решения рядом друг с другом: четыре способа извлечения параметров HTTP-запроса, девять способов внедрения зависимостей (`Depends`), два стиля объявления pydantic-полей (`Field` против `Annotated`), два способа валидации (`AfterValidator` против `field_validator`) и два способа разбора результата SQLAlchemy `joinedload`.

Вторая, меньшая часть проекта — рабочий асинхронный слой данных на SQLAlchemy 2.0 (`AsyncSession`, `asyncpg`/`aiosqlite`) с миграциями Alembic и двумя предметными областями: `User`/`Post` (one-to-many) и `Order`/`Product` (many-to-many с явной ассоциативной моделью). Эта часть пригодна как основа для реального сервиса, но требует доработок, перечисленных в [04_code_quality.md](04_code_quality.md).

**Что важно понимать перед работой с кодом:** дублирование маршрутов и обработчиков здесь **намеренное**. Четыре файла `api/my_routes_dep/my_param_*.py` реализуют один и тот же эндпоинт `/my_items/{item_id}` с идентичной семантикой — сравнивать их построчно и есть цель. Не «рефакторьте» это в общий код, не выяснив задачу.

---

## Дерево директорий

```
one-fastApi/
├── docs/                            # Эта документация
├── fastapi-application/             # Корень Python-приложения (= BASE_DIR)
│   ├── main.py                      # Точка входа uvicorn; сборка main_app + include_router
│   ├── main_gunicorn.py             # Точка входа gunicorn; переиспользует main_app
│   ├── create_fastapi.py            # Фабрика приложения create_app() + lifespan
│   ├── base_dir_path.py             # DIR_CWD / BASE_DIR (Path)
│   ├── config_log.py                # Автономная подсистема логирования (dictConfig)
│   ├── alembic.ini                  # Конфиг Alembic; post-write hook = black -l 79
│   ├── one.env                      # Профиль PostgreSQL (закоммичен в git)
│   ├── two.env                      # Профиль SQLite (активен по умолчанию)
│   │
│   ├── core/
│   │   ├── config.py                # Settings(BaseSettings) — весь конфиг приложения
│   │   └── gunicorn/
│   │       ├── gunicorn_app.py      # MyGunicornApp(BaseApplication)
│   │       ├── gunicorn_opt.py      # get_app_options() → dict опций gunicorn
│   │       └── gunicorn_log.py      # GunicornLogger(Logger) — свой формат логов
│   │
│   ├── db_core/                     # Инфраструктура БД, не зависит от предметных областей
│   │   ├── __init__.py              # Реэкспорт Base + всех моделей (нужен Alembic)
│   │   ├── db_async.py              # AsyncDbManager, db_manager, CurrentSession
│   │   ├── model_base.py            # Base(DeclarativeBase) + автогенерация __tablename__
│   │   ├── type_for_models.py       # Annotated-типы колонок (int_primary_key и др.)
│   │   └── case_converter.py        # camel_case_to_snake_case()
│   │
│   ├── api/                         # Демонстрационная часть, версионируется под /api/v1
│   │   ├── __init__.py              # router_api (/api) → router_api_v1 (/v1)
│   │   ├── dependencies/            # МЕХАНИКА Depends: 9 роутов
│   │   │   ├── __init__.py          # router_dep_examples
│   │   │   ├── func_deps.py         # Фабрика зависимостей get_header_dependency()
│   │   │   ├── cls_deps.py          # Классы-зависимости: __call__, метод, генератор
│   │   │   ├── helper.py            # BaseGreat → GreatHelper / GreatService
│   │   │   ├── dep_examp_simple.py  # 4 роута: простые зависимости
│   │   │   └── dep_examp_cls.py     # 5 роутов: классовые зависимости
│   │   └── my_routes_dep/           # ИЗВЛЕЧЕНИЕ ПАРАМЕТРОВ: 4 стиля одного эндпоинта
│   │       ├── __init__.py          # router_param_extract + 4 префикса
│   │       ├── my_param_fast_cls.py    # Стиль 1: Path()/Query() как default-значения
│   │       ├── my_param_fast_ann.py    # Стиль 2: то же через Annotated
│   │       ├── my_param_dep_cls.py     # Стиль 3: параметры собраны в классы
│   │       ├── my_param_dep_func.py    # Стиль 4: параметры собраны в функции
│   │       ├── dep_cls_schema.py       # PathData/QueryData/HeaderData/CookieData
│   │       ├── dep_func_schema.py      # get_item_id/get_param_id/get_user_id/...
│   │       ├── pydantic_schema.py      # RespFieldStyle vs RespAnnotated
│   │       └── pydantic_validator.py   # RespAfterValid vs RespDecorValid
│   │
│   ├── example_sql/                 # Домен User/Post — слоистая раскладка
│   │   ├── router_users.py          # r_users_sql (/users): 2 роута
│   │   ├── crud/crud_users.py       # get_all_users(), create_user()
│   │   ├── models/
│   │   │   ├── model_user_post.py   # User, Post (one-to-many)
│   │   │   ├── model_user_mix.py    # TestUser — НЕ подключён к Alembic
│   │   │   └── model_id_pk_mixin.py # IntIdPkMixin
│   │   └── schemas/schema_user.py   # UserCreate/UserResp, PostCreate/PostResp
│   │
│   ├── ex_order_product/            # Домен Order/Product — БЕЗ слоя CRUD
│   │   ├── router_order_one.py      # r_order_one (/orders): 6 роутов, SQL внутри
│   │   ├── model_order_product.py   # Order, Product, OrderProductAssociation
│   │   └── schema_order_product.py  # 20+ pydantic-схем, включая вложенные Resp
│   │
│   ├── utils/docs.py                # reg_docs_routes() — свои Swagger/ReDoc с CDN
│   │
│   └── alembic/
│       ├── env.py                   # Асинхронный runner; url из settings.db.url
│       └── versions/
│           ├── ...--59bdab4b2e7c--user_post.py      # users, posts
│           └── ...--35ae229e79dd--order_product.py  # orders, products, association
│
├── nginx/
│   ├── Docker-nginx                 # nginx:1.20-alpine + копирование conf/web/cert
│   ├── nginx.conf                   # TLS-терминация, reverse proxy для xaphan.ru
│   └── web/default/                 # index.html, custom_50x.html
│
├── docker-compose.yml               # Локальная разработка: pg + adminer + pgadmin
├── nginx_pg_admin.yml               # Прод-подобный стек: pg + pgadmin + redis + nginx
├── Makefile                         # Запуск uvicorn, alembic, docker network
├── adminGit.sh                      # CLI-обёртка над git
├── adminDock.sh                     # CLI-обёртка над docker
├── pyproject.toml                   # Зависимости (uv), конфиг ruff + black
├── uv.lock                          # Лок-файл uv
├── .python-version                  # 3.12
└── Install-run.md                   # Шпаргалка по командам запуска
```

---

## Ключевые модули и их абстракции

### Точки входа и сборка приложения

| Файл | Ответственность | Абстракции |
|---|---|---|
| `fastapi-application/main.py` | Собирает `main_app`: вызывает `create_app()`, подключает три корневых роутера. Функция `main()` запускает `uvicorn.run("main:main_app", reload=True)`. | `main_app: FastAPI`, `main()` |
| `fastapi-application/main_gunicorn.py` | Импортирует **готовый** `main_app` из `main.py` и оборачивает в `MyGunicornApp` с опциями из `get_app_options()`. Дублирования сборки нет. | `main()` |
| `fastapi-application/create_fastapi.py` | Единственное место создания `FastAPI`. Настраивает `ORJSONResponse` по умолчанию, `lifespan`, переключает встроенные `/docs` на кастомные по флагу. | `create_app()`, `lifespan()` |
| `fastapi-application/base_dir_path.py` | Два `Path`-константы. `BASE_DIR` = каталог `fastapi-application/`, служит якорем для `.env` и папки логов. | `DIR_CWD`, `BASE_DIR` |

### Конфигурация

| Файл | Ответственность | Абстракции |
|---|---|---|
| `fastapi-application/core/config.py` | Вся конфигурация как вложенные pydantic-модели. Читает env с префиксом `APP__` и разделителем `__`. Единственное обязательное поле — `db.url`. | `Settings`, `DatabaseConfig`, `RunConfig`, `ApiPrefix`, `ApiV1Prefix`, `GunicornConfig`, `LoggingConfigGunicorn`, `SqliteDsn`, `settings` |
| `fastapi-application/one.env` | Профиль PostgreSQL: `postgresql+asyncpg://user:password@localhost:5432/shop`. Подключается **раскомментированием строки в коде**. | — |
| `fastapi-application/two.env` | Профиль SQLite: `sqlite+aiosqlite:///./one_simple.db`, `ECHO=1`. Активен. | — |

`SqliteDsn` — кастомный `AnyUrl` с `UrlConstraints(allowed_schemes=["sqlite", "sqlite+aiosqlite"], host_required=False)`. Без `host_required=False` pydantic отверг бы URL вида `sqlite+aiosqlite:///./one_simple.db`.

### Слой доступа к данным

| Файл | Ответственность | Абстракции |
|---|---|---|
| `fastapi-application/db_core/db_async.py` | Владеет движком и фабрикой сессий. Регистрирует хук `PRAGMA foreign_keys=ON` для SQLite. Экспортирует единый DI-алиас сессии. | `AsyncDbManager`, `db_manager`, `CurrentSession` |
| `fastapi-application/db_core/model_base.py` | Декларативная база с общим `MetaData` и `naming_convention` из настроек. Автогенерирует `__tablename__` через `declared_attr.directive`. | `Base` |
| `fastapi-application/db_core/type_for_models.py` | Переиспользуемые `Annotated`-типы колонок, убирающие повторение `mapped_column(...)` в моделях. | `int_primary_key`, `time_stamp_utc`, `str_len_50`, `str_len_100` |
| `fastapi-application/db_core/case_converter.py` | `CamelCase` → `snake_case` с корректной обработкой аббревиатур (`SomeSDK` → `some_sdk`). Есть doctest-примеры. | `camel_case_to_snake_case()` |
| `fastapi-application/db_core/__init__.py` | Реэкспорт `Base` и моделей. **Критично**: именно этот импорт наполняет `Base.metadata` для Alembic `--autogenerate`. | `__all__` |

`CurrentSession = Annotated[AsyncSession, Depends(db_manager.get_async_session)]` — вся инъекция сессии сведена к одной аннотации; роуты пишут `db: CurrentSession`.

### Модели и схемы

| Файл | Ответственность | Абстракции |
|---|---|---|
| `example_sql/models/model_user_post.py` | `User` (уникальный `nickname`, составной `UniqueConstraint(firstname, surname)`) и `Post` с FK на `users.id` (`CASCADE` на delete и update). | `User`, `Post` |
| `example_sql/models/model_user_mix.py` | `TestUser` — демонстрация примеси PK. Не реэкспортирован в `db_core/__init__.py`, поэтому невидим для Alembic. | `TestUser` |
| `example_sql/models/model_id_pk_mixin.py` | Примесь с индексируемым целочисленным PK. | `IntIdPkMixin` |
| `example_sql/schemas/schema_user.py` | Схемы запросов/ответов. `UserResp(UserCreate)` наследует поле `password` — см. [04_code_quality.md](04_code_quality.md). | `UserCreate`, `UserResp`, `PostCreate`, `PostResp` |
| `ex_order_product/model_order_product.py` | Many-to-many `Order ↔ Product` через явную `OrderProductAssociation` с полезной нагрузкой (`count`, `unit_price`) и `UniqueConstraint(order_id, product_id)`. `__tablename__` переопределён вручную. | `Order`, `Product`, `OrderProductAssociation` |
| `ex_order_product/schema_order_product.py` | 20+ схем: query/body/response, включая иерархию вложенных ответов для разных вариантов `joinedload`. | `OrderResp`, `OrderRespWithProducts`, `ProductRespWithOrders`, `AssociationResp`, `OrderGetAllOrderbyQuery` и др. |

### Демонстрационная часть `api/`

| Файл | Что демонстрирует |
|---|---|
| `api/dependencies/func_deps.py` | Фабрика зависимостей: `get_header_dependency(name, default)` возвращает замыкание-зависимость. Позволяет параметризовать имя заголовка. |
| `api/dependencies/cls_deps.py` | Три способа сделать класс зависимостью: `__call__` (`HeaderAccessDependency`), метод-генератор с teardown (`PathReaderDependency.as_dependency`), pydantic-модели результата (`TokenData`, `TokenIntrospectResult`). |
| `api/dependencies/helper.py` | `GreatService.__init__` сам объявляет `Header(...)`-параметры, поэтому класс работает как зависимость напрямую через `Depends(GreatService)`. `GreatHelper` требует фабрику. |
| `api/dependencies/dep_examp_simple.py` | 4 роута: прямой `Header()`, зависимость-функция, смешанный вариант, две параметризованные зависимости. |
| `api/dependencies/dep_examp_cls.py` | 5 роутов: создание объекта в обработчике, фабрика, класс как зависимость, метод как зависимость, проверка токена. |
| `api/my_routes_dep/my_param_*.py` | Четыре реализации `GET /my_items/{item_id}`, извлекающие `Path`/`Query`/`Header`/`Cookie`/`Request`/`Response`. Различие только в стиле объявления. |
| `api/my_routes_dep/pydantic_schema.py` | `Field(...)` как default-значение против `Annotated[T, Field(...)]`. |
| `api/my_routes_dep/pydantic_validator.py` | Валидация через `Annotated` + `AfterValidator` (`RespAfterValid`, `frozen=True`) против декоратора `@field_validator` (`RespDecorValid`). |

### Вспомогательные подсистемы

| Файл | Ответственность | Абстракции |
|---|---|---|
| `fastapi-application/config_log.py` | Автономная подсистема логирования на `logging.config.dictConfig`. Настраивается **на импорте модуля** (`config_log.py:126`), создаёт папку логов, ротация 1 МБ × 20 файлов. Не связана с FastAPI и не перехватывает логи uvicorn (блок закомментирован). | `ConfigLogger`, `create_config_dict()`, `logF`, `logFC` |
| `fastapi-application/utils/docs.py` | Регистрирует свои `/docs`, `/redoc` и OAuth2-redirect с ассетами Swagger/ReDoc из CDN unpkg. Включается флагом `create_app(custom_docs_url=True)`. | `reg_docs_routes()` |
| `core/gunicorn/gunicorn_app.py` | Обёртка `gunicorn.app.base.BaseApplication`: позволяет запускать gunicorn программно с готовым ASGI-объектом. Фильтрует неизвестные и `None`-опции. | `MyGunicornApp` |
| `core/gunicorn/gunicorn_opt.py` | Собирает dict опций: `bind`, `workers`, `timeout`, `worker_class="uvicorn.workers.UvicornWorker"`, `logger_class`. | `get_app_options()` |
| `core/gunicorn/gunicorn_log.py` | Переопределяет форматтеры access- и error-логов gunicorn форматом из `settings.logging_gunicorn.log_format`. | `GunicornLogger` |
| `alembic/env.py` | Асинхронный runner миграций. Подставляет `settings.db.url` в `sqlalchemy.url` в рантайме и берёт `target_metadata` из `db_core.Base`. Использует `pool.NullPool`. | `run_migrations_online()`, `run_async_migrations()`, `do_run_migrations()` |

---

## Внешние зависимости

### Обязательные в рантайме

| Компонент | Роль | Где сконфигурировано |
|---|---|---|
| **СУБД: PostgreSQL или SQLite** | Единственное хранилище состояния. Драйверы: `asyncpg` (PostgreSQL) и `aiosqlite` (SQLite). Переключение — выбором активного `.env` в кортеже `env_file`. | `core/config.py:88-93`, `one.env`, `two.env` |
| **ASGI-сервер: uvicorn или gunicorn** | uvicorn — dev-режим с `reload=True`. gunicorn с `UvicornWorker` — многопроцессный режим. | `main.py`, `main_gunicorn.py`, `core/gunicorn/` |

### Инфраструктура (docker)

| Компонент | Роль | Где |
|---|---|---|
| **PostgreSQL 16** | Основная СУБД в прод-подобном стеке. Порт `7032:5432`, статический IP `172.20.0.2`, данные в `./pg_db`. | `nginx_pg_admin.yml` |
| **PostgreSQL (latest)** | СУБД для локальной разработки. Порт `5432:5432`, БД `shop`, без volume — **данные не сохраняются между перезапусками**. | `docker-compose.yml` |
| **pgAdmin 4** | Веб-администрирование БД. В dev — порт `5050`, в прод-стеке — за nginx по пути `/pgadmin`. | оба compose-файла |
| **Adminer** | Альтернативный веб-клиент БД, порт `8080`. Только в dev. | `docker-compose.yml` |
| **nginx 1.20-alpine** | TLS-терминация для `xaphan.ru` (сертификаты из `nginx/cert/`, в git не попадают), редирект 80→443, reverse proxy на pgadmin, flower и два приложения. | `nginx/Docker-nginx`, `nginx/nginx.conf` |
| **Redis 6.2-alpine** | Объявлен в прод-стеке (порт `7079:6379`, IP `172.20.0.4`), но **в коде приложения не используется** — нет клиента Redis в зависимостях. Задел на будущее. | `nginx_pg_admin.yml` |

### Сторонние API

Внешних HTTP-API проект не вызывает. Единственная внешняя сетевая зависимость — **CDN unpkg.com**, откуда `utils/docs.py` тянет ассеты Swagger UI и ReDoc. Активна только при `create_app(custom_docs_url=True)`; сейчас вызов идёт с `False`, поэтому используются встроенные ассеты FastAPI.

### Библиотеки

Из `pyproject.toml`, менеджер — **uv** (`[tool.uv] package = false`):

`fastapi>=0.111.0`, `uvicorn[standard]>=0.40.0`, `gunicorn>=23,<24`, `pydantic[email]>=2.7.1,<3`, `pydantic-settings>=2.2.1,<3`, `sqlalchemy[asyncio]>=2.0.30,<3`, `alembic>=1.13.1,<2`, `asyncpg>=0.31.0`, `aiosqlite>=0.22.1`, `orjson>=3.11.5`.

Линтеры `ruff>=0.14.10` и `black>=25.0.0` объявлены в основных `dependencies`, а не в dev-группе. `ruff` настроен на `line-length = 100` и игнорирует `F401`, `E402`, `F541`; `black` — на `line-length = 120`. **Настройки длины строки противоречат друг другу.**

### Чего в проекте нет

- Тестов — ни одного файла (`test_*.py`, `conftest.py`, `pytest.ini` отсутствуют)
- CI/CD — нет `.github/workflows`, нет `.gitlab-ci.yml`
- `Dockerfile` для самого приложения — есть только `nginx/Docker-nginx`; приложение в контейнере не собирается
- Кэша, брокера сообщений, очередей задач — `nginx.conf` проксирует `flower_first`/`flower_two`, а прод-стек поднимает Redis, но Celery в кодовой базе отсутствует
