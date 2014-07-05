#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import logging
from StringIO import StringIO

from simiki.utils import color_msg
from simiki.log import logging_init


class TestLogInit(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        logging_init(level=logging.DEBUG, handler=self.handler)
        self.logger = logging.getLogger()

    def test_logging_init(self):
        self.logger.debug("debug")
        self.assertEqual(self.stream.getvalue().strip(),
                         "[{0}]: debug".format(color_msg("blue", "DEBUG")))
        self.stream.truncate(0)

        self.logger.info("info")
        self.assertEqual(self.stream.getvalue().strip(),
                         "[{0}]: info".format(color_msg("green", "INFO")))
        self.stream.truncate(0)

        self.logger.warning("warning")
        self.assertEqual(
            self.stream.getvalue().strip(),
            "[{0}]: warning".format(color_msg("yellow", "WARNING")))
        self.stream.truncate(0)

        self.logger.error("error")
        self.assertEqual(self.stream.getvalue().strip(),
                         "[{0}]: error".format(color_msg("red", "ERROR")))
        self.stream.truncate(0)

        self.logger.critical("critical")
        self.assertEqual(
            self.stream.getvalue().strip(),
            "[{0}]: critical".format(color_msg("bgred", "CRITICAL")))
        self.stream.truncate(0)

    def tearDown(self):
        self.logger.handlers = []

if __name__ == "__main__":
    unittest.main()
