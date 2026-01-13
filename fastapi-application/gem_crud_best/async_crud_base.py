from fastapi.encoders import jsonable_encoder

from sqlalchemy import Column, Executable
from sqlalchemy.sql import select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Generic, TypeVar, Type, Sequence
from pydantic import BaseModel

from gem_crud_best.model_join import (
    JoinAddress,
    JoinPerson,
    Base,
)

from gem_crud_best.schema_join import (
    GetJoinAddress,
    CreateJoinAddress,
    GetJoinPerson,
    CreateJoinPerson,
)

SqlType = TypeVar("SqlType", bound=Base)
CreateType = TypeVar("CreateType", bound=BaseModel)
ReaderType = TypeVar("ReaderType", bound=BaseModel)
UpdateType = TypeVar("UpdateType", bound=BaseModel)
DeleteType = TypeVar("DeleteType", bound=BaseModel)


# ======= add result class =======
class AddResult:
    def __init__(self, model: SqlType, result: bool = True, reason: str = "OK"):
        self.result: bool = result
        self.model: SqlType = model
        self.reason: str = reason

    def str_detail(self) -> str:
        begin_D = self.reason.find("DETAIL: ")
        end_D = self.reason.find(".", begin_D)
        return self.reason[begin_D:end_D]


# ======= async base crud class =======
class AsyncBaseCRUD(
    Generic[
        SqlType,
        CreateType,
        ReaderType,
        UpdateType,
        DeleteType,
    ]
):
    # *******************************************************************
    # *************************  AsyncBaseCRUD  *************************
    def __init__(self, model: Type[SqlType]):
        self.model: Type[SqlType] = model

    # *******************************************************************
    # ************************* not sql function ************************
    def _get_filter_attr(self, schema_filter_attr):
        schema_dump = schema_filter_attr.model_dump(exclude_none=True).items()
        filter_attr = [getattr(self.model, k) == v for k, v in schema_dump]
        return filter_attr

    def get_filter_attr(self, schema_filter_attr):
        schema_dump = schema_filter_attr.model_dump(exclude_none=True).items()
        filter_attr = [getattr(self.model, k) == v for k, v in schema_dump]
        return filter_attr

    def get_order_attr(self, name_column_order_by: list[str]) -> list[Column[SqlType]]:
        order_attr = [getattr(self.model, name) for name in name_column_order_by]
        return order_attr

    def model_to_dict(self, sql_model: SqlType) -> dict:
        res: dict = jsonable_encoder(sql_model)
        return res

    # *******************************************************************
    # *********************** add  async  insert ************************
    async def add_record(
        self, schema: CreateType, db: AsyncSession, commit: bool = True
    ) -> SqlType:
        new_record: SqlType = self.model(**schema.model_dump())
        db.add(new_record)
        # ______________________ await  async  added _______________________
        if commit:
            await db.commit()  # IntegrityError
            await db.refresh(new_record)
        return new_record

    # *******************************************************************
    # *********************** add  async  insert ************************
    async def add_record_try(
        self, schema: CreateType, db: AsyncSession, commit: bool = True
    ) -> AddResult:
        new_record: SqlType = self.model(**schema.model_dump())
        db.add(new_record)
        # ______________________ await  async  added _______________________
        if commit:
            try:
                await db.commit()  # IntegrityError
                await db.refresh(new_record)
            except IntegrityError as e:
                return AddResult(model=new_record, result=False, reason=e.__str__())
        return AddResult(model=new_record)

    # *******************************************************************
    # *********************** get  async  select ************************
    async def get_record_one(
        self, schema: ReaderType, db: AsyncSession, query_n: Executable | None = None
    ) -> SqlType | None:
        filter_attr = self._get_filter_attr(schema)
        if len(filter_attr) == 0:
            return None
        query = select(self.model).where(*filter_attr) if query_n is None else query_n
        # ___________________ await  async  select  one ____________________
        result = await db.execute(query)
        record: SqlType | None = result.scalar()
        return record

    async def get_records_list(
        self, schema: ReaderType, db: AsyncSession, query_n: Executable | None = None
    ) -> list[SqlType]:
        filter_attr = self._get_filter_attr(schema)
        query = select(self.model).where(*filter_attr) if query_n is None else query_n
        # ___________________ await  async  select  all ____________________
        result = await db.execute(query)
        records: Sequence[SqlType] = result.scalars().all()
        return list(records)

    async def get_all_records(
        self, order_by: list[Column[SqlType]], db: AsyncSession, query_n: Executable | None = None
    ) -> list[SqlType]:
        query = select(self.model).order_by(*order_by) if query_n is None else query_n
        # ___________________ await  async  select  all ____________________
        result = await db.execute(query)
        records: Sequence[SqlType] = result.scalars().all()
        return list(records)

    # *******************************************************************
    # ******* get async select - with selectinload(relationship) ********
    async def get_record_rel_one(
        self, schema: ReaderType, load: list, db: AsyncSession
    ) -> SqlType | None:
        query = select(self.model).where(*self._get_filter_attr(schema))
        for name_table in load:
            query = query.options(joinedload(name_table))
        return await self.get_record_one(schema, db, query_n=query)

    async def get_records_rel_list(
        self, schema: ReaderType, load: list, db: AsyncSession
    ) -> list[SqlType]:
        query = select(self.model).where(*self._get_filter_attr(schema))
        for name_table in load:
            query = query.options(selectinload(name_table))
        return await self.get_records_list(schema, db, query_n=query)

    async def get_order_rel_list(
        self,
        schema: ReaderType,
        load: list,
        db: AsyncSession,
        order_by: list[Column[SqlType]] | None = None,
    ) -> list[SqlType]:
        query = select(self.model).where(*self._get_filter_attr(schema))
        for name_table in load:
            query = query.options(selectinload(name_table))
        if order_by is not None:
            query = query.order_by(*order_by)
        return await self.get_records_list(schema, db, query_n=query)

    async def get_all_rel_records(
        self, order_by: list[Column[SqlType]], load: list, db: AsyncSession
    ) -> list[SqlType]:
        query = select(self.model).order_by(*order_by)
        for name_table in load:
            query = query.options(selectinload(name_table))
        return await self.get_all_records(order_by, db, query_n=query)

    # *******************************************************************
    # ********************* update  async  update ***********************
    async def update_record_one(
        self, model: SqlType, schema: UpdateType, db: AsyncSession
    ) -> SqlType | None:
        if model is not None:
            for k, v in schema.model_dump(exclude_unset=True).items():
                setattr(model, k, v)
            # ___________________ await  async  update  one ____________________
            await db.commit()
        return model

    async def update_record_many(self, search: ReaderType, schema: UpdateType, db: AsyncSession):
        filter_attr = self._get_filter_attr(search)
        if len(filter_attr) == 0:
            return 0
        update_values = schema.model_dump(exclude_unset=True)
        query = update(self.model).where(*filter_attr).values(**update_values)
        # ___________________ await  async  update  all ____________________
        result = await db.execute(query)
        await db.commit()
        qty_update = result.rowcount
        return qty_update

    # *******************************************************************
    # ********************* delete  async  delete ***********************
    async def delete_record_one(self, model: SqlType, db: AsyncSession) -> SqlType | None:
        if model is not None:
            # ___________________ await  async  delete  one ____________________
            await db.delete(model)
            await db.commit()
        return model

    async def delete_record_many(self, search: ReaderType, db: AsyncSession):
        filter_attr = self._get_filter_attr(search)
        if len(filter_attr) == 0:
            return 0
        query = delete(self.model).where(*filter_attr)
        # ___________________ await  async  delete  all ____________________
        result = await db.execute(query)
        await db.commit()
        qty_delete = result.rowcount
        return qty_delete

    async def delete_all_or_id(self, db: AsyncSession, idx: int = 0):
        result = (
            await db.execute(delete(self.model))
            if idx == 0
            else await db.execute(delete(self.model).where(self.model.id == idx))
        )
        await db.commit()
        qty_delete = result.rowcount
        return qty_delete

    def json_encoder(self, base_db: Base) -> dict:
        res: dict = jsonable_encoder(base_db)
        return res


# ======= crud for join address =======
class AsyncJoinAddressCRUD(
    AsyncBaseCRUD[
        JoinAddress,
        CreateJoinAddress,
        GetJoinAddress,
        CreateJoinAddress,
        GetJoinAddress,
    ]
):
    def get_model(self):
        return self.model


addrDB = AsyncJoinAddressCRUD(JoinAddress)


class AsyncJoinPersonCRUD(
    AsyncBaseCRUD[
        JoinPerson,
        CreateJoinPerson,
        GetJoinPerson,
        CreateJoinPerson,
        GetJoinPerson,
    ]
):
    def get_model(self):
        return self.model


personDB = AsyncJoinPersonCRUD(JoinPerson)
