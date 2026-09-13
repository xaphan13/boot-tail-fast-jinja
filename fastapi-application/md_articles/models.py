# ==============================================================================
# +++++++++++++++++++++++++++++++ Blog Models +++++++++++++++++++++++++++++++++
# ------------------ SQLAlchemy 2.0 стиль проекта (Mapped) ----------------------
# ------------------------------------------------------------------------------
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users.exceptions import InvalidPasswordException
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings
from db_core.db_async import CurrentSession
from db_core.model_base import Base
from db_core.type_for_models import (
    int_primary_key,
    str_len_20,
    str_len_100,
)


class BlogUser(SQLAlchemyBaseUserTable[int], Base):
    """Пользователь блога с целочисленным ID и полями fastapi-users."""

    __tablename__ = "blog_user"

    id: Mapped[int_primary_key]
    username: Mapped[str_len_20] = mapped_column(unique=True, nullable=False)
    image_file: Mapped[str_len_20] = mapped_column(
        nullable=False,
        default="default.jpg",
    )

    posts: Mapped[list["BlogPost"]] = relationship(
        back_populates="author",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def is_authenticated(self) -> bool:
        """Совместимость с UserMixin — всегда True для реального объекта."""
        return True

    def __repr__(self) -> str:
        return f"BlogUser('{self.username}', '{self.email}', '{self.image_file}')"


class BlogPost(Base):
    """Публикация блога."""

    __tablename__ = "blog_post"

    id: Mapped[int_primary_key]
    title: Mapped[str_len_100] = mapped_column(nullable=False)
    date_posted: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("blog_user.id"),
        nullable=False,
    )

    author: Mapped["BlogUser"] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"BlogPost('{self.title}', '{self.date_posted}')"


async def get_user_db(
    session: CurrentSession,
) -> AsyncGenerator[SQLAlchemyUserDatabase[BlogUser, int], None]:
    """Предоставить fastapi-users адаптер для текущей SQLAlchemy-сессии."""
    yield SQLAlchemyUserDatabase(session, BlogUser)


class UserManager(IntegerIDMixin, BaseUserManager[BlogUser, int]):
    """Менеджер fastapi-users для BlogUser с integer ID."""

    reset_password_token_secret = settings.auth.secret_key
    verification_token_secret = settings.auth.secret_key

    async def validate_password(
        self,
        password: str,
        user: schemas.UC | BlogUser,
    ) -> None:
        """Проверить пароль до хеширования штатным fastapi-users helper."""
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters",
            )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[BlogUser, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Создать менеджер с дефолтным fastapi-users hash helper."""
    yield UserManager(user_db)
