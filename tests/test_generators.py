#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, unicode_literals

import os
import os.path
import unittest

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))

from simiki.configs import parse_configs
from simiki.generators import PageGenerator

TEST_INPUT_FILE = os.path.join(TESTS_ROOT, "content", "linux", "test_input.md")
EXPECTED_OUTPUT = os.path.join(TESTS_ROOT, "expected_output.html")


class TestPageGenerator(unittest.TestCase):
    def setUp(self):
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "simiki/conf_templates/_config.yml.in"
        )

        configs = parse_configs(self.config_file)
        self.generator = PageGenerator(configs, os.path.dirname(__file__),
                                       TEST_INPUT_FILE)

    def test_get_category_and_file(self):
        category_name, filename = self.generator.get_category_and_file()
        self.assertEqual(
            (category_name, filename),
            (u'linux', u'test_input.md')
        )

    def test_get_metadata_and_content(self):
        metadata, content = self.generator.get_metadata_and_content()
        expected_metadata = {'date': '2013-11-11 11:11', 'tag': 'test, wiki',
                             'layout': 'page', 'title': 'Test Generator'}
        assert metadata == expected_metadata
        expected_content_list = ['\n', '# Simiki #\n', '\n',
                                 ('Simiki is a simple static site generator '
                                  'for wiki. Powered by Python.\n')]
        assert content == "".join(expected_content_list)

    def test_get_template_vars(self):
        template_vars = self.generator.get_template_vars()
        expected_template_vars = {
            u'site': {
                'index': False, 'description': '', 'title': '', 'url': '',
                'default_ext': 'md', 'destination': 'output',
                'themes_dir': 'themes', 'theme': 'simple', 'pygments': True,
                'source': 'content', 'keywords': '', 'debug': False,
                'author': '', 'root': ''
            },
            u'page': {
                u'category': u'linux', u'content': (u'<h1 id="simiki">'
                'Simiki</h1>\n<p>Simiki is a simple static site generator for '
                'wiki. Powered by Python.</p>'), 'tag': 'test, wiki',
                'layout': 'page', 'title': 'Test Generator',
                'date': '2013-11-11 11:11'
            }
        }

        assert template_vars == expected_template_vars

    def test_markdown2html(self):
        html = self.generator.markdown2html().strip()
        fd = open(EXPECTED_OUTPUT, "rb")
        expected_html = unicode(fd.read(), "utf-8")
        assert html == expected_html


if __name__ == "__main__":
    unittest.main()
