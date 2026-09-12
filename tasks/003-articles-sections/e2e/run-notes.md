# QA run notes — mass article registry / sections — 2026-09-11T14:55:28Z

server: 350397 /home/max/0_0_26_new_one/boot-tail-fast-jinja/.venv/bin/python ../.venv/bin/uvicorn main:main_app --host 127.0.0.1 --port 8000 350491 bash -c cd /home/max/0_0_26_new_one/boot-tail-fast-jinja/fastapi-application N=../tasks/current/e2e/run-notes.md { echo "# QA run notes — mass article registry / sections — $(date -u '+%Y-%m-%dT%H:%M:%SZ')" echo echo "server: $(pgrep -af 'uvicorn.*main:main_app' | tr '\n' ' ')" echo echo '## C1 scan_content_art (expect >=75, True)' ../.venv/bin/python -c "from md_articles.schema_art import scan_content_art; f=scan_content_art(); print(len(f)); print(all('/' in x for x in f))" echo echo '## C2 get_section (expect AI инструменты, empty repr)' ../.venv/bin/python -c "from md_articles.schema_art import get_section; print(get_section('AI инструменты/a.md')); print(repr(get_section('a.md')))" echo echo '## C3 list_sections (expect 10 names)' ../.venv/bin/python -c "from md_articles.schema_art import list_sections; print(list_sections())" echo echo '## C4 routes (expect 44, True, True)' ../.venv/bin/python -c "from main import main_app; rs=[r.path for r in main_app.routes]; print(len(rs)); print('/art_manage/prune_missing' in rs); print('/art_section/{section}' in rs)" } > "$N" 2>&1 cat "$N" 350493 bash -c cd /home/max/0_0_26_new_one/boot-tail-fast-jinja/fastapi-application N=../tasks/current/e2e/run-notes.md { echo "# QA run notes — mass article registry / sections — $(date -u '+%Y-%m-%dT%H:%M:%SZ')" echo echo "server: $(pgrep -af 'uvicorn.*main:main_app' | tr '\n' ' ')" echo echo '## C1 scan_content_art (expect >=75, True)' ../.venv/bin/python -c "from md_articles.schema_art import scan_content_art; f=scan_content_art(); print(len(f)); print(all('/' in x for x in f))" echo echo '## C2 get_section (expect AI инструменты, empty repr)' ../.venv/bin/python -c "from md_articles.schema_art import get_section; print(get_section('AI инструменты/a.md')); print(repr(get_section('a.md')))" echo echo '## C3 list_sections (expect 10 names)' ../.venv/bin/python -c "from md_articles.schema_art import list_sections; print(list_sections())" echo echo '## C4 routes (expect 44, True, True)' ../.venv/bin/python -c "from main import main_app; rs=[r.path for r in main_app.routes]; print(len(rs)); print('/art_manage/prune_missing' in rs); print('/art_section/{section}' in rs)" } > "$N" 2>&1 cat "$N" 

## C1 scan_content_art (expect >=75, True)
80
True

## C2 get_section (expect AI инструменты, empty repr)
AI инструменты
''

## C3 list_sections (expect 10 names)
['AI инструменты', 'Fast API', 'Guide FastAPI', 'Guide MCP Python', 'Guide my fastApi', 'Jinja Templates', 'Pydantic Python', 'Python', 'Rust', 'Sql Alchemy']

## C4 routes (expect 44, True, True)
44
True
True

## C5 /about grep art_section (expect >=10)
10

## C5b first art_section href from /about -> curl it (expect 200)
href: http://127.0.0.1:8000/art_section/AI инструменты
000

## C6 /art_section/Python (expect 200, grep 01_project_structure >=1)
200
1

## C7 /art_section/NoSuchSection (expect 404)
404

## C8 POST /art_manage/add_all no login (expect 307)
307

## C9 POST /art_manage/prune_missing no login (expect 307)
307

