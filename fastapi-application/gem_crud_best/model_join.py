from __future__ import annotations

from typing import Annotated

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from datetime import datetime, timezone

from gem_crud_best.db_async import Base


# ========= types for mapped columns =========== #
time_stamp_utc = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    ),
]


class JoinPerson(Base):
    __tablename__ = "joinperson"

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    time_created: Mapped[time_stamp_utc]

    name = Column(String(20))
    surname = Column(String(20))
    link_addr = Column(Integer(), default=-1)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name}, surname={self.surname}, link_addr={self.link_addr})"
        )


class JoinAddress(Base):
    __tablename__ = "joinaddress"

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    time_created: Mapped[time_stamp_utc]

    city = Column(String(20))
    street = Column(String(20))
    addr_index = Column(Integer(), default=0)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(addr_index={self.addr_index}, "
            f"city={self.city}, street={self.street}, id={self.id})"
        )
