#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from logging import getLogger, Formatter, StreamHandler

from simiki import utils
from simiki.compat import is_linux, is_osx


class ANSIFormatter(Formatter):
    """Use ANSI escape sequences to colored log"""

    def format(self, record):
        try:
            msg = super(ANSIFormatter, self).format(record)
        except:
            # for python2.6
            # Formatter is old-style class in python2.6 and type is classobj
            # another trick: http://stackoverflow.com/a/18392639/1276501
            msg = Formatter.format(self, record)

        lvl2color = {
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bgred"
        }

        rln = record.levelname
        if rln in lvl2color:
            return "[{0}]: {1}".format(
                utils.color_msg(lvl2color[rln], rln),
                msg
            )
        else:
            return msg


class NonANSIFormatter(Formatter):
    '''Non ANSI color format'''

    def format(self, record):
        try:
            msg = super(NonANSIFormatter, self).format(record)
        except:
            # for python2.6
            # Formatter is old-style class in python2.6 and type is classobj
            # another trick: http://stackoverflow.com/a/18392639/1276501
            msg = Formatter.format(self, record)

        rln = record.levelname
        return "[{0}]: {1}".format(rln, msg)


def _is_platform_allowed_ansi():
    '''ansi be used on linux/macos'''
    if is_linux or is_osx:
        return True
    else:
        return False


def logging_init(level=None, logger=getLogger(),
                 handler=StreamHandler(), use_color=True):
    if use_color and _is_platform_allowed_ansi():
        fmt = ANSIFormatter()
    else:
        fmt = NonANSIFormatter()
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
