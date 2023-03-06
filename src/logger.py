"""Модуль с инициализацией логгера"""
import pathlib
import os
import logging
from datetime import datetime

def initialize_logger(name):
    """Инициализация логгера для логирования в файл
    :return logger: логгер, испоользуемый для записи
    :type logger: logging.Logger
    """
    # создание директории в проекте
    path = pathlib.Path(os.path.join(os.getcwd(), "logs"))
    path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    f_handler = logging.FileHandler(
        filename=f'logs/{datetime.now().strftime("%Y-%m-%d")}_{name}.log'
    )
    f_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '[%(asctime)s] – %(levelname)s – %(message)s'
    )

    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    return logger