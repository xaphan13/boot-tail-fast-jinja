# Фаза 2 — прогресс

Дата: 2026-09-13

- План: обновить `md_articles/models.py` под integer SQLAlchemy adapter fastapi-users; одним файлом создать `md_articles/schema_users.py`; сохранить реэкспорт `BlogUser` в `db_core/__init__.py`; выполнить точечные проверки.
- Ограничения: изменяются только `fastapi-application/md_articles/models.py`, `fastapi-application/md_articles/schema_users.py`, `fastapi-application/db_core/__init__.py` и этот progress-файл; роутеры, шаблоны, миграции, конфиг и `pyproject.toml` не трогаются; коммит не выполняется.
- Контракт: integer `BlogUser.id`; `hashed_password` с запасом для Argon2; `is_active`, `is_superuser`, `is_verified` с безопасными default; `UserManager`, `get_user_db`, `get_user_manager`; public create через fastapi-users `safe=True`; hash не раскрывается схемами.
- Статус: подготовка завершена; изучены AGENTS.md, фаза 2 REQUIREMENTS.md, progress фазы 1, целевые исходники, ближайшие модели/схемы и релевантные документы `template-jwt-auth`. До реализации проверяется фактический integer API установленного fastapi-users 15.0.5.
- Решение integer API: fastapi-users 15.0.5 предоставляет generic `SQLAlchemyBaseUserTable[ID]` без собственной PK-колонки и `IntegerIDMixin`; сохранён `BlogUser.id: Mapped[int_primary_key]`, модель наследует `SQLAlchemyBaseUserTable[int]`, manager — `IntegerIDMixin, BaseUserManager[BlogUser, int]`. UUID-вариант не применён, потому что контракт сохраняет integer ID.
- 2026-09-13 — `fastapi-application/md_articles/models.py`: `BlogUser` переведён на `SQLAlchemyBaseUserTable[int]`; сохранены `blog_user`, integer id, username/email/image_file/posts; добавлены библиотечные `hashed_password VARCHAR(1024)` и boolean-флаги с default fastapi-users; добавлены `UserManager`, integer `get_user_db`, `get_user_manager`, серверная проверка пароля минимум 8 символов. Import: PASS (`blog_user VARCHAR(1024) INTEGER IntegerIDMixin`). Ruff: PASS.
- 2026-09-13 — `fastapi-application/md_articles/schema_users.py`: создан единый файл `UserRead/UserCreate/UserUpdate`; read/update не содержат `hashed_password`, create принимает username/email/password/image_file, административные поля присутствуют только базово для совместимости и вырезаются manager при `safe=True`. Import: PASS; ruff: PASS.
- 2026-09-13 — `fastapi-application/db_core/__init__.py`: сохранён и явно документирован реэкспорт `BlogUser`/`BlogPost`, необходимый для наполнения `Base.metadata` и Alembic. Import metadata: PASS; ruff: PASS.

## Сырые выводы проверок

```text
../.venv/bin/python -c "...from md_articles.models..."
blog_user VARCHAR(1024) INTEGER IntegerIDMixin

../.venv/bin/ruff check md_articles/models.py
All checks passed!

../.venv/bin/python -c "...from md_articles.schema_users..."
dict_keys(['email', 'password', 'is_active', 'is_superuser', 'is_verified', 'username', 'image_file']) dict_keys(['id', 'email', 'is_active', 'is_superuser', 'is_verified', 'username', 'image_file']) dict_keys(['password', 'email', 'is_active', 'is_superuser', 'is_verified', 'username', 'image_file'])

../.venv/bin/ruff check md_articles/schema_users.py
All checks passed!

../.venv/bin/python -c "from db_core import Base; from md_articles.models import BlogUser; print(BlogUser.__tablename__, sorted(Base.metadata.tables['blog_user'].columns.keys()))"
blog_user ['email', 'hashed_password', 'id', 'image_file', 'is_active', 'is_superuser', 'is_verified', 'username']

../.venv/bin/ruff check md_articles/models.py md_articles/schema_users.py db_core/__init__.py
All checks passed!

../.venv/bin/python -c "from core.users import auth_backend, fastapi_users; from md_articles.models import UserManager, get_user_db, get_user_manager; print(auth_backend.name, type(fastapi_users).__name__, UserManager.__name__)"
jwt FastAPIUsers UserManager

../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"
43

safe-create/password-policy/hash-helper check
safe-create PASS; password-policy PASS; argon2-helper PASS
```

- Примечание о проверке: первый вариант дополнительной async-проверки через `python -c` завершился `SyntaxError` из-за объявления `async def` после `;`; продукт не выполнялся этой командой. Повторённый heredoc-прогон завершился PASS.
- Итог фазы: обязательный metadata checkpoint PASS; точечный ruff PASS; импорт auth wiring и полный smoke-import приложения PASS. Коммит не выполнялся.
