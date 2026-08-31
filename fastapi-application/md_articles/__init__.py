# ==============================================================================
# +++++++++++++++++++++++++++++ md_articles пакет ++++++++++++++++++++++++++++++
# ------------------ блог на FastAPI + Jinja2 (порт flask-blog-1) ---------------
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import HTMLResponse

from base_dir_path import BASE_DIR
from core.config import settings
from config_log import logF

from md_articles.routes_main import router_main
from md_articles.routes_users import router_users
from md_articles.routes_articles import router_articles
from md_articles.web_utils import (
    get_current_user,
    templates,
)
from db_core.db_async import db_manager


# ==============================================================================
# ++++++++++++++++++++++++++ current_user middleware +++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
async def inject_current_user_middleware(request: Request, call_next):
    """Middleware: загружает current_user для всех HTTP-запросов в блоге."""
    async with db_manager.session_factory() as session:
        await get_current_user(request, session)
        response = await call_next(request)
    return response


# ==============================================================================
# +++++++++++++++++++++++++++++++ register app +++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def register_md_articles(app: FastAPI) -> None:
    """Подключение блога к приложению: сессии, статика, ошибки, роутеры."""
    logF.info("register_md_articles: подключение middleware, static, errors, routers")

    app.middleware("http")(inject_current_user_middleware)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.web.secret_key,
        max_age=14 * 24 * 3600,
    )

    app.mount(
        "/static",
        StaticFiles(directory=BASE_DIR / "static", check_dir=False),
        name="static",
    )

    _register_error_handlers(app)

    app.include_router(router_main)
    app.include_router(router_users)
    app.include_router(router_articles)


# ==============================================================================
# ++++++++++++++++++++++++++++++ error handlers ++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def _register_error_handlers(app: FastAPI) -> None:
    """HTML-шаблоны ошибок вместо JSON по умолчанию."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        status_code = exc.status_code
        location = exc.headers.get("location") if exc.headers else None
        if status_code in (301, 302, 303, 307, 308) and location:
            return RedirectResponse(location, status_code=status_code)
        if status_code == 403:
            return _render_error(request, "errors/403.html", 403)
        if status_code == 404:
            return _render_error(request, "errors/404.html", 404)
        if status_code >= 500:
            return _render_error(request, "errors/500.html", status_code)
        # Для прочих HTTP-исключений возвращаем стандартный ответ FastAPI
        from fastapi.exception_handlers import http_exception_handler as default_handler
        return await default_handler(request, exc)

    @app.exception_handler(403)
    async def forbidden_handler(request: Request, _exc):
        return _render_error(request, "errors/403.html", 403)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, _exc):
        return _render_error(request, "errors/404.html", 404)

    @app.exception_handler(500)
    async def server_error_handler(request: Request, _exc):
        return _render_error(request, "errors/500.html", 500)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logF.error(f"Unhandled exception: {exc}")
        return _render_error(request, "errors/500.html", 500)


def _render_error(request: Request, template_name: str, status_code: int) -> HTMLResponse:
    from md_articles.web_utils import render_template

    return render_template(
        template_name,
        {"request": request, "title": f"{status_code}"},
        status_code=status_code,
    )
