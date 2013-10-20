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

TEST_INPUT_FILE = "./test_input.md"

TEST_INPUT_CONTENT = """<!-- title : Test Simiki -->

# Simiki #

Simiki is a simple static site generator for wiki. Powered by Python.

* Support [Markdown](http://daringfireball.net/projects/markdown/).
* Generate static Htmls.
* Have a CLI tool.
* Simple for wiki.

## Why named "Simiki" ##

Simki is **Sim**ple W**iki** .
"""

EXPECTED_OUTPUT = "./expected_output.html"

class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator1 = Generator(TEST_INPUT_FILE)
        self.generator2 = Generator(TEST_INPUT_CONTENT, md_type="text")

    def test_get_title_by_file(self):
        title = self.generator1._get_title()
        self.assertEqual(title, "Test Simiki")

    def test_get_title_by_text(self):
        title = self.generator2._get_title()
        self.assertEqual(title, "Test Simiki")

    def test_md2html_by_file(self):
        html = self.generator1.generate()
        with open(EXPECTED_OUTPUT, "rb") as fd:
            texts = [unicode(_, "utf-8") for _ in fd.readlines()]
            expected_html = "".join(texts)

        self.assertEqual(html, expected_html)

    def test_md2html_by_text(self):
        html = self.generator2.generate()
        with open(EXPECTED_OUTPUT, "rb") as fd:
            texts = [unicode(_, "utf-8") for _ in fd.readlines()]
            expected_html = "".join(texts)

        self.assertEqual(html, expected_html)

if __name__ == "__main__":
    unittest.main()
