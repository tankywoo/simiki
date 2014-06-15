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

if __name__ == "__main__":
    unittest.main()
