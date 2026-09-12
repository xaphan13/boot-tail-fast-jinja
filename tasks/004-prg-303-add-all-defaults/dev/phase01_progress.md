# Phase 01 progress

- Date: 2026-09-11
- File: `fastapi-application/md_articles/routes_articles.py`
- Branch: `tailwind_jinja`

## Изменения

1. Удалён декоратор `@router_articles.post("/art_home", name="art_main.art_home")` — бывшая строка 36.
   GET-декоратор `@router_articles.get("/art_home", name="art_main.art_home")` сохранён, имя маршрута `art_main.art_home` не изменилось.
2. Все 5 `RedirectResponse(..., status_code=307)` → `status_code=303` (POST-ручки блога:
   `art_manage_add_all`, `art_manage_prune_missing`, `art_manage_meta` — редиректы на ветках ошибки
   и успеха).

## Checkpoint выводы

### 1. `grep -n "status_code=307" .../routes_articles.py` → пусто
```
$ grep -n "status_code=307" .../routes_articles.py
(пусто)
```
PASS.

### 2. `grep -n "@router_articles.post" .../routes_articles.py` → 3 строки (`/art_home` отсутствует)
```
143:@router_articles.post("/art_manage/add_all", name="art_main.art_manage_add_all")
175:@router_articles.post("/art_manage/prune_missing", name="art_main.art_manage_prune_missing")
194:@router_articles.post("/art_manage/meta", name="art_main.art_manage_meta")
```
PASS. `/art_home` отсутствует — POST-декоратор удалён, остался только GET.

### 3. `ruff check .../md_articles/routes_articles.py`
```
$ cd fastapi-application && ../.venv/bin/ruff check md_articles/routes_articles.py
All checks passed!
```
PASS.

### 4. `python -c "from main import main_app; print(len(main_app.routes))"` → **43** (НЕ 40)
```
$ ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"
43
```
**DIVERGENCE от спеки (ожидалось 40).** Причина: проект не на чистом HEAD — в рабочей копии
остались некоммиченные изменения предыдущих заданий (002/003), которые добавили:
- `/art_section/{section}` (GET) — task 003
- `/art_manage/prune_missing` (POST) — task 003

Контрольное измерение чистого HEAD (через `git stash`):
```
$ git stash && python -c "from main import main_app; print(len(main_app.routes))"
42
```
HEAD содержит 42 маршрута, что на 1 больше, чем заявленные в `QWEN.md` 41
(видимо, из-за ранее закоммиченных изменений, не описанных в документации).
Мои правки корректны: единственный удалённый маршрут — POST `/art_home`. Итоговая формула:
HEAD (42) + 2 добавленных task 003 (`art_section`, `art_manage/prune_missing`) − 1 мой (POST /art_home) = **43**.

Маршруты из `routes_articles.py` после правки (7 штук):
```
/art_home                  GET    art_main.art_home
/art_section/{section}     GET    art_main.art_section
/art/{author}/{art_id}     GET    art_main.art_author
/art_manage                GET    art_main.art_manage
/art_manage/add_all        POST   art_main.art_manage_add_all
/art_manage/prune_missing  POST   art_main.art_manage_prune_missing
/art_manage/meta           POST   art_main.art_manage_meta
```

Оркестратору на заметку: в финальном отчёте задания счётчик маршрутов надо указывать
как 43 (а не 40), иначе он не сойдётся с фактическим состоянием проекта.

### 5. uvicorn
```
$ cd fastapi-application && nohup ../.venv/bin/uvicorn main:main_app --host 127.0.0.1 --port 8000 > /tmp/uvicorn_phase01.log 2>&1 &
uvicorn pid: 386914
ready after 2
```
Сервер поднят и НЕ гасится в конце фазы — его переиспользуют qa/adversary.

### 6. Логин (register → login)
Зарегистрирован `phase01_user@example.com` / `Pass1234`:
```
register=307 loc=http://127.0.0.1:8000/login
login=307 loc=http://127.0.0.1:8000/art_home
```
Регистрация и логин ещё возвращают **307** — это нормально: правка `routes_users.py`
отнесена к фазе 2.

### 7. `POST /art_manage/add_all` → 303 + Location: /art_manage
```
$ curl -i -X POST -b /tmp/cookies.txt -c /tmp/cookies.txt \
    -d "csrf_token=$CSRF_ART" http://127.0.0.1:8000/art_manage/add_all
HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:32:59 GMT
server: uvicorn
content-length: 0
location: /art_manage
set-cookie: session=...
```
PASS. Браузер после POST сделает GET на `/art_manage` — PRG инвариант восстановлен.

## Замечания оркестратору

- Чекпойнт 4 (route count) расходится со спекой: фактически **43**, не 40.
  Корневая причина — некоммиченные правки task 002/003 в рабочей копии
  (`/art_section/{section}`, `/art_manage/prune_missing`). Мои изменения
  корректны и точечно соответствуют фазе 1.
- Сервер uvicorn оставлен работать на порту 8000 для qa/adversary.
- Cookies сохранены в `/tmp/cookies.txt` от залогиненной сессии `phase01_user`.
