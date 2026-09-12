from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.password import PasswordHelper
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.templates import templates
from app.core.users import fastapi_users
from app.models.user import User, UserManager, get_user_manager
from app.schemas.user import (
    UserEmailUpdate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)

router = APIRouter()


# Custom profile page endpoint
@router.get("/profile", response_class=HTMLResponse, name="user_profile")
async def get_profile_page(
    request: Request,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Get user profile page with full user data including items."""

    # Load user with items for statistics
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user.id),  # type: ignore[arg-type]
    )
    user_with_items = result.scalar_one()

    return templates.TemplateResponse(
        request,
        "profile.jinja2",
        {"user": user_with_items},
    )


# Profile update endpoints
@router.patch("/profile/email", response_class=HTMLResponse, name="update_user_email")
async def update_email(
    request: Request,
    payload: Annotated[UserEmailUpdate, Form()],
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Update user email. Принимает form-data и валидирует через
    `UserEmailUpdate`; битый email отдаёт 422 на этапе Pydantic (Form-парсинг)."""

    password_helper = PasswordHelper()
    is_valid, _ = password_helper.verify_and_update(
        payload.current_password,
        user.hashed_password,
    )
    if not is_valid:
        return templates.TemplateResponse(
            request,
            "partials/_form_message.jinja2",
            {"message": "Current password is incorrect", "kind": "error"},
            status_code=400,
        )

    existing_user = await db.execute(
        select(User).where(
            and_(User.email == payload.email, User.id != user.id),  # type: ignore[arg-type]
        ),
    )
    if existing_user.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "partials/_form_message.jinja2",
            {"message": "Email already registered", "kind": "error"},
            status_code=400,
        )

    user.email = payload.email
    await db.commit()

    return templates.TemplateResponse(
        request,
        "partials/_email_display.jinja2",
        {"user": user},
        status_code=200,
    )


@router.patch(
    "/profile/password",
    response_class=HTMLResponse,
    name="update_user_password",
)
async def update_password(
    request: Request,
    payload: Annotated[UserPasswordUpdate, Form()],
    user: User = Depends(fastapi_users.current_user(active=True)),
    user_manager: UserManager = Depends(get_user_manager),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Update user password. Принимает form-data, валидирует через
    `UserPasswordUpdate`; сначала проверяет текущий пароль, потом —
    совпадение нового с подтверждением, потом — серверную политику."""

    if payload.password != payload.confirm_password:
        return templates.TemplateResponse(
            request,
            "partials/_form_message.jinja2",
            {"message": "Passwords do not match", "kind": "error"},
            status_code=400,
        )

    password_helper = PasswordHelper()
    is_valid, _ = password_helper.verify_and_update(
        payload.current_password,
        user.hashed_password,
    )
    if not is_valid:
        return templates.TemplateResponse(
            request,
            "partials/_form_message.jinja2",
            {"message": "Current password is incorrect", "kind": "error"},
            status_code=400,
        )

    try:
        await user_manager.validate_password(payload.password, user)
    except InvalidPasswordException as e:
        return templates.TemplateResponse(
            request,
            "partials/_form_message.jinja2",
            {"message": f"Password validation failed: {e.reason}", "kind": "error"},
            status_code=400,
        )

    user.hashed_password = password_helper.hash(payload.password)
    await db.commit()

    return templates.TemplateResponse(
        request,
        "partials/_form_message.jinja2",
        {"message": "Password updated successfully", "kind": "success"},
        status_code=200,
    )


# Include the original FastAPI Users routes for API access
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
