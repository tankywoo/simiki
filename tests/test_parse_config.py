#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import unittest
import datetime
from simiki.config import parse_config, get_default_config

test_path = os.path.dirname(os.path.abspath(__file__))


class TestParseConfig(unittest.TestCase):
    def setUp(self):
        wiki_path = os.path.join(test_path, 'mywiki_for_others')

        self.expected_config = get_default_config()
        self.expected_config.update({
            "author": "Tanky Woo",
            "debug": True,
            "default_ext": "markdown",
            "description": "This is a simiki's config sample, \u6d4b\u8bd5\u6837\u4f8b",
            "destination": "destination",
            "keywords": "wiki, simiki, python, \u7ef4\u57fa",
            "root": "/wiki/",
            "source": "source",
            "attach": "attach",
            "theme": "mytheme",
            "themes_dir": "simiki_themes",
            "title": "\u6211\u7684Wiki",
            "url": "http://wiki.tankywoo.com"
        })
        self.config_file = os.path.join(wiki_path, "config_sample.yml")

    def test_parse_config(self):
        config = parse_config(self.config_file)
        self.expected_config.pop('time')
        _date = config.pop('time')
        if hasattr(unittest.TestCase, 'assertIsInstance'):
            self.assertIsInstance(_date, datetime.datetime)
        else:
            assert isinstance(_date, datetime.datetime), \
                   '%s is not an instance of %r' % \
                   (repr(_date), datetime.datetime)
        self.assertEqual(
            config,
            self.expected_config
        )

    def test_parse_config_not_exist(self):
        not_exist_config_file = os.path.join(self.config_file, "not_exist")
        self.assertRaises(Exception,
                          lambda: parse_config(not_exist_config_file))


if __name__ == "__main__":
    unittest.main()
