from uuid import UUID

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy import JWTStrategy

from app.core.config import settings
from app.models.user import User, get_user_manager

# Cookie transport for web-based authentication.
# Все параметры читаются из Settings (app/core/config.py) — единая точка
# истины для cookie-контракта.
cookie_transport = CookieTransport(
    cookie_name=settings.AUTH_COOKIE_NAME,
    cookie_max_age=settings.AUTH_COOKIE_MAX_AGE,
    cookie_secure=settings.AUTH_COOKIE_SECURE,
    cookie_samesite=settings.AUTH_COOKIE_SAMESITE,
)


def get_jwt_strategy() -> JWTStrategy:
    """JWT-стратегия с временем жизни, синхронизированным с cookie max_age."""
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.AUTH_COOKIE_MAX_AGE,
    )


def get_logout_cookie_value() -> str:
    """Заголовок Set-Cookie для logout: обнуляет cookie, опираясь на те же
    настройки, что и CookieTransport. Используется в /auth/logout (фаза 5)
    и в любом другом месте, где нужно явно сбросить сессионную cookie.
    """
    parts = [
        f"{settings.AUTH_COOKIE_NAME}=",
        "Path=/",
        "Max-Age=0",
        f"SameSite={settings.AUTH_COOKIE_SAMESITE.capitalize()}",
        "HttpOnly",
    ]
    if settings.AUTH_COOKIE_SECURE:
        parts.append("Secure")
    return "; ".join(parts)


# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