## C11 regression (expect all 200)
/art_home -> 200
/docs -> 200
/users/get_all_users -> 200
/orders/get_all_orders -> 422
/api/v1/dep_examples/single-direct-dependency -> 422

## C5b (rerun) sidebar links from /about, percent-encoded (expect 200)
-- href attrs containing art_section:
http://127.0.0.1:8000/art_section/AI инструменты
http://127.0.0.1:8000/art_section/Fast API
http://127.0.0.1:8000/art_section/Guide FastAPI
http://127.0.0.1:8000/art_section/Guide MCP Python
http://127.0.0.1:8000/art_section/Guide my fastApi
http://127.0.0.1:8000/art_section/Jinja Templates
http://127.0.0.1:8000/art_section/Pydantic Python
http://127.0.0.1:8000/art_section/Python
http://127.0.0.1:8000/art_section/Rust
http://127.0.0.1:8000/art_section/Sql Alchemy
-- count of literal %20 in html: 0
-- per-link status:
/art_section/AI инструменты -> 200
/art_section/Fast API -> 200
/art_section/Guide FastAPI -> 200
/art_section/Guide MCP Python -> 200
/art_section/Guide my fastApi -> 200
/art_section/Jinja Templates -> 200
/art_section/Pydantic Python -> 200
/art_section/Python -> 200
/art_section/Rust -> 200
/art_section/Sql Alchemy -> 200

## C11 follow-up: 422 causes — required params from openapi.json
/orders/get_all_orders get params: [('params', 'query', True)]
/api/v1/dep_examples/single-direct-dependency get params: [('foobar', 'header', True)]

## working tree scope
 M fastapi-application/md_articles/routes_articles.py
 M fastapi-application/md_articles/schema_art.py
 M fastapi-application/md_articles/web_utils.py
 M fastapi-application/templates/includes/_sidebar.html
 M fastapi-application/templates/new_art/art_home.html
 M fastapi-application/templates/new_art/art_manage.html
 M tasks/current/REQUIREMENTS.md
 D tasks/current/dev/phase01-03_progress.md
 M tasks/current/dev/phase01_progress.md
 D tasks/current/dev/phase02_progress.md
 D tasks/current/dev/phase03_progress.md
 D tasks/current/dev/phase04_progress.md
 D tasks/current/dev/phase05_progress.md
 D tasks/current/dev/phase06_progress.md
 D tasks/current/dev/phase07_progress.md
 M tasks/current/e2e/run-notes.md
?? tasks/002-tailwind-cdn-4-themes/
?? tasks/current/dev/phase01_scan.txt
0bb2781 update docs and models agents

## C12 ruff (from project root, expect clean)
All checks passed!
ruff exit: 0

## C11 (recheck) same endpoints WITH required params (expect 200)
/orders/get_all_orders?params=x -> 422
/api/v1/dep_examples/single-direct-dependency (header foobar) -> 200

## register/login/art_manage templates: csrf + form fields
-- register.html form/csrf/input lines:
9:      <form method="POST" action="">
11:        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
20:        <button type="submit"
-- login.html form/csrf/input lines:
9:      <form method="POST" action="">
11:        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
19:          <input id="remember" name="remember" type="checkbox"
24:        <button type="submit"
-- art_manage.html prune form + csrf lines:
40:                  <form method="POST" action="{{ url_for('art_main.art_manage_meta') }}" class="grid grid-cols-1 md:grid-cols-12 gap-2">
41:                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
42:                    <input type="hidden" name="file_name" value="{{ art.file_name }}">
44:                      <input type="text" name="title" value="{{ art.title }}"
49:                      <input type="text" name="author" value="{{ art.author }}"
54:                      <input type="text" name="lang" value="{{ art.lang }}"
91:      <form method="POST" action="{{ url_for('art_main.art_manage_add_all') }}" class="mb-5">
92:        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
100:            <form method="POST" action="{{ url_for('art_main.art_manage_meta') }}" class="grid grid-cols-1 md:grid-cols-12 gap-2">
101:              <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
102:              <input type="hidden" name="file_name" value="{{ file_name }}">
104:                <input type="text" name="title" value=""
109:                <input type="text" name="author" value=""
114:                <input type="text" name="lang" value=""
138:      <form method="POST" action="{{ url_for('art_main.art_manage_prune_missing') }}" class="mb-5">
139:        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">

