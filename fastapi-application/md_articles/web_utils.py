# ==============================================================================
# +++++++++++++++++++++++++++++++ Web utilities ++++++++++++++++++++++++++++++++
# ------------------- сессии, Jinja, CSRF, current_user, flash -----------------
# ------------------------------------------------------------------------------
import secrets
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from base_dir_path import BASE_DIR
from config_log import logF
from core.users import fastapi_users
from md_articles.models import BlogUser
from md_articles.schema_art import list_sections


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
        "sidebar_sections": list_sections(),
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
    user: BlogUser | None = Depends(fastapi_users.current_user(optional=True)),
) -> BlogUser | None:
    """Получить пользователя из JWT-cookie и положить в request.state."""
    request.state.current_user = user
    return user


def _get_current_user_from_request(request: Request) -> BlogUser | None:
    return getattr(request.state, "current_user", None)


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
async def require_login(
    request: Request,
    user: BlogUser | None = Depends(get_current_user),
) -> BlogUser:
    """Dependency: аноним -> flash + redirect на /login?next=<path>."""
    if user is None:
        flash(request, "Нужно авторизоваться или зарегистрироваться", "info")
        next_url = quote(request.url.path, safe="/")
        response = RedirectResponse(f"/login?next={next_url}", status_code=303)
        request.session.setdefault("_flash_dummy", "")
        raise HTTPException(status_code=303, headers={"location": response.headers["location"]})
    return user


# ==============================================================================
# +++++++++++++++++++++++++++++ password helpers +++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
