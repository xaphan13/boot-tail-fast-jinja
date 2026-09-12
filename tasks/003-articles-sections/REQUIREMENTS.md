# Массовое наполнение реестра статей и навигация по разделам

Зона: блог `md_articles/` (Python) + шаблоны `templates/new_art/` и `templates/includes/`.
Пользователь кладёт .md-файлы статей в `fastapi-application/templates/content_art/`
по подпапкам; реестр `articles.yaml` должен отражать только реально существующие файлы,
кнопка «добавить все» в `/art_manage` должна разом регистрировать все найденные файлы
(рекурсивно), а левое меню (`includes/_sidebar.html`) должно показывать разделы —
подпапки `content_art/` — и вести на список статей раздела.

## Подтверждённые решения

- Раздел статьи = имя папки верхнего уровня в `content_art/` (например `AI инструменты`,
  `Fast API`, `Sql Alchemy`). Имя папки = имя раздела. Раздел не хранится отдельным
  полем реестра, а выводится из `file_name` (единый источник истины — путь файла).
- Задача выполняется в yolo-режиме: открытые вопросы оркестратору закрывать не нужно,
  спорные развилки зафиксированы ниже как решения.

## Результат

После задания:

1. `md_articles/schema_art.py`:
   - `scan_content_art()` возвращает **рекурсивно** найденные `.md`/`.markdown` файлы
     относительно `content_art/` в POSIX-виде (`AI инструменты/aion-zcode-1.md`),
     отсортированные. Верхнеуровневые `.gitkeep` и прочие не-`.md` файлы игнорируются.
   - существует функция `get_section(file_name: str) -> str` — имя папки верхнего уровня
     для пути (`"AI инструменты/a.md"` → `"AI инструменты"`, `"a.md"` → `""`).
   - существует функция `list_sections() -> list[str]` — отсортированный список
     непустых имён разделов, выведенных из зарегистрированных (в `articles.yaml`)
     статей. Пустые папки в сайдбар не попадают.
2. `md_articles/routes_articles.py`:
   - `POST /art_manage/add_all` (имя `art_main.art_manage_add_all`) регистрирует все
     нераспределённые файлы из рекурсивного скана; `title` = stem файла,
     `author` = `""`, `lang` = `""` (как сейчас, без выдумывания значений).
   - Новая ручка `POST /art_manage/prune_missing`
     (имя `art_main.art_manage_prune_missing`) удаляет из `articles.yaml` все записи,
     чей `file_name` не найден в рекурсивном скане, и сохраняет реестр.
     CSRF-проверка обязательна. После работы — flash + redirect на `/art_manage`.
   - Новая ручка `GET /art_section/{section}` (имя `art_main.art_section`) рендерит
     `new_art/art_home.html` со списком статей, у которых `get_section(file_name) == section`.
     Неизвестный раздел (`section` вне `list_sections()`) → 404.
   - `/art_manage` (GET) использует рекурсивный скан: `unassigned_files` показывает все
     незарегистрированные файлы, `missing_entries` — все зарегистрированные записи без файла.
3. `md_articles/web_utils.py`:
   - `_inject_globals()` добавляет в контекст каждого шаблона переменную
     `sidebar_sections: list[str]` (из `schema_art.list_sections()`), чтобы
     `layout.html`-сайдбар работал на всех страницах блога.
4. `templates/includes/_sidebar.html`:
   - статический список ссылок-заглушек (`href="#"`) заменён на
     `{% for section in sidebar_sections %}` → `url_for('art_main.art_section', section=section)`.
5. `templates/new_art/art_manage.html`:
   - в секции «Записи без файла» появляется форма-кнопка «Удалить записи б��з файла»
     (POST на `art_main.art_manage_prune_missing` с `csrf_token`).
6. `templates/new_art/art_home.html`:
   - при рендере из `art_section` отображается заголовок с именем раздела
     (переменная `section`); на `/art_home` заголовок остаётся как сейчас.

## Вне рамок

