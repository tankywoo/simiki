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

from simiki.gen import PageGenerator

TEST_INPUT_FILE = "./test_input.md"

EXPECTED_OUTPUT = "./expected_output.html"

class TestPageGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = PageGenerator(TEST_INPUT_FILE)

    def test_get_catalog_and_md_name(self):
        catalog_name, md_name = self.generator.get_catalog_and_md_name()
        self.assertEqual((catalog_name, md_name), (u'tests', u'test_input'))

    def test_get_meta_datas(self):
        meta_yaml, _ = self.generator.split_meta_and_content()
        meta_datas = self.generator.get_meta_datas(meta_yaml)
        self.assertEqual(
            meta_datas, 
            {'Date': '2013-11-11 11:11', 'Title': 'Test Generator'}
        )

if __name__ == "__main__":
    unittest.main()
