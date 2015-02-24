#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import unittest
import datetime
from simiki.config import parse_config


class TestParseConfig(unittest.TestCase):
    def setUp(self):
        self.expected_config = {
            "author": "Tanky Woo",
            "debug": True,
            "default_ext": "markdown",
            "description": "This is a simiki's config sample, \u6d4b\u8bd5\u6837\u4f8b",
            "destination": "destination",
            "index": False,
            "keywords": "wiki, simiki, python, \u7ef4\u57fa",
            "pygments": True,
            "root": "/wiki/",
            "source": "source",
            "theme": "mytheme",
            "themes_dir": "simiki_themes",
            'time': datetime.datetime.now(),
            "title": "\u6211\u7684Wiki",
            "url": "http://wiki.tankywoo.com"
        }
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tests", "configs", "config_sample.yml")

    def test_parse_config(self):
        config = parse_config(self.config_file)
        self.expected_config.pop('time')
        _date = config.pop('time')
        self.assertIsInstance(_date, datetime.datetime)
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
