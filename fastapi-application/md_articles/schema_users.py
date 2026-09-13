from fastapi_users import schemas
from pydantic import EmailStr, Field


class UserRead(schemas.BaseUser[int]):
    """Публичное представление BlogUser без пароля и его хеша."""

    username: str
    image_file: str


class UserCreate(schemas.BaseUserCreate):
    """Данные регистрации; privileged flags отбрасываются при safe=True."""

    username: str = Field(min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(min_length=1)
    image_file: str = Field(default="default.jpg", min_length=1, max_length=20)


class UserUpdate(schemas.BaseUserUpdate):
    """Разрешённые поля обновления пользователя без hashed_password наружу."""

    username: str | None = Field(default=None, min_length=1, max_length=20)
    image_file: str | None = Field(default=None, min_length=1, max_length=20)
