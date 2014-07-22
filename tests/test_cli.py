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
    u'--delete': False,
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
        self.target_path = os.path.join("tests", "_build")
        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)
        self.files = [
            "_config.yml",
            "fabfile.py",
            os.path.join("content", "intro", "gettingstarted.md")
        ]
        self.dirs = [
            "content",
            "output",
            "themes",
            os.path.join("themes", "simple"),
        ]
        os.chdir(TESTS_ROOT)

    def test_init(self):
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
        self.files = [
            os.path.join("output", "index.html"),
            os.path.join("output", "intro", "gettingstarted.html")
        ]
        self.dirs = [
            "output",
            os.path.join("output", "intro"),
            os.path.join("output", "static"),
            os.path.join("output", "static", "css")
        ]
        os.chdir(self.target_path)

    def test_generate(self):
        self.args.update({u'generate': True})
        cli.execute(self.args)
        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

    def tearDown(self):
        if os.path.exists(self.output_path):
            emptytree(self.output_path)


class TestCliNewWiki(unittest.TestCase):
    def setUp(self):
        self.args = deepcopy(INIT_ARGS)
        self.target_path = os.path.join(TESTS_ROOT, "mywiki")
        self.title = "hello/simiki"
        self.category = "testwiki"
        self.source_path = os.path.join(self.target_path, "content")
        self.odir = os.path.join(self.target_path, "content", "testwiki")
        self.ofile = os.path.join(self.odir, "hello-slash-simiki.md")
        if os.path.exists(self.odir):
            shutil.rmtree(self.odir)
        os.chdir(self.target_path)

    def test_new_wiki_without_file(self):
        self.args.update({u'new': True, u'-t': self.title,
                          u'-c': self.category})
        cli.execute(self.args)
        self.assertTrue(os.path.isfile(self.ofile))

        with io.open(self.ofile, "rt", encoding="utf-8") as fd:
            lines = fd.readlines()
            # Ignore date line
            lines[2] = u''
        expected_lines = [u'---\n', u'title: "hello/simiki"\n',
                          u'', u'---\n', u'\n']
        assert lines == expected_lines

    def tearDown(self):
        if os.path.exists(self.odir):
            shutil.rmtree(self.odir)


if __name__ == "__main__":
    unittest.main()