- Изменение поведения `/art/{author}/{art_id}` (single article) — не трогаем.
- Автозаполнение `author`/`lang` из имени файла или содержимого статьи.
- Миграция реестра со сменой схемы (поле `section` в YAML удаляется неявно, т.к.
  `_FIELDS_FOR_YAML` его не сохраняет; специальной миграции не требуется).
- Написание тестов (в проекте нет тест-инфраструктуры).
- Правка `AGENTS.md`/`QWEN.md` (счётчик маршрутов там обновляет оркестратор, не эта задача).

## План фаз

Единица исполнения — фаза: одно делегирование, 1–2 файла, бюджет ~10–15 ходов.
Следующая фаза стартует только после зелёного checkpoint и ревью диффа оркестратором.
Прогресс фазы фиксируется в `tasks/current/dev/phaseNN_progress.md`.

| # | Фаза | Исполнитель | Файлы | Контракт | Checkpoint | Бюджет ходов |
|---|---|---|---|---|---|---|
| 1 | Рекурсивный скан и хелперы раздела | backend-dev | `md_articles/schema_art.py` | `scan_content_art() -> list[str]` (рекурсивно, POSIX-путь), `get_section(str) -> str`, `list_sections() -> list[str]` | `python -c` со счётчиком файлов и печатью разделов | ~10 |
| 2 | Роуты: add_all, prune, section | backend-dev | `md_articles/routes_articles.py` | `/art_manage/add_all` (существует), `/art_manage/prune_missing` (новый POST), `/art_section/{section}` (новый GET) | `python -c` с перечнем path'ов и счётчиком route-объектов (baseline+2) | ~12 |
| 3 | Глобальный контекст сайдбара | backend-dev | `md_articles/web_utils.py` | `_inject_globals()` отдаёт `sidebar_sections: list[str]` | ruff + импорт модуля | ~6 |
| 4 | Сайдбар и кнопка prune в шаблонах | frontend-dev | `templates/includes/_sidebar.html`, `templates/new_art/art_manage.html`, `templates/new_art/art_home.html` | имена роутов `art_main.art_section`, `art_main.art_manage_prune_missing`; переменная контекста `sidebar_sections`; переменная `section` в art_home | curl `/about` содержит ссылки `art_section/...`; `/art_manage` содержит форму prune | ~10 |

### Фаза 1: Рекурсивный скан и хелперы раздела

- Файлы: `fastapi-application/md_articles/schema_art.py`
- Контракт:
  - `def scan_content_art() -> list[str]`: обход `get_path_dir()` через `rglob("*")`,
    фильтр `is_file()` и суффиксов `.md`/`.markdown` (case-insensitive), результат —
    `entry.relative_to(content_dir).as_posix()`, отсортированный `sorted()`. Каталог
    отсутствует → `[]`. `.gitkeep` и не-`.md` отбрасываются.
  - `def get_section(file_name: str) -> str`: `Path(file_name).parts[0]`, если
    `len(parts) >= 2`, иначе `""`. Не использовать `Path.parent.name` (даёт `""`/`"."`
    для корня); опираться на `parts`.
  - `def list_sections() -> list[str]`: `sorted({get_section(a.file_name) for a in get_articles() if get_section(a.file_name)})`.
  - `ArticleLang` **не расширять** полем `section`.
  - `_FIELDS_FOR_YAML` и `save_articles` не менять (поле `section` в yaml будет
    отброшено при следующем сохранении — это ожидаемо).
- Шаги:
  1. Заменить тело `scan_content_art` на рекурсивный обход.
  2. Добавить `get_section` и `list_sections` рядом.
  3. Прогнать checkpoint, зафиксировать сырой вывод в `tasks/current/dev/phase01_scan.txt`.
- Checkpoint:
  ```bash
  cd fastapi-application && uv run ruff check md_articles/schema_art.py \
    && ../.venv/bin/python -c "from md_articles.schema_art import scan_content_art, get_section, list_sections; f=scan_content_art(); print('files:', len(f)); print('first:', f[0] if f else 'EMPTY'); print('section:', get_section(f[0]) if f else ''); print('sections:', list_sections())"
  ```
  Ожидается: `files: >= 75`, `first:` содержит `/`, `section:` — имя папки (одно из
  `AI инструменты`, `Fast API`, `Guide FastAPI`, `Guide MCP Python`, `Guide my fastApi`,
  `Jinja Templates`, `Pydantic Python`, `Python`, `Rust`, `Sql Alchemy`),
  `sections:` — список из 10 имён.
