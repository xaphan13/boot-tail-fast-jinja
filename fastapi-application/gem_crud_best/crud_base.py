from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from sqlalchemy import Row, Column
from sqlalchemy.orm import Session

from typing import Optional, Generic, TypeVar, Type
from pydantic import BaseModel

from gem_crud_best.model_new_many_db import (
    Base,
    Order,
    Product,
)

from gem_crud_best.schema_many_sql import (
    OrderCreateBody,
    OrderGetQuery,
    OrderUpdateBody,
    ProductCreateBody,
    ProductGetQuery,
    ProductUpdateBody,
)


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=BaseModel)


class CRUDBase(
    Generic[
        ModelType,
        CreateSchemaType,
        ReadSchemaType,
        UpdateSchemaType,
        DeleteSchemaType,
    ]
):
    def __init__(self, model: Type[ModelType]):
        self.model: Type[ModelType] = model

    # adding record to the database *****************************************************
    # -----------------------------------------------------------------------------------
    def add_record(self, body: CreateSchemaType, db: Session, commit: bool = True) -> ModelType:
        create: ModelType = self.model(**body.model_dump())
        db.add(create)
        if commit:
            db.commit()
        return create

    def add_dict_record(self, model_dict: dict, db: Session, commit: bool = True) -> ModelType:
        create: ModelType = self.model(**model_dict)
        db.add(create)
        if commit:
            db.commit()
        return create

    # requesting first record from DB ***** if read return None -> HTTPException ********
    # -----------------------------------------------------------------------------------
    def get_record_schema_raise(self, query: ReadSchemaType, db: Session) -> ModelType:
        query_dict = {key: value for key, value in query.model_dump().items() if value is not None}
        read: Optional[ModelType] = db.query(self.model).filter_by(**query_dict).first()
        if read is None:
            raise HTTPException(
                status_code=422, detail=f"query.filter_by with {query_dict} not found"
            )
        return read

    def get_record_dict_raise(self, filter_dict: dict, db: Session) -> ModelType:
        read: Optional[ModelType] = db.query(self.model).filter_by(**filter_dict).first()
        if read is None:
            raise HTTPException(
                status_code=422, detail=f"query.filter with {filter_dict} not found"
            )
        return read

    # requesting first record from DB ******** if read return None or record ************
    # -----------------------------------------------------------------------------------
    def get_record_schema_none(self, query: ReadSchemaType, db: Session) -> Optional[ModelType]:
        query_dict = {key: value for key, value in query.model_dump().items() if value is not None}
        read: Optional[ModelType] = db.query(self.model).filter_by(**query_dict).first()
        return read

    def get_record_dict_none(self, filter_dict: dict, db: Session) -> Optional[ModelType]:
        read: Optional[ModelType] = db.query(self.model).filter_by(**filter_dict).first()
        return read

    # requesting list of records from the database **************************************
    # -----------------------------------------------------------------------------------
    def get_record_all(
        self, db: Session, order_by_list: list[Column[ModelType]] = None
    ) -> list[Row[ModelType]]:
        if order_by_list is None:
            records: list[Row[ModelType]] = db.query(self.model).all()
        else:
            records: list[Row[ModelType]] = db.query(self.model).order_by(*order_by_list).all()
        return records

    def get_record_part(
        self, begin: int, length: int, db: Session, order_by_list: list[Column[ModelType]] = None
    ) -> list[Row[ModelType]]:
        if order_by_list is None:
            records: list[Row[ModelType]] = db.query(self.model).offset(begin).limit(length).all()
        else:
            records: list[Row[ModelType]] = (
                db.query(self.model).order_by(*order_by_list).offset(begin).limit(length).all()
            )
        return records

    # updating record from the database *************************************************
    # -----------------------------------------------------------------------------------
    def update_record(
        self, query: ReadSchemaType, body: UpdateSchemaType, db: Session, commit: bool = True
    ) -> ModelType:
        update: ModelType = self.get_record_schema_raise(query, db)

        update_dict = body.model_dump(exclude_none=True).items()
        [setattr(update, name, value) for name, value in update_dict if value != ""]

        if commit:
            db.commit()
        return update

    # deleting record from the database *************************************************
    # -----------------------------------------------------------------------------------
    def delete_record(self, query: DeleteSchemaType, db: Session, commit: bool = True) -> ModelType:
        delete: ModelType = self.get_record_schema_raise(query, db)
        db.delete(delete)
        if commit:
            db.commit()
        return delete

    def delete_record_dict(self, filter_dict: dict, db: Session, commit: bool = True) -> ModelType:
        delete: ModelType = self.get_record_dict_raise(filter_dict, db)
        db.delete(delete)
        if commit:
            db.commit()
        return delete

    def delete_all(self, db: Session, commit: bool = True) -> dict[str, int]:
        res: int = db.query(self.model).delete()
        if commit:
            db.commit()
        return {"delete": res}

    def delete_all_for(self, db: Session, commit: bool = True) -> dict[str, int]:
        list_delete: list[Row[ModelType]] = db.query(self.model).all()
        [db.delete(record) for record in list_delete]
        if commit:
            db.commit()
        return {"delete": len(list_delete)}

    def json_encoder(self, base_db: Base) -> dict:
        res: dict = jsonable_encoder(base_db)
        return res


# ========= crud for Order and Product =========== #
class OrderCRUD(
    CRUDBase[
        Order,
        OrderCreateBody,
        OrderGetQuery,
        OrderUpdateBody,
        OrderGetQuery,
    ]
):
    pass


order_db = OrderCRUD(Order)


class ProductCRUD(
    CRUDBase[
        Product,
        ProductCreateBody,
        ProductGetQuery,
        ProductUpdateBody,
        ProductGetQuery,
    ]
):
    pass


product_db = ProductCRUD(Product)