## C10 admin session: register/login -> CSRF -> prune_missing
register csrf len: 64
register POST: 307
login csrf len: 64
login POST: 307
art_manage GET: 200
prune form in art_manage: 0
art_manage csrf len: 64
prune POST: 307
-- orphan entries after prune (expect []):
[]

## C11 follow-up 2: /orders/get_all_orders signature
grep: router_order_one.py: Нет такого файла или каталога
grep: router_order_one.py: Нет такого файла или каталога

## C11 follow-up 3: /orders/get_all_orders actual signature + param formats
-- router file:
__init__.py
model_order_product.py
__pycache__
router_order_one.py
schema_order_product.py
-- signature:
38:@r_order_one.post("/add_order", response_model=OrderResp)
49:@r_order_one.post("/insert_order", response_model=OrderCreateBody)
62:@r_order_one.get("/get_order_filter_by", response_model=OrderResp)
63:async def get_order_filter_by(db: CurrentSession, params: OrderGetQuery = Depends()):
65:    filter_where = {key: value for key, value in params.model_dump().items() if value is not None}
81:@r_order_one.get("/get_order_where", response_model=OrderResp | list[OrderResp])
82:async def get_order_where(db: CurrentSession, params: OrderGetQuery = Depends()):
85:        getattr(Order, key) == value for key, value in params.model_dump(exclude_none=True).items()
107:@r_order_one.get("/get_all_orders", response_model=list[OrderResp])
108:async def get_all_orders(db: CurrentSession, params: OrderGetAllOrderbyQuery):
109:    if params == "time":
111:    elif params == "promocode":
129:@r_order_one.get("/get_all_join", response_model=list[OrderRespWithProducts])
-- try param formats:
GET /orders/get_all_orders?params=x -> 422
GET /orders/get_all_orders?params=1 -> 422
GET /orders/get_all_orders?params=a&params=b -> 422
GET /orders/get_all_orders?params= -> 422
GET /orders/get_all_orders (no params) -> 422
-- body of 200 case (if any):
{"detail":[{"type":"enum","loc":["query","params"],"msg":"Input should be 'id', 'time' or 'promocode'","input":"","ctx":{"expected":"'id', 'time' or 'promocode'"}}]}

## C11 final: same endpoints WITH required params (expect 200)
/orders/get_all_orders?params=id -> 200
/orders/get_all_orders?params=time -> 200
/api/v1/dep_examples/single-direct-dependency (header foobar) -> 200

## registry counters (registered / on disk / unassigned)
80 80 0

## C10 hardening
-- registry file unchanged vs pre-run backup:
identical
-- art_manage page markers (prune section heading / prune link):
heading hits: 1
prune_missing hits: 0
-- CSRF negative: prune with bogus token (expect rejection, not 307):
403
-- prune with valid session+CSRF, then GET /art_manage flash text:
prune POST: 307
Записей без файла нет

## articles.yaml head (format reference)
articles:
- author: NoName
  lang: AI инструменты
  art_id: 1788345978
  title: aion-zcode-1
  file_name: AI инструменты/aion-zcode-1.md
  section: AI инструменты
- author: NoName
  lang: AI инструменты
  art_id: 1788345979
  title: anion-gemini
  file_name: AI инструменты/anion-gemini.md
  section: AI инструменты
- author: NoName
  lang: AI инструменты
  art_id: 1788345980
  title: anion-gpt-1
  file_name: AI инструменты/anion-gpt-1.md
  section: AI инструменты
- author: NoName

## app log: Traceback/ERROR lines during run
18:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
25:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
32:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
(end log grep)

