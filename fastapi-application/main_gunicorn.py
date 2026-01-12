from core.config import settings
from core.gunicorn.gunicorn_app import MyGunicornApp
from core.gunicorn.gunicorn_opt import get_app_options

from main import main_app


def main():
    MyGunicornApp(
        application=main_app,
        options=get_app_options(
            host=settings.gunicorn.host,
            port=settings.gunicorn.port,
            timeout=settings.gunicorn.timeout,
            workers=settings.gunicorn.workers,
            log_level=settings.logging_gunicorn.log_level,
        ),
    ).run()


if __name__ == "__main__":
    main()
