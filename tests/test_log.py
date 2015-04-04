#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
from StringIO import StringIO

import nose

from simiki.utils import color_msg
from simiki.log import logging_init


class TestLogInit(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.NOTSET)
        self.stream = StringIO()
        self.logger = logging.getLogger()
        self.handler = logging.StreamHandler(self.stream)
        for handler in self.logger.handlers:
            # exclude nosetest capture handler
            if not isinstance(handler,
                              nose.plugins.logcapture.MyMemoryHandler):
                self.logger.removeHandler(handler)
        logging_init(level=logging.DEBUG, handler=self.handler)

    def test_logging_init(self):
        l2c = {
            "debug": "blue",
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "bgred"
        }
        for level in l2c:
            # self.handler.flush()
            self.stream.truncate(0)
            func = getattr(self.logger, level)
            func(level)
            expected_output = "[{0}]: {1}" \
                .format(color_msg(l2c[level], level.upper()), level)
            self.assertEqual(self.stream.getvalue().strip(), expected_output)

    def tearDown(self):
        logging.disable(logging.CRITICAL)
        for handler in self.logger.handlers:
            if not isinstance(handler,
                              nose.plugins.logcapture.MyMemoryHandler):
                self.logger.removeHandler(handler)

if __name__ == "__main__":
    unittest.main()
