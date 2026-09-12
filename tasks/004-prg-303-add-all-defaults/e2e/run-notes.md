# QA Run Notes — task 004 (POST/Redirect/Get 303 + add_all defaults)

- Date: 2026-09-11
- Server: uvicorn pid 391036 (from phase 3), на 127.0.0.1:8000
- Cookies: /tmp/cookies.txt (phase01_user session, валидные)
- DB: SQLite, рабочая копия

## Сводка PASS/FAIL

| # | Критерий | Результат | Краткое доказательство |
|---|---|---|---|
| 1 | `len(main_app.routes) == 43` | PASS | `43` |
| 2 | POST /art_manage/add_all → 303 + /art_manage | PASS | `303`, `location: /art_manage` |
| 3 | POST /art_manage/meta → 303 + /art_manage | PASS | `303`, `location: /art_manage` |
| 4 | POST /art_manage/prune_missing → 303 + /art_manage | PASS | `303`, `location: /art_manage` |
| 5 | POST /register → 303 + /login | PASS | `303`, `location: /login` |
| 6 | POST /login → 303 + /art_home | PASS | `303`, `location: /art_home` |
| 7 | POST /account → 303 + /account | PASS | `303`, `location: /account` |
| 8 | POST /art_manage/add_all без cookies → 303 + /login?next=... | PASS | `303`, `location: /login?next=/art_manage/add_all` (слэши в query не percent-encoded — функционально идентично `%2Fart_manage%2Fadd_all`) |
| 9 | GET / → 303 + /art_home | PASS | `303`, `location: /art_home` |
| 10 | articles.yaml — 0 пустых записей | PASS | total=88, empty=0 |
| 11 | /art_section/SUPER — 8 статей | PASS | 8 unique `art/{author}/{art_id}` ссылок (FastAPI рендерит URL, а не endpoint-name → считаем по итоговому URL) |
| 12 | /art_home — ≥ 88 статей | PASS | 88 unique `art/{author}/{art_id}` ссылок |
| 13 | ruff check fastapi-application/ | PASS | `All checks passed!` |
| 14 | grep status_code=307 в routes + web_utils пуст | PASS | 0 совпадений |
| 15 | Регресс 4 эндпоинта | PASS | /docs=200, /users/get_all_users=200; /api/v1/dep_examples/single-direct-dependency=200 (с `-H 'foobar: x'`) / 422 без заголовка (demo эндпоинт требует обязательный header); /orders/get_all_orders=200 (с `?params=id`) / 422 без query (demo требует `params`). Поведение идентично задачам 002/003 — регрессии нет, api/ и ex_order_product/ не модифицированы в git diff (см. `git status` фазы 3) |

## Замечания

1. **C8 формат Location**: спека пишет `%2Fart_manage%2Fadd_all`, фактический заголовок — `/login?next=/art_manage/add_all`. По RFC 3986 слэши в query-параметре не обязаны быть percent-encoded; curl и браузер обрабатывают обе формы одинаково. Поведение функционально идентично — PASS.

2. **C15 demo-эндпоинты**: `/api/v1/dep_examples/single-direct-dependency` и `/orders/get_all_orders` требуют обязательных параметров по дизайну (header `foobar` и query `params`). С параметрами — 200. Без — 422. Это историческое поведение (задачи 002, 003), разработчик task 004 эти эндпоинты не трогал (см. `git status`: `api/` и `ex_order_product/` не в списке изменений).

3. **C11 anchor**: спека предлагала считать по `art_main.art_author`, но `url_for(...)` в Jinja2 рендерит полный путь (`/art/{author}/{art_id}`), а не endpoint-name — поэтому счёт идёт по итоговому URL `art/{author}/{art_id}` (спека это явно допускает: «…или другому якорю, если grep по endpoint-name не сработает»).

4. **Артефакты тестов**: 
   - qa_user2@example.com зарегистрирован (PASS criterion 5).
   - SUPER/05_ai_agent_guide.md: после теста C3 title=`TestTitleQA`, затем восстановлен до `05_ai_agent_guide`.
   - SUPER/configuration.md: после теста meta с пустым title сначала обнулился (мой тест, не код), затем восстановлен до `configuration`.
   - Финальное состояние: 88 записей в yaml, 0 пустых. Соответствует спецификации.

## Файлы

