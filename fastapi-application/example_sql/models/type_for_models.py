from __future__ import annotations
from typing import Annotated

from sqlalchemy import (
    String,
    DateTime,
    func,
)

from sqlalchemy.orm import mapped_column

from datetime import datetime, timezone


int_primary_key = Annotated[
    int,
    mapped_column(
        primary_key=True,
        index=True,
    ),
]

str_len_100 = Annotated[
    str,
    mapped_column(String(100)),
]

time_stamp_utc = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    ),
]
