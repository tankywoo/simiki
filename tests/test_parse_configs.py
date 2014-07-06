#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import unittest
from simiki.configs import parse_configs


class TestParseConfigs(unittest.TestCase):
    def setUp(self):
        self.expect_configs = {
            "author": "",
            "debug": False,
            "default_ext": "md",
            "description": "",
            "destination": "output",
            "index": False,
            "keywords": "",
            "pygments": True,
            "root": "/",
            "source": "content",
            "theme": "simple",
            "themes_dir": "themes",
            "title": "",
            "url": ""
        }
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "simiki/conf_templates/_config.yml.in"
        )

    def test_parse_configs(self):
        configs = parse_configs(self.config_file)
        self.assertEqual(
            configs,
            self.expect_configs
        )

    def test_parse_configs_not_exist(self):
        not_exist_config_file = os.path.join(self.config_file, "not_exist")
        self.assertRaises(Exception,
                          lambda: parse_configs(not_exist_config_file))

    def test_configs_url(self):
        config_file = os.path.join(
            os.path.dirname(__file__),
            "configs",
            "test_url.yml"
        )
        self.expect_configs["url"] = "http://wiki.tankywoo.com"
        configs = parse_configs(config_file)
        self.assertEqual(
            configs,
            self.expect_configs
        )

if __name__ == "__main__":
    unittest.main()
