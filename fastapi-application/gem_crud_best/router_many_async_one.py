from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Row
from sqlalchemy.sql import select, Select, insert, Insert
from sqlalchemy.orm import joinedload
from sqlalchemy.engine import Result
from typing import Sequence

from .schema_many_sql import (
    OrderCreateBody,
    OrderGetAllOrderbyQuery,
    OrderResp,
    ProductResp,
    OrderGetQuery,
)

from .model_new_many_db import (
    Order,
    Product,
)

from db_core.db_async import CurrentSession


new_many_async_one = APIRouter(prefix="/new_many_async_one", tags=["NEW new_many_async_one"])


# ================================================================================
# +++++++++++++++++++++++++ added record +++++++++++++++++++++++++
# ================================================================================
@new_many_async_one.post("/add_order", response_model=OrderResp)
async def add_order(body: OrderCreateBody, db: CurrentSession):
    new_order: Order = Order(**body.model_dump())
    db.add(new_order)

    await db.commit()
    await db.refresh(new_order)

    return new_order


@new_many_async_one.post("/insert_order", response_model=OrderCreateBody)
async def insert_order(db: CurrentSession, body: OrderCreateBody):
    stmt: Insert[Order] = insert(Order).values(**body.model_dump())

    await db.execute(stmt)
    await db.commit()

    return body


# ================================================================================
# +++++++++++++++++++++++++ get record - condition  +++++++++++++++++++++++++
# ================================================================================
@new_many_async_one.get("/get_order_filter_by", response_model=OrderResp)
async def get_order_filter_by(db: CurrentSession, params: OrderGetQuery = Depends()):
    # stmt: Select[tuple[Order]] = select(Order).filter_by(id=22)
    filter_where = {key: value for key, value in params.model_dump().items() if value is not None}

    stmt: Select[tuple[Order]] = select(Order).filter_by(**filter_where)

    result: Result[tuple[Order]] = await db.execute(stmt)

    order: Order = result.scalar()

    if order is not None:
        return order
    raise HTTPException(status_code=422, detail=f"select.filter_by with {filter_where} not found")


@new_many_async_one.get("/get_order_where", response_model=OrderResp | list[OrderResp])
async def get_order_where(db: CurrentSession, params: OrderGetQuery = Depends()):
    # stmt = select(Order).where(Order.id == 22)
    filter_where = [
        getattr(Order, key) == value for key, value in params.model_dump(exclude_none=True).items()
    ]

    # filter_where = [getattr(Order, key) > value
    #                 for key, value in params.dict(exclude_none=True).items()]

    stmt = select(Order).where(*filter_where)

    result = await db.execute(stmt)

    # orders: Order = result.scalar()
    # orders: Order = result.scalars().first()
    orders: Sequence[Order] = result.scalars().all()

    if orders is None:
        raise HTTPException(status_code=422, detail=f"select.where with {filter_where} not found")
    return orders


# ================================================================================
# +++++++++++++++++++++++++ get all - order_by +++++++++++++++++++++++++
# ================================================================================
# get all Order to the database **********************************************************
@new_many_async_one.get("/get_all_orders", response_model=list[OrderResp])
async def get_all_orders(db: CurrentSession, params: OrderGetAllOrderbyQuery):
    if params == "time":
        order_by_list_o: list[Column[Order]] = [Order.created_at, Order.id]
    elif params == "promocode":
        order_by_list_o: list[Column[Order]] = [Order.promocode, Order.created_at]
    else:
        order_by_list_o: list[Column[Order]] = [Order.id, Order.created_at]

    stmt: Select[tuple[Order]] = select(Order).order_by(*order_by_list_o)

    await_result_execute: Result[tuple[Order]] = await db.execute(stmt)
    result_scalars_all: Sequence[Order] = await_result_execute.scalars().all()

    return result_scalars_all


# ================================================================================
# +++++++++++++++++++++++++ test +++++++++++++++++++++++++
# ================================================================================
@new_many_async_one.get("/get_all_test", response_model=list[ProductResp | OrderResp])
async def get_all_orders(db: CurrentSession, variant: int = 1):
    stmt: Select[tuple[Order]] = (
        select(Order)
        .order_by(Order.id)
        # .options(selectinload(Order.products))
        .options(joinedload(Order.products))
    )
    await_result_execute: Result[tuple[Order]] = await db.execute(stmt)

    if variant == 1:
        result_scalars_all: Sequence[Order] = await_result_execute.unique().scalars().all()
        order0: Order = result_scalars_all[0]
        order1: Order = result_scalars_all[1]
    else:
        result_all: Sequence[Row[tuple[Order]]] = await_result_execute.unique().all()
        row0: Row[tuple[Order]] = result_all[0]
        order0: Order = row0[0]
        row1: Row[tuple[Order]] = result_all[1]
        order1: Order = row1[0]

    prods0: list[Product] = order0.products

    prods1: list[Product] = order1.products

    return [order0] + prods0 + [order1] + prods1
