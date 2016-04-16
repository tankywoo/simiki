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
from simiki.utils import copytree, emptytree
from simiki.config import get_default_config

test_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(test_path)

INIT_ARGS = {
    u'--help': False,
    u'--version': False,
    u'-c': None,
    u'-f': None,
    u'-p': None,
    u'-t': None,
    u'--host': None,
    u'--port': None,
    u'-w': None,
    u'--draft': None,
    u'generate': False,
    u'g': False,
    u'init': False,
    u'new': False,
    u'n': False,
    u'preview': False,
    u'p': False
}


class TestCliInit(unittest.TestCase):
    def setUp(self):
        self.default_config = get_default_config()
        self.args = deepcopy(INIT_ARGS)
        self.target_path = "_build"

        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path)
        self.files = [
            "_config.yml",
            "fabfile.py",
            os.path.join(self.default_config['source'], "intro",
                         "gettingstarted.md"),
            os.path.join(self.default_config['themes_dir'],
                         self.default_config['theme'],
                         "page.html"),
            os.path.join(self.default_config['themes_dir'],
                         self.default_config['theme'],
                         "static", "css", "style.css")
        ]
        self.dirs = [
            self.default_config['source'],
            self.default_config['destination'],
            self.default_config['themes_dir'],
            os.path.join(self.default_config['themes_dir'],
                         self.default_config['theme']),
        ]

    def test_init(self):
        os.chdir(test_path)
        self.args.update({u'init': True, u'-p': self.target_path})
        cli.main(self.args)
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
        self.wiki_path = os.path.join(test_path, "mywiki_for_cli")
        self.output_path = os.path.join(self.wiki_path, "output")

        if os.path.exists(self.output_path):
            emptytree(self.output_path)

        config_file_tpl = os.path.join(base_path, 'simiki',
                                       'conf_templates', '_config.yml.in')
        self.config_file_dst = os.path.join(self.wiki_path, '_config.yml')
        shutil.copyfile(config_file_tpl, self.config_file_dst)

        s_themes_path = os.path.join(base_path, 'simiki', 'themes')
        self.d_themes_path = os.path.join(self.wiki_path, 'themes')
        if os.path.exists(self.d_themes_path):
            shutil.rmtree(self.d_themes_path)
        copytree(s_themes_path, self.d_themes_path)

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
        os.chdir(self.wiki_path)

    def test_generate(self):
        self.args.update({u'generate': True})
        cli.main(self.args)
        for f in self.drafts:
            self.assertFalse(os.path.isfile(os.path.join(self.wiki_path, f)))

        for f in self.files:
            self.assertTrue(os.path.isfile(os.path.join(self.wiki_path, f)))

        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.wiki_path, d)))

        for f in self.attach:
            self.assertTrue(os.path.isdir(os.path.join(self.wiki_path, d)))

        for f in self.static:
            self.assertTrue(os.path.isdir(os.path.join(self.wiki_path, d)))

    def tearDown(self):
        os.remove(self.config_file_dst)
        if os.path.exists(self.d_themes_path):
            shutil.rmtree(self.d_themes_path)
        if os.path.exists(self.output_path):
            emptytree(self.output_path)


class TestCliNewWiki(unittest.TestCase):
    def setUp(self):
        wiki_path = os.path.join(test_path, 'mywiki_for_others')
        config_file_tpl = os.path.join(base_path, 'simiki',
                                       'conf_templates', '_config.yml.in')
        self.config_file_dst = os.path.join(wiki_path, '_config.yml')

        shutil.copyfile(config_file_tpl, self.config_file_dst)

        self.args = deepcopy(INIT_ARGS)
        self.title = "hello/simiki"
        self.category = os.path.join('my目录', 'sub-category')
        self.source_path = os.path.join(wiki_path, "content")
        self.odir = os.path.join(wiki_path, "content", self.category)
        self.odir_root = os.path.dirname(self.odir)

        os.chdir(wiki_path)
        if os.path.exists(self.odir_root):
            shutil.rmtree(self.odir_root)

    def test_new_wiki_without_file(self):
        ofile = os.path.join(self.odir, "hello-slash-simiki.md")

        self.args.update({u'new': True, u'-t': self.title,
                          u'-c': self.category})
        cli.main(self.args)
        self.assertTrue(os.path.isfile(ofile))

        with io.open(ofile, "rt", encoding="utf-8") as fd:
            lines = fd.read().rstrip().splitlines()
            # Ignore date line
            lines[2] = u''
        expected_lines = [u'---', u'title: "hello/simiki"', u'', u'---']
        assert lines == expected_lines

    def tearDown(self):
        os.remove(self.config_file_dst)
        if os.path.exists(self.odir_root):
            shutil.rmtree(self.odir_root)


if __name__ == "__main__":
    unittest.main()
