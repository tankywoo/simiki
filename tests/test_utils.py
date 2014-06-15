#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import unittest
from simiki import utils


class TestUtils(unittest.TestCase):

    def setUp(self):
        os.chdir(os.path.dirname(__file__))
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
            assert(utils.check_path_exists(os.path.join(self.output, f)))
        assert(not os.path.islink(os.path.join(self.output, "simiki.md")))

    def test_copytree_symlink(self):
        pass

    def test_copytree_ignore(self):
        pass

    def test_emptytree(self):
        utils.copytree(self.content, self.output)
        utils.emptytree(self.output)
        assert os.path.isdir(self.output) and not os.listdir(self.output)

    def test_mkdir_p(self):
        path = os.path.join(self.output, "dir1/dir2/dir3")
        utils.mkdir_p(path)
        assert (utils.check_path_exists(path))

    def test_listdir_nohidden(self):
        hidden_file = os.path.join(self.content, ".hidden.txt")
        assert (utils.check_path_exists(hidden_file))

    def tearDown(self):
        if utils.check_path_exists(self.output):
            utils.emptytree(self.output)
            os.rmdir(self.output)


if __name__ == "__main__":
    unittest.main()
