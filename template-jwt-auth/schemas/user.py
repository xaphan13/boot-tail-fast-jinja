from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field


class UserRead(schemas.BaseUser[UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UserEmailUpdate(BaseModel):
    """Схема смены email. Требует повторной проверки текущего пароля,
    чтобы исключить захват аккаунта через украденную активную сессию."""

    current_password: str = Field(..., min_length=1)
    email: EmailStr


class UserPasswordUpdate(BaseModel):
    """Схема смены пароля. Проверяет совпадение нового пароля
    с подтверждением на уровне приложения (после `model_validate`)."""

    current_password: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    confirm_password: str = Field(..., min_length=1)
