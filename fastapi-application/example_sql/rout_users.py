from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
)

from .schemas.schema_user import UserRead, UserCreate

from .crud import crud_users as users_crud

from db_core.db_async import CurrentSession

router_users = APIRouter(tags=["Sql example users"])


@router_users.get("/get_all_users", response_model=list[UserRead])
async def get_users(session: CurrentSession):
    users = await users_crud.get_all_users(session=session)
    return users


@router_users.post("/create_user", response_model=UserRead)
async def create_user(
    session: CurrentSession,
    user_create: Annotated[
        UserCreate,
        Body(),
    ],
):
    user = await users_crud.create_user(
        session=session,
        user_create=user_create,
    )
    return user
