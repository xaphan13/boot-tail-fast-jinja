from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Body,
)

from sqlalchemy.ext.asyncio import AsyncSession

from .crud import crud_users as users_crud

from .schemas.schema_user import UserRead, UserCreate

from .db_helper import db_helper_inst


router_users = APIRouter(tags=["Sql example users"])


@router_users.get("/get_all_users", response_model=list[UserRead])
async def get_users(
    session: Annotated[
        AsyncSession,
        Depends(db_helper_inst.session_getter),
    ],
):
    users = await users_crud.get_all_users(session=session)
    return users


@router_users.post("/create_user", response_model=UserRead)
async def create_user(
    user_create: Annotated[
        UserCreate,
        Body(),
    ],
    session: Annotated[
        AsyncSession,
        Depends(db_helper_inst.session_getter),
    ],
):
    user = await users_crud.create_user(
        session=session,
        user_create=user_create,
    )
    return user
