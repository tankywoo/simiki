#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import unittest
import shutil

from simiki.config import get_default_config
from simiki.initiator import Initiator


class TestInitiator(unittest.TestCase):

    def setUp(self):
        BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
        self.default_config = get_default_config()
        self.config_file = os.path.join(BASE_DIR, "simiki", "conf_templates",
                                        "_config.yml.in")
        self.target_path = os.path.join(BASE_DIR, "tests", "_build")
        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)
        self.files = [
            "_config.yml",
            "fabfile.py",
            os.path.join(self.default_config['source'], "intro",
                         "gettingstarted.md"),
        ]
        self.dirs = [
            self.default_config['source'],
            self.default_config['destination'],
            self.default_config['themes_dir'],
            os.path.join(self.default_config['themes_dir'],
                         self.default_config['theme']),
        ]

    def test_target_exist(self):
        """ test Initiator target path exist
        """

        i = Initiator(self.config_file, self.target_path)
        i.init()

        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

    def test_target_invalid(self):
        """ test Initiator target path invalid, raise OSError
        """

        target_error = "/foo/bar/why/not"
        i = Initiator(self.config_file, target_error)
        self.assertRaises(OSError, lambda: i.init())

    def tearDown(self):
        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)

if __name__ == "__main__":
    unittest.main()
