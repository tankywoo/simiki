#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, unicode_literals
import unittest
import logging

try:
    # py2
    from cStringIO import StringIO
except ImportError:
    try:
        # py2
        from StringIO import StringIO
    except ImportError:
        # py3
        # from io import BytesIO as StringIO
        from io import StringIO as StringIO

import nose

from simiki.utils import color_msg
from simiki.log import logging_init
from simiki.compat import is_py2


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
            # in python 3.x, truncate(0) would not change the current file pos
            # via <http://stackoverflow.com/a/4330829/1276501>
            self.stream.seek(0)
            func = getattr(self.logger, level)
            func(level)
            expected_output = "[{0}]: {1}" \
                .format(color_msg(l2c[level], level.upper()), level)
            stream_output = self.stream.getvalue().strip()
            if is_py2:
                stream_output = unicode(stream_output)
            self.assertEqual(stream_output, expected_output)

    def tearDown(self):
        logging.disable(logging.CRITICAL)
        for handler in self.logger.handlers:
            if not isinstance(handler,
                              nose.plugins.logcapture.MyMemoryHandler):
                self.logger.removeHandler(handler)

if __name__ == "__main__":
    unittest.main()
