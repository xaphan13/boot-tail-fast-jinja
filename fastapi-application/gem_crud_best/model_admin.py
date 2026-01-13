from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    BIGINT,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from typing import List

from gem_crud_best.db_async import Base


class Admin_list(Base):
    __tablename__ = "admin_list"

    admin_id: Mapped[int] = mapped_column(
        Integer(),
        unique=True,
        nullable=False,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(),
        unique=True,
        nullable=False,
    )

    admin_worked: Mapped[List["Admin_work"]] = relationship(
        back_populates="admin_lists",
        cascade="all, delete-orphan",
    )


class Admin_work(Base):
    __tablename__ = "admin_work"

    admin_work_id: Mapped[int] = mapped_column(
        BIGINT,
        unique=True,
        nullable=False,
        primary_key=True,
    )

    type_work: Mapped[str] = mapped_column(
        String,
        unique=False,
        nullable=False,
    )

    callback_data: Mapped[str] = mapped_column(
        String,
        unique=False,
        nullable=False,
    )

    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "admin_list.admin_id",
            ondelete="CASCADE",
        ),
    )

    admin_lists: Mapped["Admin_list"] = relationship(
        back_populates="admin_worked",
    )


# async def fixing_work_admin(admin_id_work: str, callback_data: str, db: AsyncSession):
#     stmt = select(Admin_list).where(Admin_list.user_id == str(admin_id_work))
#
#     admin_stmt = await db.execute(stmt)
#
#     add_work: Admin_list | None = admin_stmt.first()
#     add_work.admin_worked = [Admin_work(type_work="Registration", callback_data=callback_data)]
#
#     await db.commit()
