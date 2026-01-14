__all__ = (
    "Base",
    "User",
    "TestUser",
)

from db_core.model_base import Base

from example_sql.models.model_user import User
from example_sql.models.model_user_new import TestUser
