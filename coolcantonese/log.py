# -*- coding: utf-8 -*-

from os import environ
import logging
from logutils.colorize import ColorizingStreamHandler


def config_logging():
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    if "LOG_LEVEL" in environ:
        level = levels.get(environ["LOG_LEVEL"], logging.INFO)
    else:
        level = logging.INFO
    # format_str = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    format_str = "%(levelname)-8s %(message)s"
    logger = logging.getLogger()
    # handler = ColorHandler()
    handler = ColorizingStreamHandler()
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
