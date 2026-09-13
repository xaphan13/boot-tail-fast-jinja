from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy import JWTStrategy

from core.config import settings
from md_articles.models import BlogUser as User

try:
    from md_articles.models import get_user_manager
except ImportError:

    async def get_user_manager() -> AsyncGenerator[None, None]:
        """Временная dependency-заглушка до подключения manager в фазе 2."""
        raise RuntimeError("The BlogUser manager is not configured yet")
        yield


cookie_transport = CookieTransport(
    cookie_name=settings.auth.cookie_name,
    cookie_max_age=settings.auth.cookie_max_age,
    cookie_secure=settings.auth.cookie_secure,
    cookie_samesite=settings.auth.cookie_samesite,
)


def get_jwt_strategy() -> JWTStrategy:
    """Создать JWT-стратегию с TTL, совпадающим с TTL auth-cookie."""
    return JWTStrategy(
        secret=settings.auth.secret_key,
        lifetime_seconds=settings.auth.cookie_max_age,
    )


def get_logout_cookie_value() -> str:
    """Вернуть Set-Cookie значение для немедленного удаления auth-cookie."""
    parts = [
        f"{settings.auth.cookie_name}=",
        "Path=/",
        "Max-Age=0",
        f"SameSite={settings.auth.cookie_samesite.capitalize()}",
        "HttpOnly",
    ]
    if settings.auth.cookie_secure:
        parts.append("Secure")
    return "; ".join(parts)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

# Явный DI-символ оставляет wiring совместимым с последующими роутерами.
get_user_manager_dependency = Depends(get_user_manager)