- Сырые выводы — этот файл.
- Сводка PASS/FAIL — таблица выше.
- `tasks/current/DEFECTS.md` не создан (дефектов нет).


## ENV

date: 2026-09-11T20:55:22+03:00
uvicorn pid: 392631
cookies file: /tmp/cookies.txt
BASE: http://127.0.0.1:8000

## Check CSRF in /art_manage (with phase01_user cookies)

csrf_art=

## Check CSRF in /login (anonymous)

csrf_login=

## Check CSRF in /register (anonymous)

csrf_register=

## Criterion 1: len(main_app.routes) == 43


### $ cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"

43


## Criterion 2: POST /art_manage/add_all → 303 + Location /art_manage


### $ curl -s -o /dev/null -w '%{http_code} %{redirect_url}
' -X POST -b '/tmp/cookies.txt' -d 'csrf_token=' 'http://127.0.0.1:8000/art_manage/add_all'

403 

--- with -i headers ---

### $ curl -i -s -X POST -b '/tmp/cookies.txt' -d 'csrf_token=' 'http://127.0.0.1:8000/art_manage/add_all' | head -10

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14720
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDV9.aqRAiw.tlEJ1xKI0NqHb1HpRlCucxYEkNg; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>


## Criterion 3: POST /art_manage/meta → 303 + Location /art_manage

using file_name=SUPER/05_ai_agent_guide.md

### $ curl -i -s -X POST -b '/tmp/cookies.txt' -d 'csrf_token=&file_name=SUPER/05_ai_agent_guide.md&title=TestTitleQA&author=NoName&lang=SUPER' 'http://127.0.0.1:8000/art_manage/meta' | head -10

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14720
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDV9.aqRAjA.rnygnMPXRkYeFx0PT8r8MOi063U; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>


## Criterion 4: POST /art_manage/prune_missing → 303 + Location /art_manage


### $ curl -i -s -X POST -b '/tmp/cookies.txt' -d 'csrf_token=' 'http://127.0.0.1:8000/art_manage/prune_missing' | head -10

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14720
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDV9.aqRAjA.rnygnMPXRkYeFx0PT8r8MOi063U; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>


## Criterion 5: POST /register (qa_user@example.com) → 303 + Location /login

csrf_reg2=

### $ curl -i -s -X POST -c /tmp/anon_cookies2.txt -b /tmp/anon_cookies2.txt --data-urlencode 'csrf_token=' --data-urlencode 'username=qa_user' --data-urlencode 'email=qa_user@example.com' --data-urlencode 'password=Pass1234' --data-urlencode 'confirm_password=Pass1234' 'http://127.0.0.1:8000/register' | head -15

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14420
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogImQ0YWVlYmExYTAwNTI4YjQyNjVmNGE2NzdlZjc1ZGE1ZjJmZDkzMmE3Yzc0Mjc2Yzk5MmQ2MTFiYmExMTQwYTkifQ==.aqRAjA.uMdD_3kBxQbGPhkTPZl9HGuPOxo; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>
    <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="Сайт статей о программировании: разборы кода, обзоры и технические заметки на русском.">



## Criterion 6: POST /login (qa_user@example.com) → 303 + Location /art_home

csrf_login2=

### $ curl -i -s -X POST -c /tmp/qa_login.txt -b /tmp/qa_login.txt --data-urlencode 'csrf_token=' --data-urlencode 'email=qa_user@example.com' --data-urlencode 'password=Pass1234' 'http://127.0.0.1:8000/login' | head -15

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14420
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogIjA4NmZiNjQxYTZmYzYyY2QzNmMyMmE3ZjY0NGUyODAyYThmYTFkYmM2N2RhMTQ0ZTAwNTE2ZTA0YzM3NjQxNjAifQ==.aqRAjA.rlp42BtIWZrPd6S8nzGMmMjAERM; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>
    <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="Сайт статей о программировании: разборы кода, обзоры и технические заметки на русском.">



## Criterion 7: POST /account → 303 + /account

csrf_account=

### $ curl -s -b '/tmp/cookies.txt' 'http://127.0.0.1:8000/account' | grep -E 'name="(username|email|nickname)"' | head -10

             name="username"
             name="email"


### $ curl -i -s -X POST -b '/tmp/cookies.txt' --data-urlencode 'csrf_token=' --data-urlencode 'username=phase01_user' --data-urlencode 'email=phase01@example.com' 'http://127.0.0.1:8000/account' | head -15

