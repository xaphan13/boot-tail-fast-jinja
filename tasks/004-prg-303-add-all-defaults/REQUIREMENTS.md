# POST/Redirect/Get в блоге и дефолты add_all на /art_manage

Кнопки «Добавить все» и «OK» на `/art_manage` в браузере дают 405 — POST-ручки блога
отвечают `RedirectResponse(..., status_code=307)`, который сохраняет метод: браузер
повторяет POST на GET-only `/art_manage`. Параллельно `art_manage_add_all` создаёт
записи с пустыми `author`/`lang`/`title`, поэтому даже после исправления редиректа
статьи не видны ни на `/art_home`, ни на `/art_section/<раздел>` — их `_is_complete()`
возвращает `False`.

## Подтверждённые решения

- **303 для всех редиректов блога.** Любая `RedirectResponse` в `md_articles/` —
  и в POST-ручках, и в `require_login`, и в `home` — переводится на
  `status_code=303` (See Other). Это Post/Redirect/Get по RFC 7231: браузер после
  POST делает GET независимо от исходного метода. curl редиректы не следует, поэтому
  qa должна явно проверять `curl -o /dev/null -w "%{http_code} %{redirect_url}\n"`.
- **Костыль `@router_articles.post("/art_home")` удаляется.** Дубль маршрута
  существовал только потому, что 307 + POST повторно на `/art_home` работал; после
  перехода на 303 дубль не нужен. `/art_home` остаётся GET-only.
- **Дефолты add_all по конвенции реестра.** Для каждого файла из `content_art/`:
  `author = "NoName"`, `lang = get_section(file_name)` (имя папки или `""` для
  файлов в корне), `title = Path(file_name).stem` (голое имя файла без папки и
  последнего расширения). Не выдумывать значения из содержимого `.md`.
- **add_all дополняет, а не пересоздаёт.** `art_manage_add_all` в одном проходе
  делает три вещи: (а) добавляет новые записи с дефолтами; (б) для уже
  зарегистрированных записей с пустым `author` или пустым `lang` или пустым
  `title` заполняет поле из дефолта (не трогает непустые — пользовательские
  значения сохраняются); (в) полностью заполненные записи пропускает.
  Сообщение во flash: `"Добавлено: X, заполнено: Y, без изменений: Z"`.
  Это автоматически чинит 7 неполных `SUPER/*` записей одним нажатием «Добавить
  все» — отдельная ручка/кнопка не нужна.
- **art_manage_meta: дефолт title тоже `Path(file_name).stem`.** Текущий код
  использует `os.path.splitext(file_name)[0]`, что оставляет папку в title
  (например, `SUPER/file`). Меняем на `Path(file_name).stem` для согласованности
  с реестром и add_all. Поведение «title из формы перекрывает дефолт»
  сохраняется.
- **save_articles поле `section` не трогать.** В `ArticleLang` его нет, в
  `_FIELDS_FOR_YAML` оно не входит — это уже принятое решение предыдущих заданий,
  вне рамок.

## Результат

- Все POST-ручки блога (`art_manage_add_all`, `art_manage_prune_missing`,
  `art_manage_meta`, `register_post`, `login_post`, `account_post`) и
  `require_login` отвечают 303 на редиректы после успеха/ошибки.
- `@router_articles.post("/art_home")` удалён; `/art_home` — только GET.
- `art_manage_add_all` создаёт записи с дефолтами `("NoName", get_section, stem)`
  и дополняет пустые поля у уже зарегистрированных записей.
- `art_manage_meta` при пустом title в форме подставляет `Path(file_name).stem`.
- `/art_section/<раздел>` после `add_all` показывает все статьи раздела, чьи
  записи в реестре заполнены.

## Вне рамок

- Известные дефекты из `docs/04_code_quality.md` (500 на `depends_function_annotated`,
  `IntegrityError` при дубликате nickname, `password` в `UserResp`,
  `TestUser` не в миграциях) — не трогать.
- Дублирование обработчиков в `api/` — намеренное.
- Поле `section` в `ArticleLang` / `articles.yaml` — не вводить.
- Документация `docs/11_md_articles.md` — обновление счётчика маршрутов
  (15 → 14 blog objects) делает оркестратор после закрытия задания.
- Парсинг содержимого `.md` для извлечения метаданных — запрещён.
- Изменения в `articles.yaml` не коммитим как часть задания: правки только в коде,
  yaml обновляется тестовым прогоном.

## План фаз

