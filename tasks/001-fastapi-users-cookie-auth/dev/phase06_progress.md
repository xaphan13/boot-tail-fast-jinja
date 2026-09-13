# Фаза 6 — прогресс

Дата: 2026-09-13

- План: минимально адаптировать auth-шаблоны под стандартный fastapi-users cookie login; сохранить register/CSRF и существующую logout-навигацию; проверить только разрешённые шаблоны и записать checkpoint без коммита.
- Ограничения: изменяются только `fastapi-application/templates/login.html`, `fastapi-application/templates/register.html`, `fastapi-application/templates/layout.html` и этот progress-файл. Python, static, partials, миграции и дизайн не изменяются.
- Подготовка: прочитаны AGENTS.md, REQUIREMENTS.md, progress фаз 1–5, `login.html`, `register.html`, `layout.html`, `routes_users.py`, `web_utils.py`, form macro и auth-навигация. В `routes_users.py` подтверждены `/logout` с redirect `/art_home` и cookie clearing helper; logout partials используют этот существующий route.
- 2026-09-13 — `fastapi-application/templates/login.html`: form action изменён на `/auth/cookie/login`, метод оставлен `POST`; email-поле формы переименовано в `username` при сохранении текущего контекста/разметки; добавлена только auth response handling для form-data fetch: успешный `204` ведёт обычной навигацией на `/art_home`, JWT/localStorage/Bearer не используются.
- 2026-09-13 — `fastapi-application/templates/register.html`: явный action `/register`, `POST`, текущие `username`, `email`, `password`, `confirm_password` и CSRF сохранены; остальная разметка/тексты не менялись.
- 2026-09-13 — `fastapi-application/templates/layout.html`: содержимое не менялось; logout-навигация остаётся существующей named route `/logout` в подключаемых auth partials, отдельный logout wrapper не добавлялся.

## Checkpoint

- Статический checkpoint: PASS.
- Jinja2 parse: `login.html`, `register.html`, `layout.html` — PASS.
- Auth contract scan: login action — PASS; username field — PASS; password field — PASS; `204` → `/art_home` — PASS; no JWT/localStorage/Bearer — PASS; register action — PASS; register fields — PASS; register CSRF — PASS; layout auth-free/unchanged — PASS.
- `git diff --check` для трёх шаблонов — PASS.
- Diff scope: изменены только `login.html` и `register.html` среди продуктовых файлов; `layout.html` не изменён по причине отсутствия auth-разметки для точечной правки. Создан только этот progress-файл.
- Smoke/curl: сервер на `127.0.0.1:8000` недоступен (`curl` exit 7, HTTP status `000`), поэтому auth-flow smoke не запускался согласно условию задания.
- Ruff не применялся: фаза меняет только Jinja2-шаблоны и progress-файл.
- Коммит не выполнялся.

## Сырые выводы проверок

```text
--- server ---
curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: В соединении отказано
status=000

--- template parse ---
login.html: parse PASS
register.html: parse PASS
layout.html: parse PASS

--- auth contract scan ---
login action: PASS
login username field: PASS
login password field: PASS
login 204 redirect: PASS
no JWT storage: PASS
register action: PASS
register fields: PASS
register csrf: PASS
layout unchanged auth-free: PASS

--- git diff check ---
[no output; exit 0]

--- git diff stat ---
 fastapi-application/templates/login.html    | 28 ++++++++++++++++++++++++++--
 fastapi-application/templates/register.html |  2 +-
 2 files changed, 27 insertions(+), 3 deletions(-)
```

Проблем: статический checkpoint пройден; runtime smoke невозможен, потому что сервер не запущен.
