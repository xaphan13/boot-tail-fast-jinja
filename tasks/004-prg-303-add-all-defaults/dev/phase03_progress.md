# Phase 03 Progress — art_manage_add_all: fill empty fields

Дата: 2026-09-11
Файл фазы: `fastapi-application/md_articles/routes_articles.py`

## План правок

1. Добавить `from pathlib import Path` к импортам (после `import os`).
2. Добавить модульную константу `DEFAULT_AUTHOR = "NoName"` перед `router_articles = APIRouter(...)`.
3. Переписать тело `art_manage_add_all` под новый алгоритм.
4. В `art_manage_meta` (ветка создания новой записи): `os.path.splitext(file_name)[0]` → `Path(file_name).stem`.

`import os` оставлен: всё ещё нужен в `art_author` (`os.path.exists`).

## Что сделано

### Правки в `routes_articles.py`

1. Импорт:
   ```python
   from pathlib import Path
   ```
2. Константа (между импортами и роутером):
   ```python
   DEFAULT_AUTHOR = "NoName"
   ```
3. `art_manage_add_all` полностью переписан — цикл по `sorted(scan_content_art())` с тремя ветками:
   - `file_name not in registry_by_file` → создать `ArticleLang(...defaults)`, `added += 1`
   - есть пустое после `.strip()` поле → `model_copy(update=...)`, `filled += 1`
   - всё заполнено → `unchanged += 1`
   - в конце сохранить существующий flash «Нет новых файлов для добавления» для пустого `disk_files`,
     новый flash «Все записи уже полные» (info) для случая `added==0 and filled==0 and unchanged>0`,
     и стандартный flash «Добавлено: X, заполнено: Y, без изменений: Z» (success) иначе.
   - `articles` без файла на диске сохраняются в исходном порядке (через дополнительный цикл в конце).
4. `art_manage_meta`: `if not title: title = Path(file_name).stem`.

## Baseline (до правок)

`git diff fastapi-application/md_articles/articles.yaml` (HEAD → рабочий):

- Удалены все строки `section:` (формат реестра изменился — теперь `section` вычисляется из `file_name`).
- 8 записей SUPER/* (art_id 1789142345–1789142352) добавлены — кто-то прогонял `add_all` в фазе 2.
- art_id 1789142345: `author: '4'`, `lang: '4'`, `title: SUPER/05_ai_agent_guide` ← все непустые.
- art_id 1789142346–1789142352: `author: ''`, `lang: ''`, `title: SUPER/<stem>` ← нужно заполнить.

## Перезапуск uvicorn

Старый процесс (pid 388728, без `--reload`) убит.
Новый: `pid 391034`, `uvicorn main:main_app --host 127.0.0.1 --port 8000` из `fastapi-application/`.
Лог: `/tmp/uvicorn-phase03.log`.

## Checkpoint

### 1. ruff

```
$ uv run ruff check fastapi-application/md_articles/routes_articles.py
All checks passed!
```

### 2. len(main_app.routes)

```
43
```

### 3. git diff articles.yaml после первого POST add_all

```
 fastapi-application/md_articles/articles.yaml | 332 +++++++++++---------------
 1 file changed, 146 insertions(+), 186 deletions(-)
```

Главное содержание (7 заполненных записей):
```
- author: NoName
  lang: SUPER
  art_id: 1789142346
  title: SUPER/06_frontend_bootstrap_analysis
  file_name: SUPER/06_frontend_bootstrap_analysis.md
- author: NoName
  lang: SUPER
  art_id: 1789142347
  title: SUPER/06_frontend_report
  ...
- author: NoName
  lang: SUPER
  art_id: 1789142352
  title: SUPER/writing-posts
```

И запись art_id 1789142345 сохранена (непустые `author: '4'`, `lang: '4'` НЕ тронуты):
```
- author: '4'
  lang: '4'
  art_id: 1789142345
  title: SUPER/05_ai_agent_guide
  file_name: SUPER/05_ai_agent_guide.md
```

Также весь yaml пересобран в порядке `sorted(scan_content_art())` (по разделам и файлам),
поэтому diff показывает много «переездов» записей — это побочный эффект нового алгоритма.
Содержательно: 7 записей заполнены, 1 сохранена, 0 удалено, 0 добавлено.

### 4. /art_section/SUPER — ссылки на статьи

`grep "art_main.art_author"` дал 0 — FastAPI рендерит путь (`/art/{author}/{art_id}`),
а не endpoint-name. Считаю ссылки на сами статьи:

```
$ grep -oE 'href="http://127\.0\.0\.1:8000/art/[^"]+"' /tmp/super_section.html | wc -l
8
```

8 ссылок (по одной на запись art_id 1789142345–1789142352) — соответствует ожиданию.

### 5. POST add_all — flash

POST с правильным CSRF-токеном из `/art_manage`:

```
HTTP/1.1 303 See Other
location: /art_manage
set-cookie: session=...
```

Декодированная сессия:
```json
{"_flashes": [["success", "Добавлено: 0, заполнено: 7, без изменений: 81"]]}
```

- added=0 — все SUPER/* файлы уже были в реестре (добавлены в фазе 2).
- filled=7 — 7 записей с пустыми author/lang заполнены.
- unchanged=81 — все остальные 81 запись уже полные (включая art_id 1789142345 с `author: '4'`, `lang: '4'`).
  Итого: 7 + 81 = 88 записей в реестре.

### 6. Повторный POST add_all — flash «Все записи уже полные»

После первого POST все 8 записей SUPER/* теперь имеют заполненные поля.
Второй POST:

```json
{"_flashes": [["info", "Все записи уже полные"]]}
```

`added == 0 and filled == 0 and unchanged > 0` → ветка info сработала корректно.

## Чекпойнт-сводка

| # | Проверка | Результат |
|---|---|---|
| 1 | `ruff check routes_articles.py` | PASS (All checks passed!) |
| 2 | `len(main_app.routes)` | PASS (43) |
| 3 | articles.yaml: 7 SUPER/* заполнены (1789142346–1789142352) | PASS (author: NoName, lang: SUPER, title: stem) |
| 4 | /art_section/SUPER показывает 8 ссылок | PASS (8 ссылок `/art/{author}/{art_id}`) |
| 5 | flash «Добавлено: 0, заполнено: 7, без изменений: 81» | PASS (success) |
| 6 | Второй POST → flash «Все записи уже полные» | PASS (info) |

## Сервер

uvicorn оставлен работающим (pid 391034) — qa/adversary переиспользуют.
