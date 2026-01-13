from pydantic import BaseModel

from typing import Optional, List

from datetime import datetime
from enum import Enum


# ==============================================================================
# ++++++++++++++++++ BaseModel - JoinPerson - pydantic +++++++++++++++++++++++++
# ------------------------------------------------------------------------------
class GetJoinPerson(BaseModel):
    id: Optional[int] = None
    time_created: Optional[datetime] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    link_addr: Optional[int] = None


class CreateJoinPerson(BaseModel):
    name: str
    surname: str
    link_addr: Optional[int] = None


class OrderbyJoinPersonEnum(str, Enum):
    id = "id"
    time_created = "time_created"
    name = "name"
    surname = "surname"
    link_addr = "link_addr"


class OrderbyJoinPersonList(BaseModel):
    order_by_list: List[OrderbyJoinPersonEnum] = ["id"]


class RespJoinPerson(BaseModel):
    id: Optional[int]
    time_created: Optional[datetime]
    name: Optional[str]
    surname: Optional[str]
    link_addr: Optional[int]


# ==============================================================================
# ++++++++++++++++++ BaseModel - JoinAddress - pydantic ++++++++++++++++++++++++
# ------------------------------------------------------------------------------
class GetJoinAddress(BaseModel):
    id: Optional[int] = None
    time_created: Optional[datetime] = None
    city: Optional[str] = None
    street: Optional[str] = None
    addr_index: Optional[int] = None


class CreateJoinAddress(BaseModel):
    city: str
    street: str
    addr_index: int


class OrderbyJoinAddressEnum(str, Enum):
    id = "id"
    time_created = "time_created"
    city = "city"
    street = "street"
    addr_index = "addr_index"


class OrderbyJoinAddressList(BaseModel):
    order_by_list: List[OrderbyJoinAddressEnum] = ["id"]


class RespJoinAddress(BaseModel):
    id: Optional[int]
    time_created: Optional[datetime]
    city: Optional[str]
    street: Optional[str]
    addr_index: Optional[int]


data_addr2 = [
    (1, "New York", "Broadway"),
    (2, "Los Angeles", "Hollywood Blvd"),
    (4, "London", "Oxford Street"),
    (4, "Paris", "Champs-Élysées"),
    (5, "Tokyo", "Shibuya"),
]
data_pers2 = [
    ("Jane", "Smith", 1),
    ("Michael", "Johnson", 2),
    ("Emma", "Brown", 13),
    ("William", "Jones", 4),
    ("Olivia", "Davis", 5),
]
