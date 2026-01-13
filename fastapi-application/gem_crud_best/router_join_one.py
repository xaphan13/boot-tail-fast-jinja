from fastapi import APIRouter, Depends
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from gem_crud_best.db_async import async_session_factory

from gem_crud_best.async_crud_base import personDB, addrDB

from gem_crud_best.schema_join import (
    CreateJoinPerson,
    GetJoinPerson,
    CreateJoinAddress,
    GetJoinAddress,
)

from gem_crud_best.model_admin import Admin_list, Admin_work
from gem_crud_best.model_join import JoinPerson, JoinAddress


join_one_r = APIRouter(prefix="/join_one_r", tags=["NEW join_one_r"])


# ==============================================================================
# +++++++++++++++++++ JoinPerson - select - JoinAddress ++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@join_one_r.get("/get_person", response_model=dict)
async def get_person(db: AsyncSession = Depends(async_session_factory.get_db)):
    stmt = select(JoinPerson, JoinAddress).outerjoin(
        JoinAddress,
        JoinAddress.addr_index == JoinPerson.link_addr,
    )

    stmt = select(JoinPerson, JoinAddress).join(
        JoinAddress,
        JoinAddress.addr_index == JoinPerson.link_addr,
    )

    stmt = select(JoinPerson, JoinAddress).where(
        JoinAddress.addr_index == JoinPerson.link_addr,
    )

    result = await db.execute(stmt)
    records = result.fetchall()

    for record in records:
        per = record.JoinPerson
        addr = record.JoinAddress

    return {}


@join_one_r.post("/create_person_addr", response_model=dict)
async def create_person_addr(
    db: AsyncSession = Depends(async_session_factory.get_db),
    data_addr=None,
    data_pers=None,
):
    await personDB.delete_record_many(GetJoinPerson(), db)
    await addrDB.delete_record_many(GetJoinAddress(), db)

    for idx, city, street in data_addr:
        addr = CreateJoinAddress(
            addr_index=idx,
            city=city,
            street=street,
        )
        await addrDB.add_record(addr, db)

    for name, surname, link_addr in data_pers:
        person = CreateJoinPerson(
            name=name,
            surname=surname,
            link_addr=link_addr,
        )
        await personDB.add_record(person, db)
    return {"CreateJoinAddress": len(data_addr), "CreateJoinPerson": len(data_pers)}


@join_one_r.delete("/delete_person_addr", response_model=dict)
async def delete_person_addr(
    params_pers: GetJoinPerson = Depends(),
    params_addr: GetJoinAddress = Depends(),
    db: AsyncSession = Depends(async_session_factory.get_db),
):
    qty_pers = await personDB.delete_record_many(params_pers, db)
    qty_addr = await addrDB.delete_record_many(params_addr, db)
    return {"DeleteJoinAddress": qty_addr, "DeleteJoinPerson": qty_pers}


# ==============================================================================
# ++++++++++++++ Admin_list - admin_worked.append - Admin_work +++++++++++++++++
# ------------------------------------------------------------------------------
@join_one_r.post("/create_Admin_list", response_model=dict)
async def create_Admin_list(db: AsyncSession = Depends(async_session_factory.get_db)):
    new_order: Admin_list = Admin_list(user_id="new1")
    db.add(new_order)
    await db.commit()
    return {}


@join_one_r.post("/fixing_work_admin", response_model=dict)
async def fixing_work_admin(db: AsyncSession = Depends(async_session_factory.get_db)):
    admin_id_work: str = "new1"
    callback_data: str = "callback_data"

    stmt = (
        select(Admin_list)
        .options(selectinload(Admin_list.admin_worked))
        .where(Admin_list.user_id == str(admin_id_work))
    )

    admin_stmt = await db.execute(stmt)
    add_work: Admin_list = admin_stmt.scalar_one()

    add_work.admin_worked.append(Admin_work(type_work="Registration", callback_data=callback_data))

    work = Admin_work(
        admin_id=add_work.admin_id, type_work="Registration", callback_data=callback_data
    )
    work = Admin_work(admin_lists=add_work, type_work="Registration", callback_data=callback_data)
    db.add(work)

    await db.commit()

    return {}
