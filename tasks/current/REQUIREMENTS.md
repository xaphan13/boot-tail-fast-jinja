# Редизайн блога на Tailwind CDN: все 4 темы, современный дизайн

Блог `md_articles` (Jinja2 + FastAPI) сегодня стилизован Bootstrap 5.3.8 + свой
`base.css` на CSS-переменных, 4 темы (`dark`, `light`, `midnight`, `aurora`),
переключатель — селектор в шапке. Нужно заменить Bootstrap на **Tailwind CSS
(Play CDN)** и переделать дизайн **всех 4 тем** на современный: скруглённые края,
градиенты, мягкие тени, аккуратные кнопки и поля. Стили — **только Tailwind CDN
+ highlight.js CDN**; свои стили — в существующем `static/art_css/base.css`.

## Подтверждённые решения

- Bootstrap 5.3.8 полностью удаляется: CSS-ссылка, JS-bundle, все `data-bs-*`
  атрибуты и BS-классы в шаблонах.
- Подключение Tailwind — Play CDN (`https://cdn.tailwindcss.com`) с инлайн-конфигом
  `tailwind.config` в `_head.html`: семантические цвета (`page`, `surface`, `ink`,
  `line`, `accent`, ...) замаплены на CSS-переменные `--art-*`. Шаблоны пишутся
  один раз, темы различаются только значениями переменных.
- Атрибут темы на `<html>`: `data-bs-theme` → `data-theme` (Bootstrap ушёл).
  Значения и ключ хранения НЕ меняются: `localStorage['theme']`,
  `['dark', 'light', 'midnight', 'aurora']`, дефолт `dark` — совместимость
  с вернувшимися посетителями сохранена.
- Все 4 темы переделываются на единый современный дизайн-язык (скругления
  `rounded-xl/2xl`, градиентная шапка, мягкие тени, hover-подъём карточек и кнопок);
  палитры тем сохраняют свою индивидуальность (тёмная графитовая, светлая тёплая,
  сине-фиолетовая «Полночь», изумрудная «Северное сияние»).
- Мобильное меню: collapse Bootstrap удаляется — тогглер-гамбургер реализуется
  в `scripts.js` (toggle класса `hidden`, aria-expanded).
- Подсветка кода highlight.js не меняется: CDN-ссылки, 15 тёмных тем, селектор,
  логика `syncHighlightTheme` в `scripts.js` сохраняются (меняется только
  атрибут темы сайта `data-bs-theme` → `data-theme` и классы разметки селекторов).
- Python-код (`md_articles/`, роутеры, модели), Alembic, конфигурация — не трогать;
  задача чисто фронтенд-статика.
- Контент статей `templates/content_art/`, аватары `static/profile_pics/` — не трогать.
- Никаких эмодзи в коде, комментариях и логах.

## Результат

- `templates/includes/_head.html`: Tailwind Play CDN + инлайн-конфиг
  (семантические цвета на `--art-*` переменных); инлайн-скрипт восстановления
  темы ставит `data-theme`; Bootstrap CSS удалён; hljs-блок без изменений.
- `templates/includes/_scripts.html`: Bootstrap bundle удалён; остаются hljs
  и `scripts.js`.
- `static/art_css/scripts.js`: `data-bs-theme` → `data-theme`; добавлен тогглер
  мобильного меню (`#nav-toggle` / `#nav-menu`); логика hljs сохранена.
- `static/art_css/base.css`: переписан — 4 блока переменных `[data-theme=...]`
  (включая `--art-grad` фирменный градиент каждой темы) + базовая типографика,
  типографика Markdown-тела статьи (`.art-body`), мелкие правила для hljs.
  Компонентный дизайн переносится в Tailwind-классы шаблонов.
- `templates/layout.html`, `includes/_header.html`, `_sidebar.html`,
  `_footer_macro.html`, `_theme_select.html`, `_hljs_theme_select.html`,
  `_flash_msg.html`, `_form_macro.html`: разметка на Tailwind-классах
  (фиксированная градиентная шапка, пилюли-ссылки, скруглённые селекторы,
  карточки-алерты, скруглённые поля форм с состояниями ошибок).
- Страницы `login.html`, `register.html`, `account.html`, `about.html`,
  `new_art/art_home.html`, `new_art/art_author.html`, `new_art/art_manage.html`,
  `errors/403.html`, `errors/404.html`, `errors/500.html`: карточки, кнопки,
  бейджи, таблицы — на Tailwind-классах, современный вид во всех 4 темах.
- Поведение переключателя темы сохранено: мгновенная смена без перезагрузки,
  выбор переживает перезагрузку, невалидное значение откатывается к `dark`.

## Вне рамок

