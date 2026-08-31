# ==============================================================================
# +++++++++++++++++++++++++++++++ Web utilities ++++++++++++++++++++++++++++++++
# ------------------- сессии, Jinja, CSRF, current_user, flash -----------------
# ------------------------------------------------------------------------------
import secrets
from typing import Annotated
from urllib.parse import quote

import bcrypt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base_dir_path import BASE_DIR
from config_log import logF
from db_core.db_async import CurrentSession
from md_articles.models import BlogUser


# ==============================================================================
# +++++++++++++++++++++++++++++ Jinja2Templates ++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ==============================================================================
# +++++++++++++++++++++++++++++++ context/globals ++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def _inject_globals(request: Request):
    """Возвращает глобальный контекст для всех шаблонов."""
    return {
        "current_user": _get_current_user_from_request(request),
        "csrf_token": _ensure_csrf_token(request),
        "get_flashed_messages": _FlashMessagesHelper(request),
    }


class _FlashMessagesHelper:
    """Callable-обёртка для get_flashed_messages(with_categories=...)."""

    def __init__(self, request: Request) -> None:
        self.request = request

    def __call__(self, with_categories: bool = False):
        flashes = _get_flashes(self.request)
        if with_categories:
            return flashes
        return [msg for _category, msg in flashes]


def _render_with_globals(template_name: str, context: dict, **kwargs):
    """Рендер шаблона с автоматически добавляемыми глобалами."""
    request = context["request"]
    context.update(_inject_globals(request))
    return templates.TemplateResponse(template_name, context, **kwargs)


render_template = _render_with_globals


# ==============================================================================
# +++++++++++++++++++++++++++ current_user dependency ++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
async def get_current_user(
    request: Request,
    session: CurrentSession,
) -> BlogUser | None:
    """Получить пользователя из сессии и положить в request.state."""
    user = await _load_current_user(request, session)
    request.state.current_user = user
    return user


async def _load_current_user(
    request: Request,
    session: CurrentSession,
) -> BlogUser | None:
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    result = await session.execute(select(BlogUser).where(BlogUser.id == user_id))
    return result.scalar_one_or_none()


def _get_current_user_from_request(request: Request) -> BlogUser | None:
    return getattr(request.state, "current_user", None)


# ==============================================================================
# +++++++++++++++++++++++++++++ auth helpers +++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def login_user(request: Request, user_id: int) -> None:
    request.session["user_id"] = user_id


def logout_user(request: Request) -> None:
    request.session.pop("user_id", None)


# ==============================================================================
# +++++++++++++++++++++++++++++ flash messages +++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def flash(request: Request, message: str, category: str = "message") -> None:
    """Добавить flash-сообщение в сессию (Flask-совместимая сигнатура)."""
    flashes = request.session.get("_flashes", [])
    flashes.append((category, message))
    request.session["_flashes"] = flashes


def _get_flashes(request: Request) -> list[tuple[str, str]]:
    """Прочитать и очистить flash-сообщения из сессии."""
    flashes = request.session.pop("_flashes", [])
    return list(flashes)


def _ensure_csrf_token(request: Request) -> str:
    """Вернуть существующий CSRF-токен или создать новый в сессии."""
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_hex(32)
        request.session["csrf_token"] = token
    return token


async def validate_csrf(request: Request) -> None:
    """Dependency для POST-роутов: проверяет csrf_token формы."""
    form = await request.form()
    session_token = request.session.get("csrf_token")
    form_token = form.get("csrf_token")
    if not session_token or not form_token or form_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")


# ==============================================================================
# +++++++++++++++++++++++++++++ login guard ++++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
async def require_login(request: Request) -> None:
    """Dependency: аноним -> flash + redirect на /login?next=<path>."""
    if getattr(request.state, "current_user", None) is None:
        flash(request, "Нужно авторизоваться или зарегистрироваться", "info")
        next_url = quote(request.url.path, safe="/")
        response = RedirectResponse(f"/login?next={next_url}", status_code=307)
        request.session.setdefault("_flash_dummy", "")
        raise HTTPException(status_code=307, headers={"location": response.headers["location"]})


# ==============================================================================
# +++++++++++++++++++++++++++++ password helpers +++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
