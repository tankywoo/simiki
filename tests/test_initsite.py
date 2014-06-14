#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import shutil
from os import path as osp

from simiki.initsite import InitSite
from simiki.utils import check_path_exists


class TestInitSite(unittest.TestCase):

    def setUp(self):
        BASE_DIR = os.path.join(osp.dirname(__file__), '..')
        self.config_file = osp.join(BASE_DIR, "simiki", "conf_templates",
                                    "_config.yml.in")
        self.target_path = osp.join(BASE_DIR, "tests", "_build")
        if osp.exists(self.target_path):
            shutil.rmtree(self.target_path)
        os.mkdir(self.target_path)
        self.files = [
            "_config.yml",
            "fabfile.py",
            "content/intro/gettingstarted.md",
        ]
        self.dirs = [
            "content",
            "output",
            "themes",
            "themes/simple"
        ]

    def test_target_exist(self):
        """ test InitSite target path exist
        """

        i = InitSite(self.config_file, self.target_path)
        i.init_site()

        for f in self.files:
            self.assertTrue(osp.isfile(osp.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(osp.join(self.target_path, d)))

    def test_target_invalid(self):
        """ test InitSite target path invalid, raise OSError
        """

        self.files = ["_config.yml", "fabfile.py"]
        self.dirs = ["content", "output", "themes"]
        target_error = "/foo/bar/why/not"
        i = InitSite(self.config_file, target_error)
        with self.assertRaises(OSError):
            i.init_site()

    def tearDown(self):
        shutil.rmtree(self.target_path)

if __name__ == "__main__":
    unittest.main()
