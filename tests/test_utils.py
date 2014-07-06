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
        if os.path.exists(self.output):
            utils.emptytree(self.output)
            os.rmdir(self.output)

    def test_check_extension(self):
        file1 = "/tmp/file1.md"
        file2 = "/tmp/file2.mkd"
        file3 = "/tmp/test/文件3.mdown"
        file4 = "/var/lib/file4.markdown"
        file5 = "/tmp/testfile"
        file6 = "/tmp/wrong.mkdown"
        file7 = "/tmp/文件7.mkdown"
        assert utils.check_extension(file1)
        assert utils.check_extension(file2)
        assert utils.check_extension(file3)
        assert utils.check_extension(file4)
        assert not utils.check_extension(file5)
        assert not utils.check_extension(file6)
        assert not utils.check_extension(file7)

    def test_copytree_common(self):
        utils.copytree(self.content, self.output)
        files = [".hidden.txt", "hellosimiki.md", "zen_of_python.txt",
                 "simiki.md"]
        assert(os.path.exists(self.output))
        for f in files:
            assert(os.path.exists(os.path.join(self.output, f)))
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
        assert os.path.exists(path)
        path = os.path.join(self.content)
        utils.mkdir_p(path)
        assert os.path.exists(path)
        path = os.path.join(self.content, u"Simiki介绍.md")
        self.assertRaises(OSError, lambda: utils.mkdir_p(path))


    def test_listdir_nohidden(self):
        fs = utils.listdir_nohidden(self.content)
        assert sorted(list(fs)) == sorted([u"Simiki介绍.md", u"hellosimiki.md",
                                           u"simiki.md", u"zen_of_python.txt",
                                           u"介绍.md"])

    def tearDown(self):
        if os.path.exists(self.output):
            utils.emptytree(self.output)
            os.rmdir(self.output)


if __name__ == "__main__":
    unittest.main()
