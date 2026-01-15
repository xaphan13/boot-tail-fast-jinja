from pydantic import BaseModel

from typing import Optional, List

from datetime import datetime
from enum import Enum


# ==================================================================== #
#                   BaseModel - Order - pydantic                       #
# ==================================================================== #
class OrderGetQuery(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    promocode: Optional[str] = None


class OrderCreateBody(BaseModel):
    promocode: Optional[str] = None


class OrderUpdateBody(BaseModel):
    promocode: Optional[str] = None


class OrderGetAllOrderbyQuery(str, Enum):
    id = "id"
    time = "time"
    promocode = "promocode"


class OrderGetOrderbyList(BaseModel):
    order_by_list: List[OrderGetAllOrderbyQuery] = ["id"]


# ======================================================================= #
#                     BaseModel - Product - pydantic                      #
# ======================================================================= #
class ProductGetQuery(BaseModel):
    id: Optional[int] = 0
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None


class ProductCreateBody(BaseModel):
    name: str
    description: str
    price: int


class ProductUpdateBody(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    price: int | str = ""


# schemas are used when : get(GET) a OrderProductAssociation(Base)
class AssociationGetQuery(BaseModel):
    id: Optional[int] = 0
    count: Optional[int] = 0
    unit_price: Optional[int] = 0
    order_id: Optional[int] = 0
    product_id: Optional[int] = 0


# =========================================================== #
#             RESPONSE : response_model pydantic              #
# =========================================================== #
class OrderProductBase(BaseModel):
    class Config:
        from_attributes = True


# schema is used as a response_model for Order(Base)
class OrderResp(OrderProductBase):
    id: int
    created_at: datetime
    promocode: str


# schema is used as a response_model for Product(Base)
class ProductResp(OrderProductBase):
    id: int
    name: str
    description: str
    price: int


# schema is used as a response_model for OrderProductAssociation(Base)
class AssociationResp(BaseModel):
    id: int
    count: int
    unit_price: int
    order_id: int
    product_id: int


# ==================================================================== #
#     relationship('Order', secondary='order_product_association')     #
# ==================================================================== #
class ProductRespWithOrders(ProductResp):
    orders: List[OrderResp]


class ProductRespWithsAssoc(ProductResp):
    orders_details: List[AssociationResp]


class ProductRespWithOrdersAssoc(ProductResp):
    orders: List[OrderResp]
    orders_details: List[AssociationResp]


# ====================================================================== #
#     relationship('Product', secondary='order_product_association')     #
# ====================================================================== #
class OrderRespWithProducts(OrderResp):
    products: List[ProductResp]


class OrderRespWithAssoc(OrderResp):
    products_details: List[AssociationResp]


class OrderRespWithProductsAssoc(OrderResp):
    products: List[ProductResp]
    products_details: List[AssociationResp]


class OrderRespWithProductsDetails(OrderResp):
    products: List[ProductRespWithsAssoc]
