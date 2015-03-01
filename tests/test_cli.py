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
    u'--ignore-root': False,
    u'--update-theme': False,
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
            os.path.join("output", "static", "css", "style.css"),
            os.path.join("themes", "simple", "page.html"),
            os.path.join("themes", "simple", "static", "css", "style.css")
        ]
        self.dirs = [
            "content",
            "output",
            "themes",
            os.path.join("themes", "simple"),
            os.path.join("output", "static"),
            os.path.join("output", "static", "css")
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
        self.files = [
            os.path.join(self.output_path, "index.html"),
            os.path.join(self.output_path, "intro", "gettingstarted.html")
        ]
        self.dirs = [
            self.output_path,
            os.path.join(self.output_path, "intro"),
        ]
        os.chdir(self.target_path)

    def test_generate(self):
        self.args.update({u'generate': True})
        cli.execute(self.args)
        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.target_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.target_path, d)))

    def test_generate_with_update_theme(self):
        self.args.update({u'generate': True, u'--update-theme': True})
        cli.execute(self.args)
        self.files.extend([os.path.join(self.output_path, "static", "css",
                                        "style.css")])
        self.dirs.extend([os.path.join(self.output_path, "static"),
                          os.path.join(self.output_path, "static", "css")])
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


class TestCopyAttach(unittest.TestCase):
    def setUp(self):
        self.current_dir = TESTS_ROOT
        self.attach_dir = 'attach'
        self.dest_dir = '_build'
        self.dest_path = os.path.join(self.current_dir, self.dest_dir)
        if os.path.exists(self.dest_path):
            shutil.rmtree(self.dest_path)

    def test_copy_attach(self):
        cli.copy_attach(self.current_dir, self.attach_dir, self.dest_dir)
        ofile = os.path.join(self.dest_dir, self.attach_dir,
                             'images', 'linux', 'opstools.png')
        self.assertTrue(os.path.isfile(ofile))

    def tearDown(self):
        if os.path.exists(self.dest_path):
            shutil.rmtree(self.dest_path)


if __name__ == "__main__":
    unittest.main()
