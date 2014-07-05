#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from logging import getLogger, Formatter, StreamHandler

from simiki import utils


class ANSIFormatter(Formatter):
    """Use ANSI escape sequences to colored log"""

    def format(self, record):
        lvl2color = {
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bgred"
        }

        msg = record.getMessage()
        rln = record.levelname
        if rln in lvl2color:
            return "[{0}]: {1}".format(
                utils.color_msg(lvl2color[rln], rln),
                msg.encode('utf-8')
            )
        else:
            return msg


def logging_init(level=None, logger=getLogger(),
                 handler=StreamHandler(), use_color=True):
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
