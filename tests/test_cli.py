#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, unicode_literals

import os
import os.path
import shutil
import unittest
import io
from copy import deepcopy

from simiki import cli
from simiki.utils import emptytree

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))

INIT_ARGS = {
    u'--help': False,
    u'--version': False,
    u'-c': None,
    u'-f': None,
    u'-p': None,
    u'-t': None,
    u'generate': False,
    u'init': False,
    u'new': False,
    u'preview': False
}


class TestCliInit(unittest.TestCase):
    def setUp(self):
        self.args = deepcopy(INIT_ARGS)
        self.target_path = "_build"

        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)
        self.files = [
            "_config.yml",
            "fabfile.py",
            os.path.join("content", "intro", "gettingstarted.md"),
            os.path.join("themes", "simple", "page.html"),
            os.path.join("themes", "simple", "static", "css", "style.css")
        ]
        self.dirs = [
            "content",
            "output",
            "themes",
            os.path.join("themes", "simple"),
        ]

    def test_init(self):
        os.chdir(TESTS_ROOT)
        self.args.update({u'init': True, u'-p': self.target_path})
        cli.execute(self.args)
        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

    def tearDown(self):
        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)


class TestCliGenerate(unittest.TestCase):
    def setUp(self):
        self.args = deepcopy(INIT_ARGS)
        self.target_path = os.path.join(TESTS_ROOT, "mywiki")
        self.output_path = os.path.join(self.target_path, "output")
        if os.path.exists(self.output_path):
            emptytree(self.output_path)
        self.drafts = [
            os.path.join(self.output_path, "intro", "my_draft.html")
        ]
        self.files = [
            os.path.join(self.output_path, "index.html"),
            os.path.join(self.output_path, "intro", "gettingstarted.html")
        ]
        self.dirs = [
            self.output_path,
            os.path.join(self.output_path, "intro"),
        ]
        self.attach = [
            os.path.join(self.output_path, 'attach', 'images', 'linux',
                         'opstools.png'),
        ]
        self.static = [
            os.path.join(self.output_path, "static", "css", "style.css"),
        ]
        os.chdir(self.target_path)

    def test_generate(self):
        self.args.update({u'generate': True})
        cli.execute(self.args)
        for f in self.drafts:
            self.assertFalse(os.path.isfile(os.path.join(self.target_path, f)))

        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

        for f in self.attach:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

        for f in self.static:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

    def tearDown(self):
        if os.path.exists(self.output_path):
            emptytree(self.output_path)


class TestCliNewWiki(unittest.TestCase):
    def setUp(self):
        self.args = deepcopy(INIT_ARGS)
        self.title = "hello/simiki"
        self.category = os.path.join('my目录', 'sub-category')
        self.source_path = os.path.join(TESTS_ROOT, "content")
        self.odir = os.path.join(TESTS_ROOT, "content", self.category)
        self.odir_root = os.path.join(TESTS_ROOT, "content",
                                      self.category.split(os.sep)[0])
        os.chdir(TESTS_ROOT)
        if os.path.exists(self.odir_root):
            shutil.rmtree(self.odir_root)

    def test_new_wiki_without_file(self):
        ofile = os.path.join(self.odir, "hello-slash-simiki.md")

        self.args.update({u'new': True, u'-t': self.title,
                          u'-c': self.category})
        cli.execute(self.args)
        self.assertTrue(os.path.isfile(ofile))

        with io.open(ofile, "rt", encoding="utf-8") as fd:
            lines = fd.read().rstrip().splitlines()
            # Ignore date line
            lines[2] = u''
        expected_lines = [u'---', u'title: "hello/simiki"', u'', u'---']
        assert lines == expected_lines

    def tearDown(self):
        if os.path.exists(self.odir_root):
            shutil.rmtree(self.odir_root)


if __name__ == "__main__":
    unittest.main()
