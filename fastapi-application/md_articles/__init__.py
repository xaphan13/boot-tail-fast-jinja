# ==============================================================================
# +++++++++++++++++++++++++++++ md_articles пакет ++++++++++++++++++++++++++++++
# ------------------ блог на FastAPI + Jinja2 (порт flask-blog-1) ---------------
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

from base_dir_path import BASE_DIR
from config_log import logF
from core.config import settings
from db_core import Base as _DbBase


# ==============================================================================
# ++++++++++++++++++++++++++ current_user middleware +++++++++++++++++++++++++++
# ------------------------------------------------------------------------------


# ==============================================================================
# +++++++++++++++++++++++++++++++ register app +++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def register_md_articles(app: FastAPI) -> None:
    """Подключение блога: сессии, auth API, статика, ошибки и роутеры."""
    logF.info("register_md_articles: подключение middleware, static, errors, routers")

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

    from core.users import auth_backend, fastapi_users
    from md_articles.routes_articles import router_articles
    from md_articles.routes_main import router_main
    from md_articles.routes_users import router_users
    from md_articles.schema_users import UserRead, UserUpdate

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/cookie",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/auth/users",
        tags=["auth users"],
    )
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