Единица исполнения — фаза: одно делегирование, 1–3 файла, бюджет ~10–15 ходов.
Следующая фаза стартует только после зелёного checkpoint и ревью диффа оркестратором.
Прогресс фазы разработчик фиксирует в `tasks/current/dev/phaseNN_progress.md`.

| # | Фаза | Исполнитель | Файлы | Контракт | Checkpoint | Бюджет ходов |
|---|---|---|---|---|---|---|
| 1 | POST→303 в routes_articles.py + снятие костыля /art_home | backend-dev | `md_articles/routes_articles.py` | 5 POST-редиректов 307→303; удалён `@router_articles.post("/art_home")`; route count `len(main_app.routes) == 40` | `python -c "from main import main_app; print(len(main_app.routes))"` → 40; `ruff check fastapi-application/md_articles/routes_articles.py` → 0; `curl -i -X POST -b cookies.txt -d "csrf_token=..." http://127.0.0.1:8000/art_manage/add_all` → `HTTP/1.1 303 See Other`, `Location: /art_manage` | ~10 |
| 2 | POST→303 в routes_users.py + web_utils.py + routes_main.py | backend-dev | `md_articles/routes_users.py`, `md_articles/web_utils.py`, `md_articles/routes_main.py` | 8 редиректов 307→303; `grep -n "status_code=307" md_articles/routes_users.py md_articles/web_utils.py md_articles/routes_main.py` → пусто | `python -c "from main import main_app; print(len(main_app.routes))"` → 40; `ruff check ...` по трём файлам → 0; `grep -rn "status_code=307" md_articles/routes_users.py md_articles/web_utils.py md_articles/routes_main.py` → без вывода | ~12 |
| 3 | Дефолты add_all + meta: title из `Path(...).stem` | backend-dev | `md_articles/routes_articles.py` | `from pathlib import Path` импортирован; `art_manage_add_all` добавляет новые записи с `author="NoName"`, `lang=get_section(file_name)`, `title=Path(file_name).stem`; для уже зарегистрированных записей пустые поля заполняются теми же дефолтами; flash `"Добавлено: X, заполнено: Y, без изменений: Z"`; `art_manage_meta` использует `Path(file_name).stem` вместо `os.path.splitext(file_name)[0]` | `ruff check ...` → 0; сценарий qa в e2e: после POST add_all все 8 записей `SUPER/*` имеют `author="NoName"`, `lang="SUPER"`, `title=<stem без папки>`; `curl /art_section/SUPER` → 200 и в HTML видны все 8 заголовков | ~12 |

### Фаза 1: POST→303 в routes_articles.py + снятие костыля /art_home

- Файлы: `fastapi-application/md_articles/routes_articles.py` (1 файл).
- Контракт (фиксируется для фаз 2 и 3):
  - Все `RedirectResponse(..., status_code=307)` в POST-ручках этого файла
    становятся `status_code=303`.
  - Декоратор `@router_articles.post("/art_home", name="art_main.art_home")`
    удаляется; GET-декоратор остаётся, имя маршрута `art_main.art_home` сохраняется.
  - Счётчик маршрутов `len(main_app.routes)` уменьшается с 41 до 40.
- Шаги:
  1. Прочитать `routes_articles.py` целиком, найти все `status_code=307` (5 штук в
     POST-ручках) и декоратор `post("/art_home")`.
  2. Пять точечных правок: `status_code=307` → `status_code=303` в строках 155,
     170, 189, 217, 243 (нумерация приблизительная — ориентироваться на
     `grep -n "status_code=307"` внутри файла).
  3. Удалить строку декоратора `@router_articles.post("/art_home", name="art_main.art_home")`.
  4. `ruff check fastapi-application/md_articles/routes_articles.py` — должно быть
     чисто.
  5. Поднять uvicorn (`cd fastapi-application && ../.venv/bin/uvicorn main:main_app --port 8000`),
     залогиниться через сессию (любым удобным способом — `register`/`login`),
     CSRF-токен взять со страницы `/art_manage` из cookie+form.
  6. `curl -i -X POST -b cookies.txt -c cookies.txt -d "csrf_token=<token>" http://127.0.0.1:8000/art_manage/add_all`
     — ожидаем `HTTP/1.1 303 See Other` и `Location: /art_manage`.
  7. `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"`
     — ожидаем 40.
- Checkpoint:
  - `python -c "from main import main_app; print(len(main_app.routes))"` → `40`.
  - `ruff check fastapi-application/md_articles/routes_articles.py` → `All checks passed!`.
  - `grep -n "status_code=307" fastapi-application/md_articles/routes_articles.py` → пусто.
  - `grep -n "@router_articles.post" fastapi-application/md_articles/routes_articles.py` → одна строка (`/art_manage/add_all`), `/art_home` отсутствует.
  - `curl -i -X POST .../art_manage/add_all` → `303` + `Location: /art_manage`.
