# Фаза 5 — прогресс

Дата: 2026-09-13

- План: создать одну новую Alembic-ревизию для существующей `blog_user`; в `upgrade` переименовать и расширить hash-колонку, добавить auth-флаги с безопасными server defaults; в `downgrade` убрать новые поля и вернуть имя/размер исходного hash-поля без удаления строк.
- Ограничения: изменяются только новая миграция `fastapi-application/alembic/versions/<revision>_fastapi_users_blog_user.py` и этот progress-файл; существующие ревизии, модели, конфиг, роутеры и шаблоны не трогаются; `create_all` не используется; коммит не выполняется.
- Фактическая цепочка ревизий: `59bdab4b2e7c` → `35ae229e79dd` → `b59cbdf15878` (текущий head); новая ревизия использует `down_revision = "b59cbdf15878"`.
- Исходная ревизия `b59cbdf15878` создаёт `blog_user.password` как `VARCHAR(60) NOT NULL` и сохраняет `id`, `username`, `email`, `image_file`; `blog_post.user_id` ссылается на `blog_user.id`. Модель после фаз 1–4 ожидает `hashed_password` длиной 1024 и поля `is_active`, `is_superuser`, `is_verified`.
- Первичная проверка Alembic: `alembic heads` показал `b59cbdf15878 (head)`; `alembic current` не вывел применённую revision (выход 0), поэтому состояние БД будет проверено после создания ревизии. Файл `*.db` в репозитории не найден.
- 2026-09-13 — progress-файл создан до записи миграции; начальные проверки и контракт зафиксированы. Статус: migration pending.
- 2026-09-13 — `fastapi-application/alembic/versions/2026-09-13_00-00--a1c2d3e4f5a6--fastapi_users_blog_user.py`: создана ревизия `a1c2d3e4f5a6` с `down_revision=b59cbdf15878`; upgrade использует `batch_alter_table`, переименовывает `password` в `hashed_password` длиной 1024 и добавляет non-null auth flags с true/false/false server defaults; downgrade удаляет только новые flags и возвращает `password` длиной 60. Импорт: PASS. Ruff: PASS. Статус: migration file complete; checkpoint pending.
- 2026-09-13 — SQLite checkpoint: первый `alembic upgrade heads` и повторный upgrade завершились с кодом 0; inspector подтвердил `hashed_password VARCHAR(1024)`, `is_active/is_superuser/is_verified BOOLEAN` с defaults `1/0/0`, сохранённую связь `blog_post.user_id → blog_user.id`; в БД сохранены 7 пользователей и 7 непустых bcrypt-хешей длиной 60, email/username не изменены. Финальный `alembic current`: `a1c2d3e4f5a6 (head)`. Checkpoint: PASS.

## Сырые выводы проверок

```text
$ ../.venv/bin/alembic heads
b59cbdf15878 (head)

$ ../.venv/bin/alembic current
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
Error: (none)
Exit Code: 0

$ ../.venv/bin/python -c "... import new migration ..."
migration import PASS a1c2d3e4f5a6 b59cbdf15878

$ ../.venv/bin/ruff check alembic/versions/2026-09-13_00-00--a1c2d3e4f5a6--fastapi_users_blog_user.py
All checks passed!
```

$ ../.venv/bin/alembic upgrade heads (first)
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade b59cbdf15878 -> a1c2d3e4f5a6, Migrate blog_user to fastapi-users fields.
exit=0

$ ../.venv/bin/alembic upgrade heads (repeat)
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
exit=0

checkpoint_exit_codes first=0 repeat=0
inspector columns: [('id', 'INTEGER', False, None), ('username', 'VARCHAR(20)', False, None), ('email', 'VARCHAR(120)', False, None), ('image_file', 'VARCHAR(20)', False, None), ('hashed_password', 'VARCHAR(1024)', False, None), ('is_active', 'BOOLEAN', False, '1'), ('is_superuser', 'BOOLEAN', False, '0'), ('is_verified', 'BOOLEAN', False, '0')]
blog_post foreign keys: [{'name': 'fk_blog_post_user_id_blog_user', 'constrained_columns': ['user_id'], 'referred_schema': None, 'referred_table': 'blog_user', 'referred_columns': ['id'], 'options': {}}]
user_count: 7
post_count: 0
user_identity_rows: [(1, 'aaa@mail.ru', 'aaa'), (2, 'qqq@mail.ru', 'qqq@mail.ru'), (3, 'qa@example.com', 'qa_tester'), (4, 'adv_1789139086@example.com', 'adv_1789139086'), (5, 'phase01_user@example.com', 'phase01_user'), (6, 'phase02_user@example.com', 'phase02_user'), (7, 'qa_user2@example.com', 'qa_user2')]
hash_check: {'nonempty': 7, 'min_length': 60, 'max_length': 60, 'prefixes': ['$2b$']}
auth_defaults_rows: [(1, 1, 0, 0), (2, 1, 0, 0), (3, 1, 0, 0), (4, 1, 0, 0), (5, 1, 0, 0), (6, 1, 0, 0), (7, 1, 0, 0)]
alembic_version: a1c2d3e4f5a6
inspector/count/hash checkpoint: PASS

inspector/count/hash checkpoint exit=0
