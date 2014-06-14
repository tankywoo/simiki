#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os import path as osp
import unittest
from simiki import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.content = "sample"
        self.output = "output"
        if utils.check_path_exists(self.output):
            utils.emptytree(self.output)
            os.rmdir(self.output)

    def test_copytree_common(self):
        utils.copytree(self.content, self.output)
        files = [".hidden.txt", "hellosimiki.md", "zen_of_python.txt",
                 "simiki.md"]
        assert(utils.check_path_exists(self.output))
        for f in files:
            assert(utils.check_path_exists(osp.join(self.output, f)))
        assert(not osp.islink(osp.join(self.output, "simiki.md")))

    def test_copytree_symlink(self):
        pass

    def test_copytree_ignore(self):
        pass

    def test_emptytree(self):
        utils.copytree(self.content, self.output)
        utils.emptytree(self.output)
        assert osp.isdir(self.output) and not os.listdir(self.output)

    def test_mkdir_p(self):
        path = osp.join(self.output, "dir1/dir2/dir3")
        utils.mkdir_p(path)
        assert (utils.check_path_exists(path))

    def test_listdir_nohidden(self):
        hidden_file = osp.join(self.content, ".hidden.txt")
        assert (utils.check_path_exists(hidden_file))

    def tearDown(self):
        if utils.check_path_exists(self.output):
            utils.emptytree(self.output)
            os.rmdir(self.output)


if __name__ == "__main__":
    unittest.main()