- Готовность фазы: ruff чист, checkpoint напечатал ≥75 файлов и 10 разделов,
  сырой вывод сохранён в `tasks/current/dev/`.

### Фаза 2: Роуты: add_all, prune, section

- Файлы: `fastapi-application/md_articles/routes_articles.py`
- Контракт:
  - Импорт из `md_articles.schema_art`: добавить `get_section`, `list_sections`.
  - `POST /art_manage/add_all` (имя `art_main.art_manage_add_all` — без изменений):
    `disk_files = set(scan_content_art())`, `new_files = sorted(disk_files - registered_files)`,
    `title = Path(file_name).stem`, `author=""`, `lang=""`, `save_articles(articles)`,
    flash + 307 на `/art_manage`. Если новых нет — flash info и 307.
  - `POST /art_manage/prune_missing` (имя `art_main.art_manage_prune_missing`):
    `await validate_csrf(request)`; `_user=Depends(require_login)`;
    `disk_files = set(scan_content_art())`; `kept = [a for a in get_articles() if a.file_name in disk_files]`;
    `removed = len(get_articles()) - len(kept)`; если `removed > 0` — `save_articles(kept)`,
    flash success `Удалено записей: N`; иначе flash info `Записей без файла нет`;
    redirect 307 на `/art_manage`.
  - `GET /art_section/{section}` (имя `art_main.art_section`): `section: str` в пути.
    Если `section not in list_sections()` → `raise HTTPException(404)`.
    Иначе `title_list = [art.model_dump(exclude={"content"}) for art in get_articles() if _is_complete(art) and get_section(art.file_name) == section]`,
    `render_template("new_art/art_home.html", {"request": request, "title_list": title_list, "section": section})`.
  - `/art_manage` (GET): `disk_files = set(scan_content_art())`; `unassigned_files` — все
    незарегистрированные файлы (уже так); `missing_entries` — записи, чей `file_name`
    не в `disk_files` (уже так); двойной вызов `scan_content_art()` убрать — один раз.
  - Порядок объявления роутов: `art_author` (`/art/{author}/{art_id}`) не должен
    перехватывать `/art_section/...` — FastAPI сопоставляет по объявлению, но
    `/art_section/...` имеет два сегмента после `/`, `/art/{author}/{art_id}` тоже;
    `art_section` обязан быть объявлен **выше** `art_author` в модуле.
- Шаги:
  1. Добавить импорты `get_section`, `list_sections`.
  2. Вставить `art_section` **до** `art_author`.
  3. Добавить `art_manage_prune_missing` рядом с `art_manage_add_all`.
  4. Убедиться, что `art_manage_add_all` работает с рекурсивным сканом (изменений
     в теле почти не требуется — полагается на новый `scan_content_art`).
  5. Убрать двойной вызов `scan_content_art()` в `art_manage`.
- Checkpoint (baseline снять ДО правок, `BASELINE=$(...)`):
  ```bash
  cd fastapi-application && \
    BASE=$(../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))") && \
    ../.venv/bin/python -c "from main import main_app; rs=[r.path for r in main_app.routes]; print('count:', len(rs)); print('prune:', '/art_manage/prune_missing' in rs); print('section:', '/art_section/{section}' in rs)" && \
    echo "expected delta: $((BASE)) -> $((BASE+2))"
  ```
  Ожидается: `count` = baseline+2, `prune: True`, `section: True`. Не полагаться на
  зафиксированные в AGENTS.md/QWEN.md «41»/«42» — брать фактический baseline.
- Готовность фазы: ruff по файлу чист, обе новые ручки видны в `main_app.routes`,
  счётчик вырос ровно на 2.

### Фаза 3: Глобальный контекст сайдбара

