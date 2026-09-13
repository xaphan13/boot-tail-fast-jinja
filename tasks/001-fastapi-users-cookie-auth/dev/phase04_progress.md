# Фаза 4 — прогресс

Дата: 2026-09-13

- План: добавить явную dependency `get_current_user` во все публичные рендерящие handlers в `routes_main.py` и `routes_articles.py`; сохранить `require_login` для защищённых handlers с контрактом `BlogUser`; не менять URL, registry/markdown, CSRF, auth logic или шаблоны.
- Ограничения: изменяются только `fastapi-application/md_articles/routes_main.py`, `fastapi-application/md_articles/routes_articles.py` и этот progress-файл; коммит не выполняется.
- Подготовка: прочитаны AGENTS.md, фаза 4 и контракты REQUIREMENTS.md, progress фаз 1–3, оба роутера, `web_utils.py`, релевантные шаблоны и `docs/11_md_articles.md`.
- Статус: подготовка завершена; до правок middleware current-user уже удалён, `render_template` получает `current_user` из state, который заполняется только dependency.
- 2026-09-13 — `fastapi-application/md_articles/routes_main.py`: добавлен `Depends` и явная dependency `get_current_user` в рендерящий handler `/about`; redirect handlers `/` и `/home` не требуют current-user context. Импорт: PASS (`routes_main import PASS 3`). Ruff для двух роутеров: PASS (`All checks passed!`).
- 2026-09-13 — `fastapi-application/md_articles/routes_articles.py`: публичные SSR handlers `/art_home`, `/art_section/{section}` и `/art/{author}/{art_id}` получили `Depends(get_current_user)`; защищённые `/art_manage`, `/art_manage/add_all`, `/art_manage/prune_missing`, `/art_manage/meta` используют единый `require_login` с типом `BlogUser`. Импорт обоих роутеров: PASS (`routers import PASS 3 7`). Ruff для двух роутеров: PASS (`All checks passed!`). Registry, markdown, URL, CSRF и response logic сохранены.

## Checkpoint

- 2026-09-13 — Smoke приложения без cookie: PASS. `GET /` → `303` на `/art_home`; `GET /art_home` → `200`; `GET /art_manage` → `303` на `/login?next=/art_manage`; traceback не наблюдался.
- 2026-09-13 — Финальный импорт обоих роутеров: PASS (`routers import PASS 3 7`); финальный `ruff check md_articles/routes_main.py md_articles/routes_articles.py`: PASS (`All checks passed!`).
- 2026-09-13 — Тестовый `uvicorn` остановлен после smoke; порт 8000 не отвечает (`curl` exit 7).

## Сырые выводы проверок

```text
$ ../.venv/bin/python -c "from md_articles.routes_main import router_main; from md_articles.routes_articles import router_articles; print('routers import PASS', len(router_main.routes), len(router_articles.routes))"
routers import PASS 3 7

$ ../.venv/bin/ruff check md_articles/routes_main.py md_articles/routes_articles.py
All checks passed!

$ for path in / /art_home /art_manage; do printf '%s ' "$path"; curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\\n' --max-time 5 "http://127.0.0.1:8000$path"; done
/ 303 http://127.0.0.1:8000/art_home
/art_home 200 
/art_manage 303 http://127.0.0.1:8000/login?next=/art_manage

$ curl -sS -m 2 -o /dev/null http://127.0.0.1:8000/openapi.json
curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: В соединении отказано
```

Статус фазы: готово; проблем не обнаружено.
