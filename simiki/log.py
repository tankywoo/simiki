#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging import getLogger, Formatter, StreamHandler

from simiki import utils

class ANSIFormatter(Formatter):
    """Use ANSI escape sequences to colored log"""

    def format(self, record):
        msg = record.getMessage()
        if record.levelname == "INFO":
            return msg
        elif record.levelname == "WARNING":
            return utils.color_msg("yellow", record.levelname) + ": " + msg
        elif record.levelname == "ERROR":
            return utils.color_msg("red", record.levelname) + ": " + msg
        elif record.levelname == "CRITICAL":
            return utils.color_msg("bgred", record.levelname) + ": " + msg
        elif record.levelname == "DEBUG":
            return utils.color_msg("blue", record.levelname) + ": " + msg
        else:
            return msg

def logging_init(level=None, logger=getLogger(), handler=StreamHandler(), use_color=True):
    if use_color:
        fmt = ANSIFormatter()
    else:
        fmt = Formatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)


if __name__ == "__main__":
    logging_init(level=logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.debug("debug")
    root_logger.info("info")
    root_logger.warning("warning")
    root_logger.error("error")
    root_logger.critical("critical")
