# Фаза 1 — прогресс

Дата: 2026-09-13

- План: обновить зависимость и lock; добавить `AuthConfig` в `core/config.py`; создать `core/users.py` с cookie/JWT wiring без привязки к модели следующей фазы.
- Ограничения: изменяются только `pyproject.toml`, `uv.lock`, `fastapi-application/core/config.py`, `fastapi-application/core/users.py` и этот progress-файл; коммит не выполняется.
- Статус: подготовка завершена; до первой записи изучены AGENTS.md, контракт фазы 1, текущие config/dependency файлы и донорский auth wiring.
- 2026-09-13 — `pyproject.toml`: добавлена runtime-зависимость `fastapi-users[sqlalchemy]>=15.0,<16`. Проверки файла: ожидается `uv lock` после обновления lock.
- 2026-09-13 — `uv.lock`: обновлён через `uv lock`; добавлены `fastapi-users 15.0.5`, SQLAlchemy adapter и транзитивные auth-зависимости. Проверка `uv lock`: PASS.
- 2026-09-13 — `fastapi-application/core/config.py`: добавлен вложенный `AuthConfig` с `secret_key`, `cookie_name`, `cookie_max_age`, `cookie_secure=False`, `cookie_samesite='lax'`, подключён как `settings.auth`. Проверка: точечная конфигурационная правка завершена; импорт проверяется после auth wiring.
auth 3600 jwt FastAPIUsers
All checks passed!
- 2026-09-13 — `fastapi-application/core/users.py`: создано cookie/JWT wiring с TTL из `settings.auth`, явными secure/samesite и helper `get_logout_cookie_value()`, integer generic `FastAPIUsers[User, int]`; до фазы 2 используется безопасная import-заглушка manager. Импорт: PASS (`auth 3600 jwt FastAPIUsers`); ruff: PASS.
Resolved 56 packages in 1ms
jwt FastAPIUsers
All checks passed!