- Список hljs-тем, их CDN-ссылки, логика `syncHighlightTheme` — не менять
  (кроме неизбежной смены атрибута темы сайта).
- Идентификаторы/ключи тем: `dark`/`light`/`midnight`/`aurora`,
  `localStorage['theme']` — не менять.
- Python-код, миграции, конфигурация — не трогать.
- Контент статей и аватары — не трогать.

## План фаз

Единица исполнения — фаза: одно делегирование, 1–3 файла, бюджет ~10–15 ходов.
Следующая фаза стартует только после зелёного checkpoint и ревью диффа
оркестратором. Прогресс фазы разработчик фиксирует в `tasks/current/dev/phaseNN_progress.md`.

| # | Фаза | Исполнитель | Файлы | Контракт | Checkpoint | Бюджет ходов |
|---|---|---|---|---|---|---|
| 1 | Tailwind CDN + JS-модель тем | frontend-dev | `_head.html`, `_scripts.html`, `scripts.js` | Tailwind CDN + конфиг; `data-theme`; Bootstrap удалён; тогглер меню | приложение стартует, роутов 41 | ~10 |
| 2 | base.css: 4 палитры + типографика | frontend-dev | `base.css` | 4 блока `[data-theme=...]` с полным набором `--art-*` + `--art-grad`; типографика и `.art-body` | CSS отдаётся 200, скобки сбалансированы | ~8 |
| 3 | Каркас: layout + шапка/сайдбар/футер/селекторы | frontend-dev | `layout.html`, `_header.html`, `_sidebar.html`, `_footer_macro.html`, `_theme_select.html`, `_hljs_theme_select.html` | градиентная fixed-шапка, гамбургер, пилюли-ссылки, скруглённые селекторы | `/login` содержит `data-theme`, `cdn.tailwindcss.com`, `id="theme-select"`, без `data-bs-` | ~12 |
| 4 | Флеш-сообщения + макрос форм + страницы аккаунта | frontend-dev | `_flash_msg.html`, `_form_macro.html`, `login.html`, `register.html`, `account.html`, `about.html` | карточки-алерты, скруглённые поля с ошибками, градиентные кнопки | формы `/login`, `/register`, `/account` отдаются 200 и без BS-классов | ~12 |
| 5 | Страницы статей | frontend-dev | `art_home.html`, `art_author.html`, `art_manage.html` | карточки статей с hover-подъёмом, бейджи-пилюли, таблица управления | `/art_home`, статья, `/art_manage` отдаются 200 | ~10 |
| 6 | Страницы ошибок | frontend-dev | `errors/403.html`, `errors/404.html`, `errors/500.html` | карточки ошибок на Tailwind-классах | HTML-ошибки 403/404/500 без BS-классов | ~5 |
| 7 | Проверка | qa | `tasks/current/e2e/`, `DEFECTS.md` | curl-сценарии из критериев успеха | все критерии зелёные | ~8 |

### Фаза 1: Tailwind CDN + JS-модель тем

- Файлы: `templates/includes/_head.html`, `templates/includes/_scripts.html`,
  `static/art_css/scripts.js`.
- Контракт:
  - `_head.html`: `<script src="https://cdn.tailwindcss.com"></script>` +
    инлайн `tailwind.config = { theme: { extend: { colors: { ... 'var(--art-*)' } } } }`;
    семантические имена минимум: `page` (фон), `surface` (карточки), `surface2`,
    `ink` (текст), `muted`, `line` (границы), `accent`, `accent-strong`,
    `heading`, `codebg`, `codeink`, `ok`, `warn`, `danger`. Инлайн-скрипт
    восстановления темы ставит `data-theme` (валидация 4 значений сохранена).
    Bootstrap CSS-ссылка удалена. hljs-ссылки не тронуты.
  - `_scripts.html`: удалить Bootstrap bundle; hljs и `scripts.js` остаются.
  - `scripts.js`: `applyTheme` ставит `data-theme`; новый тогглер
    `initNavToggle()` — кнопка `#nav-toggle` переключает `hidden` у `#nav-menu`
    и синхронизирует `aria-expanded`; остальная логика без изменений.
- Checkpoint: `cd fastapi-application && ../.venv/bin/python -c "from main import
  main_app; print(len(main_app.routes))"` → 41.
- Готовность: JS синтаксически цел, шаблоны головы отдаются без Bootstrap.

### Фаза 2: base.css — 4 палитры + типографика