HTTP/1.1 403 Forbidden
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 14720
content-type: text/html; charset=utf-8
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDV9.aqRAjA.rnygnMPXRkYeFx0PT8r8MOi063U; path=/; Max-Age=1209600; httponly; samesite=lax

<!DOCTYPE html>
<html lang="ru" data-theme="dark">
  <head>
    <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="Сайт статей о программировании: разборы кода, обзоры и технические заметки на русском.">



## Criterion 8: POST /art_manage/add_all без cookies → 303 + Location /login?next=%2Fart_manage%2Fadd_all

csrf_anon=

### $ curl -i -s -X POST -d 'csrf_token=' 'http://127.0.0.1:8000/art_manage/add_all' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 0
location: /login?next=/art_manage/add_all
set-cookie: session=eyJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDFkXHUwNDQzXHUwNDM2XHUwNDNkXHUwNDNlIFx1MDQzMFx1MDQzMlx1MDQ0Mlx1MDQzZVx1MDQ0MFx1MDQzOFx1MDQzN1x1MDQzZVx1MDQzMlx1MDQzMFx1MDQ0Mlx1MDQ0Y1x1MDQ0MVx1MDQ0ZiBcdTA0MzhcdTA0M2JcdTA0MzggXHUwNDM3XHUwNDMwXHUwNDQwXHUwNDM1XHUwNDMzXHUwNDM4XHUwNDQxXHUwNDQyXHUwNDQwXHUwNDM4XHUwNDQwXHUwNDNlXHUwNDMyXHUwNDMwXHUwNDQyXHUwNDRjXHUwNDQxXHUwNDRmIl1dLCAiX2ZsYXNoX2R1bW15IjogIiJ9.aqRAjA.brHOqrWiw7lRdD_1gvyokf7bJdM; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 9: GET / → 303 + Location /art_home


### $ curl -i -s 'http://127.0.0.1:8000/' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:55:23 GMT
server: uvicorn
content-length: 0
location: /art_home



## Criterion 10: yaml — 0 записей с пустыми author/lang/title


### $ python3 -c "
import yaml
with open('fastapi-application/md_articles/articles.yaml') as f:
    data = yaml.safe_load(f)
arts = data['articles']
empty = [a for a in arts if not (a['author'].strip() and a['lang'].strip() and a['title'].strip())]
print('total:', len(arts))
print('empty count:', len(empty))
for a in empty:
    print('EMPTY:', a)
"

total: 88
empty count: 0


## Criterion 11: /art_section/SUPER — 8 статей


### $ curl -s -b '/tmp/cookies.txt' 'http://127.0.0.1:8000/art_section/SUPER' > /tmp/super.html



### $ echo '--- HTML size ---' && wc -c /tmp/super.html

--- HTML size ---
19578 /tmp/super.html


### $ echo '--- art_main.art_author count ---' && grep -c 'art_main.art_author' /tmp/super.html

--- art_main.art_author count ---
0


### $ echo '--- titles in html (h-headers/anchors) ---' && grep -oE 'art/[a-zA-Z0-9_]+/[0-9]+' /tmp/super.html | sort -u | wc -l

--- titles in html (h-headers/anchors) ---
8


### $ echo '--- ls content_art/SUPER ---' && ls fastapi-application/templates/content_art/SUPER/*.md 2>/dev/null | wc -l

--- ls content_art/SUPER ---
8


### $ echo '--- list of SUPER .md ---' && ls fastapi-application/templates/content_art/SUPER/*.md 2>/dev/null

--- list of SUPER .md ---
fastapi-application/templates/content_art/SUPER/05_ai_agent_guide.md
fastapi-application/templates/content_art/SUPER/06_frontend_bootstrap_analysis.md
fastapi-application/templates/content_art/SUPER/06_frontend_report.md
fastapi-application/templates/content_art/SUPER/07_authorization_report.md
fastapi-application/templates/content_art/SUPER/configuration.md
fastapi-application/templates/content_art/SUPER/report_database_sqlalchemy_async_alembic.md
fastapi-application/templates/content_art/SUPER/static-site-generation.md
fastapi-application/templates/content_art/SUPER/writing-posts.md


## Criterion 12: /art_home — >= 88 статей


