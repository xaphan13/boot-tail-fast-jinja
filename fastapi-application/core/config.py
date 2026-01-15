from base_dir_path import BASE_DIR

from typing import Literal

from pydantic import (
    BaseModel,
    AnyUrl,
    UrlConstraints,
    PostgresDsn,
)

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class GunicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    timeout: int = 900


LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class LoggingConfigGunicorn(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    dep_examples: str = "/dep_examples"
    fastapi_class_old: str = "/fastapi_class_old"
    fastapi_class_annotated: str = "/fastapi_class_annotated"
    depends_class_annotated: str = "/depends_class_annotated"
    depends_function_annotated: str = "/depends_function_annotated"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()
    user_post_prefix: str = "/users"
    order_product_prefix: str = "/orders"


class SqliteDsn(AnyUrl):
    _constraints = UrlConstraints(
        allowed_schemes=[
            "sqlite",
            "sqlite+aiosqlite",
        ],
        host_required=False,
    )


class DatabaseConfig(BaseModel):
    url: PostgresDsn | SqliteDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / "two.env",  # sqlite
            # BASE_DIR / "one.env",  # postgres
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_prefix="APP__",
        env_nested_delimiter="__",
    )

    logging_gunicorn: LoggingConfigGunicorn = LoggingConfigGunicorn()
    gunicorn: GunicornConfig = GunicornConfig()

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()

    db: DatabaseConfig


settings = Settings()