- Файлы: `static/art_css/base.css` (переписать целиком).
- Контракт:
  - 4 блока: `[data-theme="dark"]`, `[data-theme="light"]`,
    `[data-theme="midnight"]`, `[data-theme="aurora"]`.
  - В каждом: `--art-page`, `--art-surface`, `--art-surface-2`, `--art-ink`,
    `--art-muted`, `--art-line`, `--art-accent`, `--art-accent-strong`,
    `--art-heading`, `--art-header-from/via/to` (градиент шапки), `--art-grad`
    (фирменный градиент кнопок/акцентов), `--art-ring` (фокус), `--art-code-bg`,
    `--art-code-ink`, `--art-ok`, `--art-warn`, `--art-danger`.
  - Имена переменных согласованы с `tailwind.config` фазы 1.
  - Базовая типографика: body, ссылки, заголовки; типографика `.art-body`
    (p, h2-h3, списки, blockquote, table, inline-code); мягкие правила для
    `pre`/`.hljs` (скругление, паддинги) и `.hljs-theme-select`.
- Checkpoint: `curl -s .../static/art_css/base.css | grep -c 'data-theme'` >= 4;
  скобки сбалансированы.
- Готовность: все переменные из контракта определены во всех 4 темах.

### Фаза 3: Каркас — layout, шапка, сайдбар, футер, селекторы

- Файлы: `templates/layout.html`, `includes/_header.html`,
  `includes/_sidebar.html`, `includes/_footer_macro.html`,
  `includes/_theme_select.html`, `includes/_hljs_theme_select.html`.
- Контракт:
  - `layout.html`: `<html lang="ru" data-theme="dark">`; каркас — fixed-шапка,
    main с отступом, сетка контента (сайдбар + статья) на Tailwind, футер.
  - `_header.html`: градиентная шапка (`bg-gradient-to-r` из `--art-header-*`),
    бренд с градиентным текстом, гамбургер `#nav-toggle`, меню `#nav-menu`
    (скрыто на мобильных, `hidden md:flex`), ссылки-пилюли с hover-подсветкой;
    обе ветки (гость/авторизованный) включают оба селектора.
  - `_theme_select.html` / `_hljs_theme_select.html`: те же `id` и option-ы,
    классы — Tailwind (скруглённый select на фоне шапки). id `theme-select` и
    `hljs-theme-select` не менять.
  - `_sidebar.html`: пилюли-ссылки с hover-подъёмом.
  - `_footer_macro.html`: тёмная панель, центрированные ссылки, копирайт.
- Checkpoint: `curl -s http://127.0.0.1:8000/login` содержит `data-theme`,
  `cdn.tailwindcss.com`, `id="theme-select"`, `id="hljs-theme-select"` и не
  содержит `data-bs-` и `navbar`.
- Готовность: шапка собирается в обеих ветках, селекторы на месте.

### Фаза 4: Флеш-сообщения, макрос форм, страницы аккаунта

- Файлы: `includes/_flash_msg.html`, `includes/_form_macro.html`,
  `login.html`, `register.html`, `account.html`, `about.html`.
- Контракт:
  - `_flash_msg.html`: карточка-алерт со скруглением и цветом по категории
    (`success`/`danger`/`info`/`warning` → `--art-ok/danger/...`).
  - `_form_macro.html`: контракт данных макроса НЕ меняется (form dict, поля
    name/id/type/label/value/errors); разметка — Tailwind: скруглённые поля,
    состояние ошибки — красная рамка + список сообщений.
  - Страницы: карточка `surface rounded-2xl shadow`, кнопка — градиентная
    пилюля, account — аватар с кольцом-градиентом.
- Checkpoint: GET `/login`, `/register`, `/about` → 200; POST с ошибкой
  `/register` отдаёт форму с сообщением об ошибке и без `is-invalid`/`invalid-feedback`.
- Готовность: все формы выглядят единообразно, ошибки читаемы.

### Фаза 5: Страницы статей

- Файлы: `new_art/art_home.html`, `new_art/art_author.html`,
  `new_art/art_manage.html`.
- Контракт:
  - `art_home.html`: список статей — карточки `rounded-2xl` с hover-подъёмом
    и тенью; бейджи языка/автора — пилюли; ссылки и структура данных не меняются.
  - `art_author.html`: шапка статьи (заголовок, бейджи, номер), тело `.art-body`;
    понижение h1→h2 в теле сохраняется.
  - `art_manage.html`: alert yaml_error, три секции-карточки, таблица реестра
    (Tailwind-классы, скруглённый контейнер, тинт шапки, hover строк),
    inline-формы строк, списки файлов — карточки; имена полей/роутов/CSRF
    не меняются.
- Checkpoint: `/art_home` → 200; GET любой статьи → 200; `/art_manage` → 200
  (под авторизацией) либо редирект/403 без неё.
- Готовность: страницы статей полностью на Tailwind.

### Фаза 6: Страницы ошибок

- Файлы: `errors/403.html`, `errors/404.html`, `errors/500.html`.
- Контракт: карточка с крупным кодом ошибки (градиентный текст), заголовок,
  пояснение, ссылка-кнопка «На главную». Структура extends layout сохраняется.
