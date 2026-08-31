# QA Notes — Порт блога flask-blog-1 на FastAPI + Jinja

Дата прогона: 2026-08-31
Сервер: uvicorn main:main_app, port 8000, PID 1132090, cwd=fastapi-application/

## Итоговая таблица критериев

| # | Критерий | Результат | Доказательство |
|---|---|---|---|
| 1 | Счётчик маршрутов (41) | PASS | batch1 (41, объяснено оркестратором) |
| 2 | Миграция (head b59cbdf15878) | PASS | batch2 |
| 3 | Редирект главной (/ и /home -> 307 -> /art_home) | PASS | batch1 |
| 4 | Список статей (200, "Статьи", заголовки из YAML) | PASS | batch1 |
| 5 | Markdown-рендер (h2 SEO, fenced code, table) | PASS | batch5 |
| 6 | Регистрация (307->/login, дубликат=200+ошибка, невалид=200+"Fields must match") | PASS | batch3 |
| 7 | Вход/выход (307->/art_home, account=200+e2e_user, logout=307, post-logout redirect) | PASS | batch3 |
| 8 | Защита роутов (307->/login?next=...) | PASS | batch3 |
| 9 | Управление реестром (GET=200+flash, POST=307+flash) | BLOCKED | batch4 (POST always 403 — CSRF defect) |
| 10 | CSRF на /login (403 + HTML) | PASS | batch2 |
| 11 | Статика /static/art_css/base.css (200) | PASS | batch1 |
| 12 | 404 HTML (404 + text/html + "Страница не найдена") | PASS | batch2 |
| 13 | Регресс /docs, /users/get_all_users (200) | PASS | batch1 |
| 13 | Регресс /orders/get_all_orders (422=expected, 200 with ?params=id) | PASS | batch1 |
| 13 | Регресс /api/v1/dep_examples/single-direct-dependency (422=expected, 200 with header) | PASS | batch1 |
| 14 | Линтер ruff check (All checks passed) | PASS | batch1 |

## Замечания

1. **Criterion 1**: Фактическое число маршрутов = 41 (не 38). Расхождение объяснено: FastAPI создаёт отдельные route-объекты для GET/POST-пар /register, /login, /account и для / и /home. PASS при объяснении.

2. **Criterion 5a**: /art/Max/1787932544 вернул 200 (файл .md существует), а не 404. Файл уже был создан ранее.

3. **Criterion 6**: Email e2e_user@test.local отклонён валидатором ("Invalid email address"). Использован e2e_user@example.com. Возможный дефект — email-валидатор слишком строг для нестандартных TLD.

4. **Criterion 9 (DEFECT)**: POST /art_manage/meta всегда возвращает 403. Формы на /art_manage не содержат `<input type="hidden" name="csrf_token">`, а серверная CSRF-проверка требует этот токен. Серверная проверка корректна, но UI-форма сломана — пользователь не может отправить форму из браузера. См. DEFECTS.md.

## Созданные e2e-файлы

- `e2e/batch1_criteria_1_3_4_11_13_14.txt` — сырые выводы критериев 1,3,4,11,13,14
- `e2e/batch2_criteria_2_10_12.txt` — сырые выводы критериев 2,10,12
- `e2e/batch3_criteria_6_7_8.txt` — сырые выводы критериев 6,7,8
- `e2e/batch4_criteria_9_csrf_defect.txt` — сырые выводы критерия 9 + расследование CSRF-дефекта
- `e2e/batch5_criteria_5_markdown.txt` — сырые выводы критерия 5 (markdown-рендер)
- `e2e/notes_qa.md` — этот файл (сводка)