- Файлы: `fastapi-application/md_articles/web_utils.py`
- Контракт:
  - Импорт: `from md_articles.schema_art import list_sections`.
  - `_inject_globals(request)` возвращает словарь, в который добавлен ключ
    `"sidebar_sections": list_sections()`. Остальные ключи (`current_user`,
    `csrf_token`, `get_flashed_messages`) — без изменений.
- Шаги:
  1. Добавить импорт.
  2. Дописать ключ в возвращаемый словарь.
- Checkpoint:
  ```bash
  cd fastapi-application && uv run ruff check md_articles/web_utils.py \
    && ../.venv/bin/python -c "import md_articles.web_utils; print('ok')"
  ```
  Ожидается: `ok`.
- Готовность фазы: ruff чист, импорт без ошибок, проверка цепочки
  `web_utils -> schema_art` не даёт циклического импорта (при запуске `main` приложение
  поднимается без ошибок — увидит следующая фаза).

### Фаза 4: Сайдбар и кнопка prune в шаблонах

- Файлы:
  - `fastapi-application/templates/includes/_sidebar.html`
  - `fastapi-application/templates/new_art/art_manage.html`
  - `fastapi-application/templates/new_art/art_home.html`
- Контракт:
  - Сайдбар: заменить статический `<ul>` на
    `{% for section in sidebar_sections %}<li><a href="{{ url_for('art_main.art_section', section=section) }}" class="side-link">{{ section }}</a></li>{% else %}<li class="text-muted text-xs">Разделов нет</li>{% endfor %}`.
    Сохранить обёртку `<nav class="pt-1 w-full">` и подпись «Разделы».
  - `art_manage.html`: в секции «Записи без файла» (там, где `{% if missing_entries %}`)
    добавить над списком форму:
    `<form method="POST" action="{{ url_for('art_main.art_manage_prune_missing') }}"><input type="hidden" name="csrf_token" value="{{ csrf_token }}"><button type="submit" class="btn-grad ...">Удалить записи без файла</button></form>`.
    Кнопка «Добавить все» в секции «Нераспределённые файлы» остаётся без изменений.
  - `art_home.html`: перед списком статей — если `section` определён,
    `<h1 class="text-2xl font-bold text-heading mb-6">Раздел: {{ section }}</h1>`,
    иначе текущий `<h1>Статьи</h1>`.
- Шаги:
  1. Правки в `_sidebar.html`.
  2. Правки в `art_manage.html`.
  3. Правки в `art_home.html`.
  4. Поднять сервер (если не поднят) и снять сырой HTML в `tasks/current/dev/phase04_curl.txt`.
- Checkpoint:
  ```bash
  (pgrep -f "uvicorn.*main:main_app" >/dev/null || (cd fastapi-application && nohup ../.venv/bin/uvicorn main:main_app --port 8000 >/tmp/uv_phase4.log 2>&1 &)) ; sleep 3 ; \
    echo "about:" && curl -s http://127.0.0.1:8000/about | grep -c 'art_section' ; \
    echo "art_home:" && curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/art_home ; \
    echo "section:" && curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000/art_section/Python" ; \
    echo "bad-section:" && curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000/art_section/NoSuchSection"
  ```
  Ожидается: `about:` ≥ 10, `art_home:` 200, `section:` 200, `bad-section:` 404.
  (Проверка `/art_manage` и формы prune требует логина — их закрывает qa через
  регистрацию/логин в критериях успеха.)
- Готовность фазы: сайдбар рендерит ссылки разделов, `/art_section/Python` отдаёт 200,
  несуществующий раздел — 404, `/art_home` не сломан.

## Критерии успеха

Проверяются qa по завершении всех фаз; сырые выводы — в `tasks/current/e2e/`.
Сервер запускается из `fastapi-application/`, `BASELINE` — фактический счётчик
`len(main_app.routes)` до старта проверок (не 41 и не 42).

