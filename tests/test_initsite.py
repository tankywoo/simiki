#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os import path as osp
import unittest
from simiki.initsite import InitSite
from simiki.utils import check_path_exists, emptytree


class TestInitSite(unittest.TestCase):
    def setUp(self):
        BASE_DIR = osp.dirname(osp.dirname(osp.abspath(__file__)))
        config_file = osp.join(BASE_DIR, "simiki/conf_templates/_config.yml.in")
        i = InitSite(config_file)
        i.init_site()
        self.files = ["_config.yml", "fabfile.py"]
        self.dirs = ["content", "output", "themes"]

    def test_all_files_exist(self):
        all_fd = self.files + self.dirs + [\
                "content/intro/gettingstarted.md",\
                "themes/simple"\
                ]
        for fd in all_fd:
            assert check_path_exists(fd)

    def tearDown(self):
        for f in self.files:
            os.remove(f)
        for d in self.dirs:
            emptytree(d)
            os.rmdir(d)


if __name__ == "__main__":
    unittest.main()

