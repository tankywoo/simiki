#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement, unicode_literals

import sys
import os
import os.path
import unittest

# Prepend ../ to PYTHONPATH so that we can import simiki
TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTS_ROOT, '..'))) 

from simiki.gen import Generator

TEST_INPUT = "./test_input.md"
EXPECTED_OUTPUT = "./expected_output.html"

class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = Generator(TEST_INPUT)

    def test_get_title(self):
        title = self.generator._get_title()
        self.assertEqual(title, "Test Simiki")

    def test_md2html(self):
        title = self.generator._get_title()
        html = self.generator._md2html(title)
        with open(EXPECTED_OUTPUT, "rb") as fd:
            contents = [unicode(_, "utf-8") for _ in fd.readlines()]
            expected_html = "".join(contents)

        self.assertEqual(html, expected_html)

if __name__ == "__main__":
    unittest.main()
