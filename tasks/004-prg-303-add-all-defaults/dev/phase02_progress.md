# Phase 02 progress — 307 → 303 synchronization

## Task
Replace all `status_code=307` with `status_code=303` in three files:
- `fastapi-application/md_articles/routes_users.py`
- `fastapi-application/md_articles/web_utils.py`
- `fastapi-application/md_articles/routes_main.py`

## Step 0 — preconditions
- uvicorn already running on 127.0.0.1:8000 (from phase 1)
- pre-check curl OK

## Step 1 — initial grep
Full list of `status_code=307` occurrences (12 total):

```
fastapi-application/md_articles/routes_users.py:167:        return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:190:        return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:213:    return RedirectResponse("/login", status_code=307)
fastapi-application/md_articles/routes_users.py:288:        return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:310:        return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:327:            return RedirectResponse(next_page, status_code=307)
fastapi-application/md_articles/routes_users.py:328:        return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:373:    return RedirectResponse("/art_home", status_code=307)
fastapi-application/md_articles/routes_users.py:429:    return RedirectResponse("/account", status_code=307)
fastapi-application/md_articles/web_utils.py:146:        response = RedirectResponse(f"/login?next={next_url}", status_code=307)
fastapi-application/md_articles/web_utils.py:148:        raise HTTPException(status_code=307, headers={"location": response.headers["location"]})
fastapi-application/md_articles/routes_main.py:23:    return RedirectResponse("/art_home", status_code=307)
```

Per-file count: routes_users.py=9, web_utils.py=2, routes_main.py=1. Total=12.

Plan: `replace_all` on `status_code=307` → `status_code=303` for each of the three files
(handles both RedirectResponse and the HTTPException in web_utils.py).

## Step 2 — edits applied
- routes_users.py: replace_all done
- web_utils.py: replace_all done (covers line 146 RedirectResponse + line 148 HTTPException)
- routes_main.py: replace_all done

## Step 3 — checkpoints

### 3.1 grep — `status_code=307` in target files
```
$ grep -rn "status_code=307" fastapi-application/md_articles/routes_users.py \
    fastapi-application/md_articles/web_utils.py \
    fastapi-application/md_articles/routes_main.py
(empty, exit 1)
```
PASS

### 3.2 ruff check — three files
```
$ .venv/bin/ruff check fastapi-application/md_articles/routes_users.py \
    fastapi-application/md_articles/web_utils.py \
    fastapi-application/md_articles/routes_main.py
All checks passed!
```
PASS

### 3.3 route count
```
$ cd fastapi-application && ../.venv/bin/python -c "from main import main_app; print(len(main_app.routes))"
43
```
PASS (matches phase-1 baseline 43; status_code changes don't touch route table)

### 3.4 curl scenarios
uvicorn was started without `--reload`, so old process was killed and a fresh
one was launched against the new code (pid 388728) — kept running for qa.

```
POST /register (new user phase02_user@example.com / Pass1234)
  → HTTP 303 | Location: http://127.0.0.1:8000/login

POST /login (phase02_user@example.com / Pass1234)
  → HTTP 303 | Location: http://127.0.0.1:8000/art_home

POST /account (phase01_user session, no field changes)
  → HTTP 303 | Location: http://127.0.0.1:8000/account

POST /art_manage/add_all (no cookies — require_login kicks in)
  → HTTP 303 | Location: http://127.0.0.1:8000/login?next=/art_manage/add_all
  (raw Location header: /login?next=/art_manage/add_all — pre-existing
   quote(request.url.path, safe="/") leaves slashes unencoded; outside this contract)

GET /
  → HTTP 303 | Location: http://127.0.0.1:8000/art_home
```
PASS — all five redirect endpoints return HTTP 303 See Other.

## Step 4 — server state
- uvicorn pid 388728 still running on 127.0.0.1:8000
- ready for qa/adversary

