from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from db_core.type_for_models import time_stamp_utc

from db_core.model_base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer(),
        primary_key=True,
        index=True,
    )

    created_at: Mapped[time_stamp_utc]
    promocode = Column(String(50))

    # association between Order -> Association
    products_details = relationship(
        "OrderProductAssociation",
        back_populates="order",
        cascade="all, delete",
        overlaps="orders",
    )

    # association many to many
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

    # association between Product -> Association
    orders_details = relationship(
        "OrderProductAssociation",
        back_populates="product",
        cascade="all, delete",
        overlaps="products",
    )

    # association many to many
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

    # association between Assocation -> Order
    order = relationship(
        "Order",
        back_populates="products_details",
        overlaps="orders, products",
    )

    # association between Assocation -> Product
    product = relationship(
        "Product",
        back_populates="orders_details",
        overlaps="orders, products",
    )