| # | Критерий | Проверка | Ожидание |
|---|---|---|---|
| 1 | Рекурсивный скан находит все .md | `python -c "from md_articles.schema_art import scan_content_art; f=scan_content_art(); print(len(f)); print(all('/' in x for x in f))"` | счётчик ≥ 75, `all` = True |
| 2 | Раздел выводится из пути | `python -c "from md_articles.schema_art import get_section; print(get_section('AI инструменты/a.md')); print(repr(get_section('a.md')))"` | `AI инструменты` и `''` |
| 3 | Список разделов содержит 10 папок | `python -c "from md_articles.schema_art import list_sections; print(list_sections())"` | 10 имён из content_art |
| 4 | Счётчик route-объектов вырос на 2 | `python -c "from main import main_app; print(len(main_app.routes))"` | BASELINE + 2 |
| 5 | `/about` рендерит сайдбар с ссылками разделов | `curl -s http://127.0.0.1:8000/about \| grep -c 'art_section'` | ≥ 10 |
| 6 | `/art_section/Python` отдаёт 200 и статьи раздела | `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/art_section/Python` и `curl -s http://127.0.0.1:8000/art_section/Python \| grep -c '01_project_structure'` | 200 и ≥ 1 |
| 7 | Неизвестный раздел → 404 | `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/art_section/NoSuchSection` | 404 |
| 8 | POST `/art_manage/add_all` без логина → редирект на /login | `curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/art_manage/add_all` | 307 |
| 9 | POST `/art_manage/prune_missing` без логина → редирект на /login | `curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/art_manage/prune_missing` | 307 |
| 10 | `articles.yaml` после prune не ссылается на отсутствующие файлы | через админ-сессию: POST `/art_manage/prune_missing` с CSRF, затем `python -c "from md_articles.schema_art import get_articles, scan_content_art; d=set(scan_content_art()); print([a.file_name for a in get_articles() if a.file_name not in d])"` | пустой список |
| 11 | Регресс: `/art_home`, `/docs`, `/users/get_all_users`, `/orders/get_all_orders`, `/api/v1/dep_examples/single-direct-dependency` | пять curl | все 200 |
| 12 | Ruff чист по изменённым файлам | `uv run ruff check md_articles/schema_art.py md_articles/routes_articles.py md_articles/web_utils.py` | без ошибок |

## Финальные критерии

1. Каждый критерий успеха подтверждён доказательством (e2e/, DEFECTS.md,
   ADVERSARIAL_REVIEW.md).
2. `tasks/current/DEFECTS.md` существует только если найдены дефекты; все записи
   не OPEN.
3. Adversarial-прогон выполнен, ни одна запись ADVERSARIAL_REVIEW.md не PENDING.

## Открытые вопросы

Решены в самой спеке (yolo-режим, вопросов пользователю не задавать):

- Нужна ли отдельная кнопка «удалить записи без файла», или `/art_manage/add_all`
  должен чистить реестр сам? Решение: отдельная кнопка и отдельный POST-роут
  `art_manage_prune_missing` — сайд-эффект удаления не совмещается с добавлением.
- Хранить ли `section` отдельным полем реестра? Решение: не хранить, выводить из
  `file_name` (единый источник истины). Существующие строки `section:` в YAML
  исчезнут при ближайшем `save_articles` — это ожидаемо.
- Показывать ли в сайдбаре разделы-папки без зарегистрированных статей? Решение:
  нет — `list_sections()` строится по зарегистрированным статьям.
- Обновлять ли счётчики маршрутов в `AGENTS.md`/`QWEN.md`? Решение: правку в
  `AGENTS.md`/`QWEN.md` делает оркестратор, не эта задача.

---

# Отчёт о выполнении

- Дата закрытия: 2026-09-11
- Коммит: не коммитилось (изменения остаются в рабочем дереве)

Рекурсивный скан `content_art/`, вывод раздела из пути (`get_section`/`list_sections`),
ручки `GET /art_section/{section}` и `POST /art_manage/prune_missing`, `sidebar_sections`
в глобальном контексте, сайдбар разделов и форма prune в шаблонах — реализовано.
Все 12 критериев успеха PASS (сырые выводы — `e2e/run-notes.md`), ruff по изменённым
файлам чист. Adversary-прогон выполнен, все три записи REJECTED (`ADVERSARIAL_REVIEW.md`),
принятых находок нет; `DEFECTS.md` не создавался — дефектов нет.