- Готовность фазы: чек-лист пройден, прогресс записан в
  `tasks/current/dev/phase01_progress.md`.

### Фаза 2: POST→303 в routes_users.py + web_utils.py + routes_main.py

- Файлы: `fastapi-application/md_articles/routes_users.py`,
  `fastapi-application/md_articles/web_utils.py`,
  `fastapi-application/md_articles/routes_main.py` (3 файла).
- Контракт:
  - В `routes_users.py`: 6 редиректов в POST-ручках
    (`register_post`×2, `login_post`×3, `account_post`×1) и 2 редиректа в
    GET-ручках (`register_get`, `login_get`, `logout`) переводятся на 303.
    Решение по GET-ручкам принимается в этой фазе: 303 семантически верен
    («See Other» применим к любому методу), 307 в GET-only местах не ломает
    браузер, но для согласованности с остальной кодовой базой переводим всё
    на 303.
  - В `web_utils.py`: единственный `RedirectResponse(..., status_code=307)`
    в `require_login` → 303. `HTTPException(status_code=307, ...)` рядом —
    только синхронизация статуса исключения (на практике FastAPI всё равно
    редиректит по заголовку `location`, но единый код чище).
  - В `routes_main.py`: единственный `RedirectResponse(..., status_code=307)`
    в `home` → 303. Это GET-only редирект, но меняем для единообразия.
- Шаги:
  1. `grep -n "status_code=307" fastapi-application/md_articles/routes_users.py
     fastapi-application/md_articles/web_utils.py
     fastapi-application/md_articles/routes_main.py` — составить список строк.
  2. По каждой строке точечная правка `307` → `303`. Для
     `web_utils.require_login` — оба места (RedirectResponse и HTTPException).
  3. `ruff check` по трём файлам — чисто.
  4. Поднять uvicorn, прогнать:
     - `POST /register` (валидная форма) → `303 See Other` + `Location: /login`.
     - `POST /login` (валидная форма) → `303 See Other` + `Location: /art_home`.
     - `POST /account` (валидная форма) → `303 See Other` + `Location: /account`.
     - `POST /art_manage/add_all` без сессии → `303` + `Location: /login?next=...`
       (через `require_login` guard).
     - `GET /` → `303 See Other` + `Location: /art_home`.
- Checkpoint:
  - `grep -rn "status_code=307" fastapi-application/md_articles/routes_users.py
     fastapi-application/md_articles/web_utils.py
     fastapi-application/md_articles/routes_main.py` → пусто.
  - `ruff check` по трём файлам → 0.
  - `python -c "from main import main_app; print(len(main_app.routes))"` → `40`
    (не изменилось — POST-декораторы остались на месте).
  - Все пять curl-сценариев выше возвращают 303.
- Готовность фазы: чек-лист пройден, прогресс записан в
  `tasks/current/dev/phase02_progress.md`.

### Фаза 3: Дефолты add_all + meta: title из `Path(...).stem`

- Файлы: `fastapi-application/md_articles/routes_articles.py` (1 файл).
- Контракт:
  - Импорт `from pathlib import Path` добавлен к существующим импортам (или
    заменяет `import os` локально для новой логики; `os` остаётся нужен в
    `art_author` для `os.path.exists`).
  - В `art_manage_add_all` (тело):
    - `DEFAULT_AUTHOR = "NoName"` (модульная константа).
    - Для каждого `file_name` в отсортированном `disk_files`:
      - `default_author = "NoName"`
      - `default_lang = get_section(file_name)`
      - `default_title = Path(file_name).stem`
      - Если `file_name` не в `registry_by_file`: создать новую запись
        `ArticleLang(...defaults)` и увеличить `added`.
      - Иначе, если у существующей записи `author` или `lang` или `title` пустые
        (после `.strip()`): заменить соответствующие поля из дефолта, увеличить
        `filled`. Непустые пользовательские значения не трогать.
      - Иначе: `unchanged += 1`.
    - В конце `save_articles(articles)` и `flash(request,
      f"Добавлено: {added}, заполнено: {filled}, без изменений: {unchanged}",
      "success")`.
    - Если `added + filled == 0` и `unchanged > 0`: flash `"Все записи уже полные"`
      с категорией `info` (как и сейчас для случая «нет новых файлов»).
  - В `art_manage_meta` (тело, ветка создания новой записи):
    - `if not title: title = Path(file_name).stem` вместо
      `os.path.splitext(file_name)[0]`.
