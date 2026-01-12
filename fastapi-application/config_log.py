from base_dir_path import DIR_CWD, BASE_DIR
from pathlib import Path

import logging.config
import os


class ConfigLogger:
    pathDir_default: str = "./log"
    nameFile_default: str = "example.log"
    isSetting: bool = False  # для того чтобы settingLogger() вызвать один раз при запуске программы

    @staticmethod
    def __create_log_dir(log_dir: str):
        """Создание папки для лог-файлов"""
        path_dir: Path = BASE_DIR / log_dir
        if not os.path.exists(path_dir):
            os.mkdir(path_dir)

    @staticmethod
    def __settings_logger(log_dir: str = pathDir_default, log_file: str = nameFile_default):
        """настройка логгера с использованием словаря"""
        ConfigLogger.__create_log_dir(log_dir=log_dir)

        logging_config: dict = create_config_dict(log_dir, log_file)
        logging.config.dictConfig(logging_config)

        logging.basicConfig(level=logging.INFO, handlers=[])
        ConfigLogger.isSetting = True

    @staticmethod
    def setting_path_logger(log_dir: str = pathDir_default, log_file: str = nameFile_default):
        """настройка имени файла логгера и директории"""
        ConfigLogger.pathDir_default = log_dir
        ConfigLogger.nameFile_default = log_file
        ConfigLogger.__settings_logger(log_dir, log_file)

    @staticmethod
    def get_logger(nameBase: str):
        """nameBase берётся из словаря = 'loggers'
        OnlyFile = логгер будет писать в файл, в консоль не будет
        Stdout = только в консоль; FileStdout = и в консоль и в файл
        """
        if not ConfigLogger.isSetting:
            ConfigLogger.__settings_logger()
        return logging.getLogger(nameBase)


def create_config_dict(log_dir: str, log_file: str) -> dict:
    path_dir: Path = BASE_DIR / log_dir

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "form1": {
                "format": "/* %(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - [%(threadName)s] - %(thread)d - [%(processName)s] - %(process)d */ -> \n%(levelname)s: %(message)s"
            },
            "form2": {
                "format": "/* %(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - [%(threadName)s] - [%(thread)d] */  \n%(levelname)s: %(message)s"
            },
            "form3": {
                "format": "/* %(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - %(name)s */ -> \n%(levelname)s: %(message)s"
            },
            "form4": {
                "format": "/* %(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - [%(processName)s] - %(process)d */ -> \n%(levelname)s: %(message)s"
            },
            "con1": {
                "format": "%(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - [%(threadName)s] - [%(thread)d] \n > %(levelname)s: %(message)s"
            },
            "con2": {
                "format": "%(asctime)s - %(module)s.%(funcName)s(%(lineno)d) - [%(threadName)s] - [%(thread)d] > %(levelname)s: %(message)s"
            },
        },
        "handlers": {
            "rotating_file1": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "form2",
                "filename": f"{path_dir}/{log_file}",
                "maxBytes": 1048576,
                "backupCount": 20,
            },
            "console1": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "con2",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "Stdout": {
                "handlers": ["console1"],
                "level": "DEBUG",
            },
            "FileStdout": {
                "handlers": ["rotating_file1", "console1"],
                "level": "DEBUG",
            },
            "OnlyFile": {
                "handlers": ["rotating_file1"],
                "level": "DEBUG",
            },
            # Перехватываем логи Uvicorn
            # "uvicorn": {
            #     "handlers": ["rotating_file1", "console1"],
            #     "level": "INFO",
            #     "propagate": False,
            # },
            # "uvicorn.error": {
            #     "handlers": ["rotating_file1", "console1"],
            #     "level": "INFO",
            #     "propagate": False,
            # },
            # "uvicorn.access": {
            #     "handlers": ["rotating_file1", "console1"],
            #     "level": "INFO",
            #     "propagate": False,
            # },
        },
    }

    return logging_config


ConfigLogger.setting_path_logger(log_file="one_fast.log")

logF = ConfigLogger.get_logger("OnlyFile")
logFC = ConfigLogger.get_logger("FileStdout")
