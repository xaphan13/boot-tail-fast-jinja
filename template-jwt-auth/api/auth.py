import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists
from pydantic import ValidationError

from app.api.dependencies import is_htmx
from app.core.templates import templates
from app.core.users import fastapi_users, get_logout_cookie_value
from app.models.user import User, UserManager, get_user_manager
from app.schemas.user import UserCreate

router: APIRouter = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse, name="auth_login_page")
async def get_login_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url=request.url_for("index"), status_code=302)

    return templates.TemplateResponse(request, "auth/login.jinja2")


@router.get("/register", response_class=HTMLResponse, name="auth_register_page")
async def get_register_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url=request.url_for("index"), status_code=302)

    return templates.TemplateResponse(request, "auth/register.jinja2")


@router.post("/register", name="auth_register")
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    user_manager: UserManager = Depends(get_user_manager),
) -> Response:
    """Custom registration endpoint that redirects to login after success."""
    try:
        # Create the user
        user_create = UserCreate(email=email, password=password)
        user = await user_manager.create(user_create, safe=True, request=request)
        logger.info("User %s registered successfully, redirecting to login", user.email)

        # Check if this is an HTMX request
        if is_htmx(request):
            # For HTMX requests, return an HX-Redirect header
            login_url = str(request.url_for("auth_login_page")) + "?registered=true"
            return Response(
                content="",
                status_code=200,
                headers={"HX-Redirect": login_url},
            )
        else:
            # For regular requests, return a standard redirect
            login_url = str(request.url_for("auth_login_page")) + "?registered=true"
            return RedirectResponse(url=login_url, status_code=302)

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "REGISTER_USER_ALREADY_EXISTS",
                "reason": "User with this email already exists",
            },
        ) from e
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=400,
            detail={"code": "REGISTER_INVALID_PASSWORD", "reason": e.reason},
        ) from e


@router.post("/logout", name="auth_logout")
async def logout_user(
    request: Request,
    user: User = Depends(fastapi_users.current_user()),
) -> Response:
    """Handle logout by making a request to the FastAPI Users logout endpoint."""
    logger.info("User %s logging out", user.email)

    # Clear the session cookie via the single source of truth
    # (app/core/users.py:get_logout_cookie_value). Используется и в HTMX,
    # и в обычной ветке, чтобы контракт clear-cookie жил в одном месте.
    set_cookie_header = get_logout_cookie_value()

    if is_htmx(request):
        # For HTMX requests, return HX-Redirect + Set-Cookie (clear).
        return Response(
            content="",
            status_code=200,
            headers={
                "HX-Redirect": str(request.url_for("index")),
                "Set-Cookie": set_cookie_header,
            },
        )

    # For regular requests, clear the cookie and redirect to home.
    response = RedirectResponse(url=request.url_for("index"), status_code=302)
    response.headers["Set-Cookie"] = set_cookie_header
    return response
