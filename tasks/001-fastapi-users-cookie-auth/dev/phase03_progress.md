# Фаза 3 — прогресс

Дата: 2026-09-13

- План: перевести SSR current-user/guard на dependency fastapi-users, подключить стандартные auth/users routers и перевести HTML register/login/logout/account на JWT-cookie без изменения URL/имен/CSRF/flash.
- Ограничения: изменяются только `fastapi-application/md_articles/web_utils.py`, `fastapi-application/md_articles/__init__.py`, `fastapi-application/md_articles/routes_users.py` и этот progress-файл; `routes_main.py`, `routes_articles.py`, шаблоны и миграции не трогаются; коммит не выполняется.
- Подготовка: изучены AGENTS.md, контракт фазы 3, progress фаз 1/2, три целевых модуля, `core/users.py`, модели/схемы пользователя, `create_fastapi.py`, шаблоны auth/account и релевантные материалы `template-jwt-auth`.
- 2026-09-13 — `fastapi-application/md_articles/web_utils.py`: `get_current_user` переведён на единственную dependency `fastapi_users.current_user(optional=True)` с записью в `request.state.current_user`; `require_login` использует тот же результат и возвращает `BlogUser` либо сохраняет redirect 303 на `/login?next=...`; session `user_id` и ручной bcrypt-контур удалены, CSRF/flash сохранены.
- 2026-09-13 — `fastapi-application/md_articles/__init__.py`: SessionMiddleware оставлен для session-only CSRF/flash; добавлены стандартные `get_auth_router` под `/auth/cookie` и `get_users_router` под `/auth/users`; устранён цикл импорта отложенными импортами внутри `register_md_articles`.
- 2026-09-13 — `fastapi-application/md_articles/routes_users.py`: HTML register вызывает `UserCreate` и `user_manager.create(..., safe=True)` без privilege flags; HTML login использует fastapi-users manager/auth backend и ставит JWT-cookie; logout очищает cookie через `get_logout_cookie_value()` и редиректит на `/art_home`; account получает пользователя через `require_login`; URL/names/CSRF/flash сохранены.

- 2026-09-13 — Дополнительная узкая проверка `md_articles.web_utils` сначала выявила цикл импорта `core.users -> md_articles.models -> db_core.__init__ -> md_articles.models`; в рамках разрешённых файлов добавлен harmless import `Base` в `md_articles.__init__`, чтобы пакет `db_core` был инициализирован до auth wiring. После адаптации прямой импорт `web_utils/routes_users` и прямой import auth wiring проходят.

## Checkpoint

- Import/path checkpoint: PASS. `from main import main_app` завершился успешно; обязательные пути найдены: `['/account', '/auth/cookie/login', '/auth/cookie/logout', '/auth/users/me', '/login', '/logout', '/register']`.
- Ruff checkpoint: PASS. `../.venv/bin/ruff check md_articles/web_utils.py md_articles/__init__.py md_articles/routes_users.py` → `All checks passed!`.

## Замечания

- Фаза 4 должна адаптировать `routes_main.py` и `routes_articles.py` к явной dependency `get_current_user`: middleware-загрузка пользователя удалена по контракту фазы 3, а эти файлы в текущей фазе запрещены к изменению.
- Шаблоны не изменялись по контракту фазы 3; текущая HTML-форма `/login` сохранена, а стандартный машинный form-data endpoint остаётся `/auth/cookie/login`. Адаптация auth UI выполняется фазой 6.
- Финальная проверка состава: изменены только три разрешённых Python-файла и создан `phase03_progress.md`; `git diff --check` — PASS.
- Исправленная финальная команда `ruff` из `fastapi-application/`: `../.venv/bin/ruff check md_articles/web_utils.py md_articles/__init__.py md_articles/routes_users.py` → `All checks passed!`.
- Примечание: одна попытка той же команды из корня завершилась `127` из-за неверного относительного пути `../.venv/bin/ruff`; повтор с требуемым cwd прошёл, продуктовой ошибки нет.

## Сырые выводы проверок

```text
../.venv/bin/python -c "from md_articles.web_utils import get_current_user, require_login; from md_articles.routes_users import router_users; print(get_current_user.__name__, require_login.__name__, router_users.prefix)"
get_current_user require_login

../.venv/bin/python -c "from core.users import auth_backend, fastapi_users; from md_articles.routes_users import router_users; print(auth_backend.name, type(fastapi_users).__name__, len(router_users.routes))"
jwt FastAPIUsers 7

../.venv/bin/python -c "from main import main_app; paths={getattr(r,'path',None) for r in main_app.routes}; required={'/auth/cookie/login','/auth/cookie/logout','/auth/users/me','/register','/login','/logout','/account'}; print(sorted(required & paths)); assert required <= paths"
['/account', '/auth/cookie/login', '/auth/cookie/logout', '/auth/users/me', '/login', '/logout', '/register']

../.venv/bin/ruff check md_articles/web_utils.py md_articles/__init__.py md_articles/routes_users.py
All checks passed!

git diff --check -- fastapi-application/md_articles/web_utils.py fastapi-application/md_articles/__init__.py fastapi-application/md_articles/routes_users.py tasks/current/dev/phase03_progress.md
[no output; exit 0]
```