- Шаги:
  1. Прочитать текущее тело `art_manage_add_all` и `art_manage_meta`.
  2. Добавить `DEFAULT_AUTHOR` константу и импорт `Path`.
  3. Переписать тело `art_manage_add_all` под новый алгоритм. Сохранить порядок
     сортировки и CSRF-проверку. Сохранить существующий flash `"Нет новых файлов
     для добавления"` для случая пустого `new_files` ДО замены логики (т.е. если
     на диске нет ни одного нового файла, поведение идентично текущему).
  4. Поправить дефолт title в `art_manage_meta`.
  5. `ruff check fastapi-application/md_articles/routes_articles.py` — чисто.
  6. Сценарий qa пишется отдельной фазой проверки, но разработчик обязан
     локально проверить:
     - Поднять uvicorn, залогиниться.
     - Перед тестом: `git diff fastapi-application/md_articles/articles.yaml`
       должен показать изменения в 7 строках (неполные SUPER-записи).
     - `POST /art_manage/add_all` → `303 See Other` + flash `"Добавлено: 0,
       заполнено: 7, без изменений: 1"` (1 — это запись `1789142345` с
       `author="4"`, `lang="4"`, она уже заполнена).
     - `git diff articles.yaml` показать в `tasks/current/dev/phase03_progress.md`:
       у записей `1789142346`–`1789142352` появились `author: NoName`,
       `lang: SUPER`, `title: <stem>`.
     - `GET /art_section/SUPER` → 200, в HTML видны 8 заголовков.
