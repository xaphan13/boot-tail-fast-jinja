from base_dir_path import DIR_CWD, BASE_DIR
from config_log import logF

import uvicorn
from core.config import settings
from create_fastapi import create_app

from api import router_api
from example_sql.router_users import r_users_sql
from ex_order_product.router_order_product import r_order_one


main_app = create_app(
    custom_docs_url=False,
)

main_app.include_router(
    router_api,
)

main_app.include_router(
    r_users_sql,
)

main_app.include_router(
    r_order_one,
)


def main():
    logF.info(f"Base dir path :\n{DIR_CWD=} \n{BASE_DIR=}")

    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        # log_config=None,
        reload=True,
    )

    logF.warning(
        "end '-----------------' one-fastApi - main() '--------------------------' \n\n\n\n"
        "'********************************************************************************'"
    )


if __name__ == "__main__":
    main()