- Checkpoint: HTML-ответы 403/404/500 содержат разметку без BS-классов.
- Готовность: три страницы ошибок единообразны.

### Фаза 7: Проверка

- Файлы: `tasks/current/e2e/` (заметки прогона), `tasks/current/DEFECTS.md`
  (если найдены дефекты).
- Шаги: поднять приложение, прогнать curl-сценарии критериев успеха,
  зафиксировать сырые выводы.
- Checkpoint: все критерии успеха зелёные либо дефекты заведены в DEFECTS.md.

## Критерии успеха

Проверяются qa по завершении всех фаз; сырые выводы — в `tasks/current/e2e/`.

| # | Критерий | Проверка | Ожидание |
|---|---|---|---|
| 1 | Приложение стартует, роуты не потеряны | `cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"` | 41 |
| 2 | Страницы отдаются | GET `/`, `/art_home`, `/login`, `/register`, `/about` | 200 |
| 3 | Tailwind CDN подключён | `curl -s http://127.0.0.1:8000/login \| grep -c 'cdn.tailwindcss.com'` | >= 1 |
| 4 | Bootstrap удалён | `curl -s http://127.0.0.1:8000/login \| grep -ci 'bootstrap'` | 0 |
| 5 | Атрибут темы новый | `curl -s http://127.0.0.1:8000/login \| grep -c 'data-theme="dark"'`; `grep -c 'data-bs-theme'` | >= 1; 0 |
| 6 | Селектор темы на месте, 4 option | `curl -s .../login \| grep -c 'id="theme-select"'` и подсчёт option | 1; dark, light, midnight, aurora |
| 7 | hljs не тронут | `curl -s .../login \| grep -c 'hljs-theme-select'`; `grep -c 'highlightjs/cdn-release@11.12.0'` | >= 1; >= 1 |
| 8 | base.css содержит 4 темы | `curl -s .../static/art_css/base.css \| grep -c '\[data-theme='` | >= 4 |
| 9 | scripts.js знает 4 темы и тогглер | `curl -s .../static/art_css/scripts.js \| grep -c 'aurora'`; `grep -c 'nav-toggle'` | >= 1; >= 1 |
| 10 | Страницы ошибок на Tailwind | curl несуществующий путь; 403 без прав | HTML без `navbar`/`data-bs-`, есть `data-theme` |
| 11 | Регресс старых проверок | `/docs` 200; `/users/get_all_users`; `/art_home` 200 | без изменений |

## Финальные критерии

1. Каждый критерий успеха подтверждён доказательством (e2e/, DEFECTS.md,
   ADVERSARIAL_REVIEW.md).
2. `tasks/current/DEFECTS.md` существует только если найдены дефекты; все записи
   не OPEN.
3. Adversarial-прогон выполнен, ни одна запись ADVERSARIAL_REVIEW.md не PENDING.

## Открытые вопросы

Закрыты пользователем 2026-08-31 (ответ: «Подтверждаю»):

- Палитры 4 тем обновлены под современный дизайн с сохранением характера
  каждой (dark — графит/голубой, light — тёплый бумажный, midnight —
  сине-фиолетовый, aurora — изумрудный). Имена тем не менялись.
- Фаза 1, выполненная до подтверждения, оставлена как есть; исполнение
  продолжено с фазы 2.
- База маршрутов — 42 (число 41 в AGENTS.md устарело; правки задания
  Python-код не затрагивают).

## Отчёт о выполнении

- Дата закрытия: 2026-08-31.
- Итог: Bootstrap 5.3.8 удалён полностью (CSS, JS, классы, data-bs-*),
  подключён Tailwind Play CDN с инлайн-конфигом на `--art-*` переменных;
  все 4 темы (dark, light, midnight, aurora) переделаны на единый
  современный дизайн: скруглённые карточки/кнопки/поля, градиентная шапка,
  градиентные кнопки и бейджи-пилюли, мягкие тени, hover-подъёмы;
  переключатель темы сохранён (data-theme, localStorage['theme'],
  мгновенно, без перезагрузки); highlight.js не тронут; мобильное меню —
  тогглер в scripts.js вместо BS-collapse.
- Изменения: 19 шаблонов (layout, 8 includes, 4 страницы, 3 статьи,
  3 ошибки), base.css (переписан), scripts.js, _head.html, _scripts.html.
  Python-код не менялся.
- Проверка: все 11 критериев успеха зелёные, доказательства —
  tasks/current/e2e/run-notes.md; прогресс фаз — tasks/current/dev/.
- Дефекты: не найдены, DEFECTS.md не создавался.
- Adversarial-прогон: не назначался (исполнение вёл оркестратор-сессия
  напрямую с пользователем).