- Checkpoint:
  - `ruff check ...` → 0.
  - `git diff fastapi-application/md_articles/articles.yaml` показывает
    заполненные поля у 7 записей SUPER/*.
  - `curl -s http://127.0.0.1:8000/art_section/SUPER | grep -c "badge-accent"`
    → 8 (по одному badge на статью; в качестве альтернативы — считать
    вхождения `art_main.art_author` в HTML, тоже 8).
  - Прогресс-файл `tasks/current/dev/phase03_progress.md` содержит вывод
    `git diff articles.yaml` и curl-сценарий.
- Готовность фазы: чек-лист пройден, прогресс записан, diff приложен.

## Критерии успеха

Проверяются qa по завершении всех фаз; сырые выводы — в `tasks/current/e2e/`.

| # | Критерий | Проверка | Ожидание |
|---|---|---|---|
| 1 | `len(main_app.routes) == 43` (HEAD содержит 42; некоммиченные правки task 002/003 в рабочей копии добавляют `+1` за `/art_section/{section}` и `+1` за `/art_manage/prune_missing`; фаза 1 снимает `−1` POST `/art_home`; итого 42+2−1=43. Зафиксировано оркестратором 2026-09-11 после ревью фазы 1.) | `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"` | `43` |
| 2 | `POST /art_manage/add_all` (с авторизованной сессией и CSRF) отдаёт 303 | `curl -i -X POST -b cookies.txt -d "csrf_token=..." http://127.0.0.1:8000/art_manage/add_all` | `HTTP/1.1 303 See Other` + `Location: /art_manage` |
| 3 | `POST /art_manage/meta` отдаёт 303 | `curl -i -X POST -b cookies.txt -d "csrf_token=...&file_name=...&title=...&author=...&lang=..." http://127.0.0.1:8000/art_manage/meta` | `HTTP/1.1 303 See Other` + `Location: /art_manage` |
| 4 | `POST /art_manage/prune_missing` отдаёт 303 | `curl -i -X POST -b cookies.txt -d "csrf_token=..." http://127.0.0.1:8000/art_manage/prune_missing` | `HTTP/1.1 303 See Other` + `Location: /art_manage` |
| 5 | `POST /register` (валидная форма) отдаёт 303 | `curl -i -X POST -d "csrf_token=...&username=...&email=...&password=...&confirm_password=..." http://127.0.0.1:8000/register` | `HTTP/1.1 303 See Other` + `Location: /login` |
| 6 | `POST /login` (валидная форма) отдаёт 303 | `curl -i -X POST -d "csrf_token=...&email=...&password=..." http://127.0.0.1:8000/login` | `HTTP/1.1 303 See Other` + `Location: /art_home` |
| 7 | `POST /account` (валидная форма) отдаёт 303 | `curl -i -X POST -b cookies.txt -d "csrf_token=...&username=...&email=..." http://127.0.0.1:8000/account` | `HTTP/1.1 303 See Other` + `Location: /account` |
| 8 | `require_login` гард на POST `/art_manage/add_all` без сессии отдаёт 303 на `/login?next=...` | `curl -i -X POST -d "csrf_token=..." http://127.0.0.1:8000/art_manage/add_all` (без cookie) | `HTTP/1.1 303 See Other` + `Location: /login?next=%2Fart_manage%2Fadd_all` |
| 9 | `GET /` отдаёт 303 | `curl -i http://127.0.0.1:8000/` | `HTTP/1.1 303 See Other` + `Location: /art_home` |
| 10 | В `articles.yaml` нет записей с пустыми `author`, `lang`, `title` (кроме случаев, когда пользователь явно ввёл пустую строку через форму meta — допустимо, но таких записей сейчас нет) | `python -c "import yaml; data=yaml.safe_load(open('fastapi-application/md_articles/articles.yaml')); empty=[a for a in data['articles'] if not (a['author'].strip() and a['lang'].strip() and a['title'].strip())]; print(len(empty))"` | `0` (после применения add_all к SUPER-папке) |
| 11 | `/art_section/SUPER` показывает все статьи раздела | `curl -s -b cookies.txt http://127.0.0.1:8000/art_section/SUPER \| grep -c "art_main.art_author"` | `8` (по количеству `.md` в `templates/content_art/SUPER/`) |
| 12 | `/art_home` показывает только полные записи, в т.ч. SUPER-раздел | `curl -s http://127.0.0.1:8000/art_home \| grep -c "art_main.art_author"` | `>= 88` (88 = 81 полных + 7 заполненных SUPER + 1 запись с `author="4"`/`lang="4"`) |
| 13 | `ruff check fastapi-application/` чист | `cd fastapi-application && ../.venv/bin/ruff check .` | `All checks passed!` |
| 14 | `grep status_code=307` в `md_articles/routes_*.py` и `web_utils.py` пуст | `grep -rn "status_code=307" fastapi-application/md_articles/routes_articles.py fastapi-application/md_articles/routes_users.py fastapi-application/md_articles/routes_main.py fastapi-application/md_articles/web_utils.py` | без вывода |
| 15 | Регресс: `/docs`, `/api/v1/dep_examples/single-direct-dependency`, `/users/get_all_users`, `/orders/get_all_orders` отвечают как раньше | четыре `curl -s -o /dev/null -w "%{http_code}\n" ...` | `200` для первых трёх, `200` для `/orders/get_all_orders` |

## Финальные критерии

1. Каждый критерий успеха подтверждён доказательством (e2e-заметка с сырым
   выводом curl/python, ссылка на `git diff` для правок `articles.yaml`).
2. `tasks/current/DEFECTS.md` существует только если найдены дефекты; все
   записи не OPEN.
3. Adversarial-прогон выполнен, ни одна запись
   `tasks/current/ADVERSARIAL_REVIEW.md` не PENDING.
4. Сервер, поднятый на время проверок, остановлен оркестратором при закрытии
   задания (`pgrep -af "uvicorn.*main:main_app"` → пусто).

## Открытые вопросы

Нет. yolo-режим, все развилки закрыты в «Подтверждённые решения» с обоснованием.

---

# Отчёт о выполнении

- Дата закрытия: 2026-09-11

## Итог

POST-ручки блога переведены на 303 (PRG по RFC 7231), костыль POST `/art_home` снят,
`art_manage_add_all` создаёт записи с дефолтами `("NoName", get_section, stem)` и
дополняет пустые поля уже зарегистрированных, `art_manage_meta` подставляет
`Path(file_name).stem` при пустом title.

## Чем подтверждено

- 15/15 критериев успеха PASS — `tasks/current/e2e/run-notes.md` (515 строк сырых
  curl/python выводов).
- Прогресс фаз — `tasks/current/dev/phase0{1,2,3}_progress.md`.
- Счётчик маршрутов `len(main_app.routes) == 43` зафиксирован в спеке (HEAD=42,
  некоммиченные правки 002/003 добавляют +2, фаза 1 снимает −1).
- Дефектов нет: `tasks/current/DEFECTS.md` не создан.

## Adversarial-прогон

Пропущен по решению пользователя (`так давай без adversary - заканчивай`,
2026-09-11) — модель `xiaomi/mimo-v2.5` для роли adversary была недоступна
(404 No active credentials), а пользователь явно отказался от прогона через
замену провайдера. Прогон через `general-purpose` стартовал, но был отменён
по той же команде.