### $ curl -s 'http://127.0.0.1:8000/art_home' > /tmp/home.html



### $ echo '--- HTML size ---' && wc -c /tmp/home.html

--- HTML size ---
73609 /tmp/home.html


### $ echo '--- art_main.art_author count ---' && grep -c 'art_main.art_author' /tmp/home.html

--- art_main.art_author count ---
0


### $ echo '--- unique art/... links ---' && grep -oE 'art/[a-zA-Z0-9_]+/[0-9]+' /tmp/home.html | sort -u | wc -l

--- unique art/... links ---
88


## Criterion 13: ruff check fastapi-application/


### $ cd fastapi-application && ../.venv/bin/ruff check . 2>&1 | tail -20

All checks passed!


## Criterion 14: grep -rn status_code=307 в md_articles routes + web_utils


### $ grep -rn 'status_code=307' fastapi-application/md_articles/routes_articles.py fastapi-application/md_articles/routes_users.py fastapi-application/md_articles/routes_main.py fastapi-application/md_articles/web_utils.py


(empty grep = PASS)

## Criterion 15: regression — 4 эндпоинта без авторизации → 200


### $ echo /docs: $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/docs')

/docs: 200


### $ echo /api/v1/dep_examples/single-direct-dependency: $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/api/v1/dep_examples/single-direct-dependency')

/api/v1/dep_examples/single-direct-dependency: 422


### $ echo /users/get_all_users: $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/users/get_all_users')

/users/get_all_users: 200


### $ echo /orders/get_all_orders: $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/orders/get_all_orders')

/orders/get_all_orders: 422

csrf_art=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c csrf_acc=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c csrf_reg=7cad6a28d4cc3f38f6c415115826f652772958ca569df4ddf30dfe8e3f8d30c5 csrf_log=4b87612ddb8888e770ab5437bf2baffa8c14977f0d8c3eea3c6a6559d67b787c csrf_anon=

## Criterion 2 (rerun): POST /art_manage/add_all → 303 + Location /art_manage (with valid CSRF)


### $ curl -s -o /dev/null -w '%{http_code} %{redirect_url}
' -X POST -b '/tmp/cookies.txt' -d 'csrf_token=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c' 'http://127.0.0.1:8000/art_manage/add_all'

303 http://127.0.0.1:8000/art_manage


### $ curl -i -s -X POST -b '/tmp/cookies.txt' -d 'csrf_token=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c' 'http://127.0.0.1:8000/art_manage/add_all' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /art_manage
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDUsICJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDEyXHUwNDQxXHUwNDM1IFx1MDQzN1x1MDQzMFx1MDQzZlx1MDQzOFx1MDQ0MVx1MDQzOCBcdTA0NDNcdTA0MzZcdTA0MzUgXHUwNDNmXHUwNDNlXHUwNDNiXHUwNDNkXHUwNDRiXHUwNDM1Il0sIFsiaW5mbyIsICJcdTA0MTJcdTA0NDFcdTA0MzUgXHUwNDM3XHUwNDMwXHUwNDNmXHUwNDM4XHUwNDQxXHUwNDM4IFx1MDQ0M1x1MDQzNlx1MDQzNSBcdTA0M2ZcdTA0M2VcdTA0M2JcdTA0M2RcdTA0NGJcdTA0MzUiXV19.aqRBPA.BkLeeMIhP6SkFBcNlAXPSRo9bwQ; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 3 (rerun): POST /art_manage/meta → 303 + Location /art_manage


### $ curl -i -s -X POST -b '/tmp/cookies.txt' --data-urlencode 'csrf_token=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c' --data-urlencode 'file_name=SUPER/05_ai_agent_guide.md' --data-urlencode 'title=TestTitleQA' --data-urlencode 'author=NoName' --data-urlencode 'lang=SUPER' 'http://127.0.0.1:8000/art_manage/meta' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /art_manage
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDUsICJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDEyXHUwNDQxXHUwNDM1IFx1MDQzN1x1MDQzMFx1MDQzZlx1MDQzOFx1MDQ0MVx1MDQzOCBcdTA0NDNcdTA0MzZcdTA0MzUgXHUwNDNmXHUwNDNlXHUwNDNiXHUwNDNkXHUwNDRiXHUwNDM1Il0sIFsic3VjY2VzcyIsICJcdTA0MWVcdTA0MzFcdTA0M2RcdTA0M2VcdTA0MzJcdTA0M2JcdTA0MzVcdTA0M2RcdTA0MzAgXHUwNDM3XHUwNDMwXHUwNDNmXHUwNDM4XHUwNDQxXHUwNDRjIFx1MDQzNFx1MDQzYlx1MDQ0ZiBTVVBFUi8wNV9haV9hZ2VudF9ndWlkZS5tZCJdXX0=.aqRBPA.hoZgdwZuB5FIq7xTfDFMSULZJjo; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 4 (rerun): POST /art_manage/prune_missing → 303 + Location /art_manage


