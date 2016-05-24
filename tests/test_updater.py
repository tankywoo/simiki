#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import os
import os.path
import shutil
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from simiki import utils, updater
from simiki.config import get_default_config

test_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(test_path)


class TestUpdater(unittest.TestCase):

    def setUp(self):
        self.default_config = get_default_config()

        self.wiki_path = os.path.join(test_path, 'mywiki_for_others')
        os.chdir(self.wiki_path)

        self.kwargs = {'themes_dir': 'themes'}
        self.original_fabfile = os.path.join(base_path, 'simiki',
                                             'conf_templates', 'fabfile.py')
        self.local_fabfile = os.path.join(self.wiki_path, 'fabfile.py')

        self.original_theme = os.path.join(base_path, 'simiki',
                                           self.default_config['themes_dir'],
                                           self.default_config['theme'])
        self.local_theme = os.path.join(self.wiki_path,
                                        self.default_config['themes_dir'],
                                        self.default_config['theme'])

        self.local_theme_afile = os.path.join(self.local_theme, 'base.html')

    @patch('simiki.updater.get_input', return_value='yes')
    def test_update_builtin_not_exists_with_yes(self, mock_input):
        self.assertFalse(os.path.exists(self.local_fabfile))
        self.assertFalse(os.path.exists(self.local_theme))

        updater.update_builtin(**self.kwargs)

        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertEqual(original_fn_md5, local_fn_md5)

        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertEqual(original_fn_md5, local_fn_md5)

        os.remove(self.local_theme_afile)
        updater.update_builtin(**self.kwargs)

        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertEqual(original_fn_md5, local_fn_md5)

    @patch('simiki.updater.get_input', return_value='no')
    def test_update_builtin_not_exists_with_no(self, mock_input):
        self.assertFalse(os.path.exists(self.local_fabfile))
        self.assertFalse(os.path.exists(self.local_theme))

        updater.update_builtin(**self.kwargs)

        self.assertFalse(os.path.exists(self.local_fabfile))
        self.assertFalse(os.path.exists(self.local_theme))

    @patch('simiki.updater.get_input', return_value='yes')
    def test_update_builtin_exists_with_yes(self, mock_input):
        # empty fabfile.py
        with open(self.local_fabfile, 'wb') as _fd:
            _fd.close()
        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

        utils.copytree(self.original_theme, self.local_theme)
        with open(self.local_theme_afile, 'wb') as _fd:
            _fd.close()
        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

        updater.update_builtin(**self.kwargs)

        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertEqual(original_fn_md5, local_fn_md5)

        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertEqual(original_fn_md5, local_fn_md5)

    @patch('simiki.updater.get_input', return_value='no')
    def test_update_builtin_exists_with_no(self, mock_input):
        # empty fabfile.py
        with open(self.local_fabfile, 'wb') as _fd:
            _fd.close()
        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

        utils.copytree(self.original_theme, self.local_theme)
        with open(self.local_theme_afile, 'wb') as _fd:
            _fd.close()
        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

        updater.update_builtin(**self.kwargs)

        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertNotEqual(original_fn_md5, local_fn_md5)

    def test_update_builtin_up_to_date(self):
        shutil.copyfile(self.original_fabfile, self.local_fabfile)
        utils.copytree(self.original_theme, self.local_theme)

        updater.update_builtin(**self.kwargs)

        original_fn_md5 = utils.get_md5(self.original_fabfile)
        local_fn_md5 = utils.get_md5(self.local_fabfile)
        self.assertEqual(original_fn_md5, local_fn_md5)

        original_fn_md5 = utils.get_dir_md5(self.original_theme)
        local_fn_md5 = utils.get_dir_md5(self.local_theme)
        self.assertEqual(original_fn_md5, local_fn_md5)

    def tearDown(self):
        if os.path.exists(self.local_fabfile):
            os.remove(self.local_fabfile)
        if os.path.exists(self.local_theme):
            shutil.rmtree(os.path.dirname(self.local_theme))


if __name__ == '__main__':
    unittest.main()