## log files listing
итого 272
drwxrwxr-x  2 max max   4096 авг 31 15:33 .
drwxrwxr-x 14 max max   4096 сен 11 17:57 ..
-rw-rw-r--  1 max max 264356 сен 11 17:59 one_fast.log

## per-log error/traceback lines (with filename)
--- fastapi-application/log/one_fast.log ---
18:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
25:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
32:ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user

## log head (context for first errors)
--- fastapi-application/log/one_fast.log (head 45) ---
/* 2026-08-31 15:33:20,921 - __init__.register_md_articles(42) - [MainThread] - [130019159877440] */  
INFO: register_md_articles: подключение middleware, static, errors, routers
/* 2026-08-31 15:33:20,953 - main.main(31) - [MainThread] - [130019159877440] */  
INFO: Base dir path :
DIR_CWD=PosixPath('/home/max/0_0_26_new_one/boot-tail-fast-jinja/fastapi-application') 
BASE_DIR=PosixPath('/home/max/0_0_26_new_one/boot-tail-fast-jinja/fastapi-application')
/* 2026-08-31 15:33:21,854 - __init__.register_md_articles(42) - [MainThread] - [137476562298688] */  
INFO: register_md_articles: подключение middleware, static, errors, routers
/* 2026-08-31 15:33:21,966 - __init__.register_md_articles(42) - [MainThread] - [137476562298688] */  
INFO: register_md_articles: подключение middleware, static, errors, routers
/* 2026-08-31 15:33:21,996 - create_fastapi.lifespan(16) - [MainThread] - [137476562298688] */  
INFO: startup lifespan :
settings.db.url=SqliteDsn('sqlite+aiosqlite:///one_simple.db') 
app.title='Example Request Parameters Extraction'
/* 2026-08-31 15:33:21,996 - create_fastapi.lifespan(18) - [MainThread] - [137476562298688] */  
WARNING: used test sqlite dataBase : settings.db.url=SqliteDsn('sqlite+aiosqlite:///one_simple.db')
/* 2026-08-31 15:33:25,666 - __init__.generic_exception_handler(102) - [MainThread] - [137476562298688] */  
ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
[SQL: SELECT blog_user.id, blog_user.username, blog_user.email, blog_user.image_file, blog_user.password 
FROM blog_user 
WHERE blog_user.id = ?]
[parameters: (6,)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
/* 2026-08-31 15:33:25,732 - __init__.generic_exception_handler(102) - [MainThread] - [137476562298688] */  
ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
[SQL: SELECT blog_user.id, blog_user.username, blog_user.email, blog_user.image_file, blog_user.password 
FROM blog_user 
WHERE blog_user.id = ?]
[parameters: (6,)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
/* 2026-08-31 15:33:25,753 - __init__.generic_exception_handler(102) - [MainThread] - [137476562298688] */  
ERROR: Unhandled exception: (sqlite3.OperationalError) no such table: blog_user
[SQL: SELECT blog_user.id, blog_user.username, blog_user.email, blog_user.image_file, blog_user.password 
FROM blog_user 
WHERE blog_user.id = ?]
[parameters: (6,)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
/* 2026-08-31 15:33:40,012 - main.main(41) - [MainThread] - [130019159877440] */  
WARNING: end '-----------------' my-fastapi-one - main() '--------------------------' 



'********************************************************************************'
/* 2026-08-31 15:36:11,474 - __init__.register_md_articles(42) - [MainThread] - [126542982182720] */  
INFO: register_md_articles: подключение middleware, static, errors, routers

## db files present
-rw-r--r-- 1 max max 90112 сен 11 17:57 fastapi-application/one_simple.db

## tables in fastapi-application/one_simple.db
['alembic_version', 'users', 'posts', 'orders', 'products', 'order_product_association', 'blog_user', 'blog_post']

## session auth proof
GET /art_manage with cookie -> 200
GET /art_manage no cookie   -> 307

## 422 endpoints untouched by task (diff stat should be empty)
(end diff stat)
