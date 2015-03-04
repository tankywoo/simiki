#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, unicode_literals

import os
import os.path
import unittest
import datetime

from simiki.config import parse_config, get_default_config
from simiki.generators import PageGenerator

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))


class TestPageGenerator(unittest.TestCase):
    def setUp(self):
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "simiki/conf_templates/_config.yml.in"
        )

        self.config = parse_config(self.config_file)

        self.base_path = os.path.dirname(__file__)

    def test_get_category_and_file(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        category, filename = generator.get_category_and_file()
        self.assertEqual(
            (category, filename),
            (u'foo\u76ee\u5f55', u'foo_page_\u4e2d\u6587.md')
        )

    def test_get_meta_and_content(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        meta, content = generator.get_meta_and_content()
        expected_meta = {'date': '2013-10-17 00:03', 'layout': 'page',
                         'title': 'Foo Page 2'}
        self.assertEqual(meta, expected_meta)
        self.assertEqual(content, '<p>Simiki is a simple wiki '
                                  'framework, written in Python.</p>')

        # get meta notaion error
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文_meta_error_1.md')
        generator = PageGenerator(self.config, self.base_path,
                                    src_file_path)
        self.assertRaises(Exception, generator.get_meta_and_content)

        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                       'foo_page_中文_meta_error_2.md')
        generator = PageGenerator(self.config, self.base_path,
                                    src_file_path)
        self.assertRaises(Exception, generator.get_meta_and_content)

    def test_get_template_vars(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        meta, content = generator.get_meta_and_content()
        template_vars = generator.get_template_vars(meta, content)
        expected_template_vars = {
            u'page': {
                u'category': u'foo\u76ee\u5f55',
                u'content': u'<p>Simiki is a simple wiki '
                            'framework, written in Python.</p>',
                'date': '2013-10-17 00:03',
                'layout': 'page',
                'title': 'Foo Page 2'
            },
            u'site': get_default_config()
        }

        expected_template_vars['site'].update({'root': ''})
        template_vars['site'].pop('time')
        expected_template_vars['site'].pop('time')
        assert template_vars == expected_template_vars

    def test_to_html(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        html = generator.to_html().strip()
        expected_output = os.path.join(TESTS_ROOT, 'expected_output.html')
        fd = open(expected_output, "rb")
        expected_html = unicode(fd.read(), "utf-8")
        assert html == expected_html

        # load template error
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_中文.md')
        generator = PageGenerator(self.config, 'wrong_basepath', src_file_path)
        self.assertRaises(Exception, generator.to_html)

    def test_get_layout(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_layout_old_post.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        meta, _ = generator.get_meta_and_content()

        layout = generator.get_layout(meta)
        self.assertEqual(layout, 'page')

        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_layout_without_layout.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        meta, _ = generator.get_meta_and_content()

        layout = generator.get_layout(meta)
        self.assertEqual(layout, 'page')

    def test_get_meta(self):
        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_get_meta_yaml_error.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        self.assertRaises(Exception, generator.get_meta_and_content)

        src_file_path = os.path.join(TESTS_ROOT, 'content', 'foo目录',
                                     'foo_page_get_meta_without_title.md')
        generator = PageGenerator(self.config, self.base_path, src_file_path)
        self.assertRaises(Exception, generator.get_meta_and_content)

if __name__ == "__main__":
    unittest.main()
