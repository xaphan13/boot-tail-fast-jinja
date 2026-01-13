from __future__ import annotations
from typing import Annotated
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    relationship,
    DeclarativeBase,
    mapped_column,
)


# ========= base class for async crud =========== #
from gem_crud_best.async_crud_base import SqlType


class AddResult:
    def __init__(self, model: SqlType, result: bool = True, reason: str = "OK"):
        self.result: bool = result
        self.model: SqlType = model
        self.reason: str = reason

    def str_detail(self) -> str:
        begin_D = self.reason.find("DETAIL: ")
        end_D = self.reason.find(".", begin_D)
        return self.reason[begin_D:end_D]


# ========= types for mapped columns =========== #
int_primary_key = Annotated[
    int,
    mapped_column(
        primary_key=True,
        index=True,
    ),
]

str_len_100 = Annotated[
    str,
    mapped_column(String(100)),
]

time_stamp_utc = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    ),
]


# ========= base class for models =========== #
class Base(DeclarativeBase):
    __abstract__ = True


# ========= models for database =========== #
class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    created_at: Mapped[time_stamp_utc]
    promocode = Column(String(50))

    products_details = relationship(
        "OrderProductAssociation",
        back_populates="order",
        cascade="all, delete",
        overlaps="orders",
    )

    products = relationship(
        "Product",
        secondary="order_product_association",
        back_populates="orders",
        overlaps="products_details",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, promocode={self.promocode}, created_at={self.created_at})"


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    name = Column(String(100))
    description = Column(String(100))
    price = Column(Integer())

    orders_details = relationship(
        "OrderProductAssociation",
        back_populates="product",
        cascade="all, delete",
        overlaps="products",
    )

    orders = relationship(
        "Order",
        secondary="order_product_association",
        back_populates="products",
        overlaps="orders_details",
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, name={self.name}, "
            f"description={self.description}, price={self.price})"
        )


# ========= models for association between Order and Product =========== #
class OrderProductAssociation(Base):
    __tablename__ = "order_product_association"
    __table_args__ = (UniqueConstraint("order_id", "product_id", name="idx_unique_order_product"),)

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    count = Column(Integer(), default=1, server_default="1")
    unit_price = Column(Integer(), default=0, server_default="0")

    order_id = Column(
        Integer(),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_id = Column(
        Integer(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    order = relationship(
        "Order",
        back_populates="products_details",
        overlaps="orders, products",
    )

    product = relationship(
        "Product",
        back_populates="orders_details",
        overlaps="orders, products",
    )