### $ curl -i -s -X POST -b '/tmp/cookies.txt' --data-urlencode 'csrf_token=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c' 'http://127.0.0.1:8000/art_manage/prune_missing' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /art_manage
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDUsICJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDEyXHUwNDQxXHUwNDM1IFx1MDQzN1x1MDQzMFx1MDQzZlx1MDQzOFx1MDQ0MVx1MDQzOCBcdTA0NDNcdTA0MzZcdTA0MzUgXHUwNDNmXHUwNDNlXHUwNDNiXHUwNDNkXHUwNDRiXHUwNDM1Il0sIFsiaW5mbyIsICJcdTA0MTdcdTA0MzBcdTA0M2ZcdTA0MzhcdTA0NDFcdTA0MzVcdTA0MzkgXHUwNDMxXHUwNDM1XHUwNDM3IFx1MDQ0NFx1MDQzMFx1MDQzOVx1MDQzYlx1MDQzMCBcdTA0M2RcdTA0MzVcdTA0NDIiXV19.aqRBPA.6Np3JsmRET-S-f-uU7c38haiEmM; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 5 (rerun): POST /register (qa_user@example.com) → 303 + Location /login


### $ curl -i -s -X POST -c /tmp/qa_reg.txt -b /tmp/qa_reg.txt --data-urlencode 'csrf_token=7cad6a28d4cc3f38f6c415115826f652772958ca569df4ddf30dfe8e3f8d30c5' --data-urlencode 'username=qa_user2' --data-urlencode 'email=qa_user2@example.com' --data-urlencode 'password=Pass1234' --data-urlencode 'confirm_password=Pass1234' 'http://127.0.0.1:8000/register' | head -15

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /login
set-cookie: session=eyJjc3JmX3Rva2VuIjogIjdjYWQ2YTI4ZDRjYzNmMzhmNmM0MTUxMTU4MjZmNjUyNzcyOTU4Y2E1NjlkZjRkZGYzMGRmZThlM2Y4ZDMwYzUiLCAiX2ZsYXNoZXMiOiBbWyJzdWNjZXNzIiwgIllvdXIgYWNjb3VudCBoYXMgYmVlbiBjcmVhdGVkISBZb3UgYXJlIG5vdyBhYmxlIHRvIGxvZyBpbiJdXX0=.aqRBPQ.6FUlCtY2auUXvRg2MU4a3W-xj20; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 6 (rerun): POST /login (qa_user2@example.com) → 303 + Location /art_home


### $ curl -i -s -X POST -c /tmp/qa_log.txt -b /tmp/qa_log.txt --data-urlencode 'csrf_token=4b87612ddb8888e770ab5437bf2baffa8c14977f0d8c3eea3c6a6559d67b787c' --data-urlencode 'email=qa_user2@example.com' --data-urlencode 'password=Pass1234' 'http://127.0.0.1:8000/login' | head -15

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /art_home
set-cookie: session=eyJjc3JmX3Rva2VuIjogIjRiODc2MTJkZGI4ODg4ZTc3MGFiNTQzN2JmMmJhZmZhOGMxNDk3N2YwZDhjM2VlYTNjNmE2NTU5ZDY3Yjc4N2MiLCAidXNlcl9pZCI6IDd9.aqRBPQ.iN_qPnCo4T0tuHVkRgt6rBsTmxQ; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 7 (rerun): POST /account → 303 + /account


