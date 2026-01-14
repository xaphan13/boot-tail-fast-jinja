from __future__ import annotations

from sqlalchemy import (
    UniqueConstraint,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from db_core.type_for_models import (
    int_primary_key,
    str_len_100,
)

from db_core.model_base import Base


class User(Base):
    id: Mapped[int_primary_key]

    nickname: Mapped[str] = mapped_column(String(20), unique=True)

    firstname: Mapped[str | None] = mapped_column(String(20))
    surname: Mapped[str | None] = mapped_column(String(20))

    password: Mapped[str_len_100 | None]

    __table_args__ = (UniqueConstraint(firstname, surname),)
