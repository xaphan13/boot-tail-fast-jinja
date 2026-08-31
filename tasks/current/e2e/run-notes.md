# Прогон проверок — Tailwind-редизайн блога (2026-08-31)

Сервер: `nohup ../.venv/bin/uvicorn main:main_app --port 8000` из
`fastapi-application/`, проверки curl. Полные сырые выводы: /tmp/checks.txt,
/tmp/checks2.txt (продублированы ниже по секциям).

## 1. Статус-коды

```
/                        307   (редирект на /art_home — штатно)
/art_home                200
/login                   200
/register                200
/about                   200
/docs                    200
/users/get_all_users     200
/orders/get_all_orders   422   (требует query-параметры — вне задания)
```

## 2. /login — состав страницы

```
tailwind cdn:        1      (критерий 3)
bootstrap refs:      0      (критерий 4)
data-theme="dark":   1      (критерий 5)
data-bs-theme:       0
navbar:              0
theme-select:        1      (критерий 6)
options тем:         dark, light, midnight, aurora — все 4 на месте
hljs-theme-select:   3      (критерий 7)
hljs cdn ссылки:     17     (16 тем + сам highlight.min.js)
nav-toggle/nav-menu: 1/2
```

## 3. base.css и scripts.js

```
блоков [data-theme=: 8   (4 палитры + 3 в группе color-scheme + 1 light) — критерий 8
скобки: 44/44 — сбалансированы
scripts.js: aurora=2, nav-toggle=3, data-bs-theme=0 — критерий 9
```

## 4. Страница ошибки 404

```
code: 404, data-theme: да, navbar: 0, grad-text: 1 — критерий 10
```

## 5. Страница статьи (/art/aaa/1787935183)

```
code: 200
art-body: 1, badge: 2, h1: ровно 1 (SEO-критерий сохранён), pre: 1
```

## 6. Флеш-сообщения (/about, все 5 категорий)

```
flash-success: 1, flash-danger: 1, flash-info: 1, flash-warning: 1, flash-message: 1
```

## 7. Валидация форм (POST)

```
POST /register (username=ab, email=bad, пароли не совпадают):
  code 200; ошибки отрендерены (text-danger=2); invalid-feedback=0; is-invalid=0
POST /login (неверный пароль):
  code 200; flash-danger=1 («Login Unsuccessful...»)
```

## 8. Авторизация

```
/art_manage без авторизации: 307 -> /login?next=/art_manage (штатно)
```

## 9. Роуты и регресс

```
from main import main_app -> 42 маршрута.
Правки задания не касаются Python-кода (только templates/ + static/),
значит 42 — до-заданная база; цифра 41 в AGENTS.md устарела.
BS-классов в templates/ и static/ не осталось (grep по списку — пусто).
```

## Итог

Все критерии успеха из REQUIREMENTS.md выполнены, дефектов не найдено,
DEFECTS.md не создаётся.