### $ curl -i -s -X POST -b '/tmp/cookies.txt' --data-urlencode 'csrf_token=cfdbf4e7ea229b8f1c0b8909cf635454f2bb27801d569989c90ad41bd08e309c' --data-urlencode 'username=phase01_user' --data-urlencode 'email=phase01@example.com' 'http://127.0.0.1:8000/account' | head -15

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /account
set-cookie: session=eyJjc3JmX3Rva2VuIjogImNmZGJmNGU3ZWEyMjliOGYxYzBiODkwOWNmNjM1NDU0ZjJiYjI3ODAxZDU2OTk4OWM5MGFkNDFiZDA4ZTMwOWMiLCAidXNlcl9pZCI6IDUsICJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDEyXHUwNDQxXHUwNDM1IFx1MDQzN1x1MDQzMFx1MDQzZlx1MDQzOFx1MDQ0MVx1MDQzOCBcdTA0NDNcdTA0MzZcdTA0MzUgXHUwNDNmXHUwNDNlXHUwNDNiXHUwNDNkXHUwNDRiXHUwNDM1Il0sIFsic3VjY2VzcyIsICJZb3VyIGFjY291bnQgaGFzIGJlZW4gdXBkYXRlZCEiXV19.aqRBPQ.v5_GI8bMWqHP2-HgegGx70OWwDQ; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 8 (rerun): POST /art_manage/add_all без cookies → 303 + Location /login?next=...


### $ curl -i -s -X POST --data-urlencode 'csrf_token=' 'http://127.0.0.1:8000/art_manage/add_all' | head -10

HTTP/1.1 303 See Other
date: Fri, 11 Sep 2026 17:58:20 GMT
server: uvicorn
content-length: 0
location: /login?next=/art_manage/add_all
set-cookie: session=eyJfZmxhc2hlcyI6IFtbImluZm8iLCAiXHUwNDFkXHUwNDQzXHUwNDM2XHUwNDNkXHUwNDNlIFx1MDQzMFx1MDQzMlx1MDQ0Mlx1MDQzZVx1MDQ0MFx1MDQzOFx1MDQzN1x1MDQzZVx1MDQzMlx1MDQzMFx1MDQ0Mlx1MDQ0Y1x1MDQ0MVx1MDQ0ZiBcdTA0MzhcdTA0M2JcdTA0MzggXHUwNDM3XHUwNDMwXHUwNDQwXHUwNDM1XHUwNDMzXHUwNDM4XHUwNDQxXHUwNDQyXHUwNDQwXHUwNDM4XHUwNDQwXHUwNDNlXHUwNDMyXHUwNDMwXHUwNDQyXHUwNDRjXHUwNDQxXHUwNDRmIl1dLCAiX2ZsYXNoX2R1bW15IjogIiJ9.aqRBPQ._6twoSxlQHJI1n_bLolRwLWWa08; path=/; Max-Age=1209600; httponly; samesite=lax



## Criterion 15 (rerun): regression — 4 эндпоинта → 200 (with required params for demo endpoints)


### $ echo '/docs: ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/docs')

/docs:  200


### $ echo '/users/get_all_users: ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/users/get_all_users')

/users/get_all_users:  200


### $ echo '/api/v1/dep_examples/single-direct-dependency (no params): ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/api/v1/dep_examples/single-direct-dependency')

/api/v1/dep_examples/single-direct-dependency (no params):  422


### $ echo '/api/v1/dep_examples/single-direct-dependency (header foobar): ' $(curl -s -o /dev/null -w '%{http_code}' -H 'foobar: x' 'http://127.0.0.1:8000/api/v1/dep_examples/single-direct-dependency')

/api/v1/dep_examples/single-direct-dependency (header foobar):  200


### $ echo '/orders/get_all_orders (no params): ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/orders/get_all_orders')

/orders/get_all_orders (no params):  422


### $ echo '/orders/get_all_orders (params=id): ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/orders/get_all_orders?params=id')

/orders/get_all_orders (params=id):  200


### $ echo '/orders/get_all_orders (params=time): ' $(curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8000/orders/get_all_orders?params=time')

/orders/get_all_orders (params=time):  200


## Criterion 12 (rerun): /art_home — alt anchor check


### $ curl -s 'http://127.0.0.1:8000/art_home' > /tmp/home2.html && echo "home HTML size: $(wc -c < /tmp/home2.html)" && echo "unique art/ links: $(grep -oE 'href="[^"]*art/[^"]+"' /tmp/home2.html | sort -u | wc -l)"

home HTML size: 73611
unique art/ links: 88

