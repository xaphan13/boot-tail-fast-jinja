from pydantic import BaseModel
from pydantic import ConfigDict


class UserBase(BaseModel):
    nickname: str
    firstname: str | None
    surname: str | None
    password: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
