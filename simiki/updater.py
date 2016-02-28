#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
from simiki.compat import raw_input
from simiki.utils import copytree


def update_builtin(**kwargs):
    '''Update builtin scripts and themes under local site'''
    # for fabfile.py
    yes_ans = ('y', 'yes')
    _fabfile_r = os.path.join(os.path.dirname(__file__), 'conf_templates',
                              'fabfile.py')
    _fabfile_l = os.path.join(os.getcwd(), 'fabfile.py')
    if os.path.exists(_fabfile_l):
        # py3 require md5 with bytes object, otherwise raise
        # TypeError: Unicode-objects must be encoded before hashing
        with open(_fabfile_r, 'rb') as _fd:
            _fabfile_r_md5 = hashlib.md5(_fd.read()).hexdigest()
        with open(_fabfile_l, 'rb') as _fd:
            _fabfile_l_md5 = hashlib.md5(_fd.read()).hexdigest()
        if _fabfile_l_md5 != _fabfile_r_md5:
            try:
                _ans = raw_input('Overwrite fabfile.py? (y/N) ')
                if _ans.lower() in yes_ans:
                    shutil.copy2(_fabfile_r, _fabfile_l)
            except (KeyboardInterrupt, SystemExit):
                print()  # newline with Ctrl-C
    else:
        try:
            _ans = raw_input('New fabfile.py? (y/N) ')
            if _ans.lower() in yes_ans:
                shutil.copy2(_fabfile_r, _fabfile_l)
        except (KeyboardInterrupt, SystemExit):
            print()

    # for themes
    _themes_r = os.path.join(os.path.dirname(__file__), 'themes')
    _themes_l = os.path.join(os.getcwd(), kwargs['themes_dir'])
    for theme in os.listdir(_themes_r):
        _theme_r = os.path.join(_themes_r, theme)
        _theme_l = os.path.join(_themes_l, theme)
        if os.path.exists(_theme_l):
            _need_update = False
            for root, dirs, files in os.walk(_theme_r):
                files = [f for f in files if not f.startswith(".")]
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for filename in files:
                    with open(os.path.join(root, filename), 'rb') as _fd:
                        _theme_r_md5 = hashlib.md5(_fd.read()).hexdigest()
                    _dir = os.path.relpath(root, _theme_r)
                    with open(os.path.join(_theme_l, _dir, filename),
                              'rb') as _fd:
                        _theme_l_md5 = hashlib.md5(_fd.read()).hexdigest()
                    if _theme_l_md5 != _theme_r_md5:
                        _need_update = True
                        break
                if _need_update:
                    break
            if _need_update:
                try:
                    _ans = raw_input('Overwrite theme {0}? (y/N) '
                                     .format(theme))
                    if _ans.lower() in yes_ans:
                        shutil.rmtree(_theme_l)
                        copytree(_theme_r, _theme_l)
                except (KeyboardInterrupt, SystemExit):
                    print()
        else:
            try:
                _ans = raw_input('New theme {0}? (y/N) '.format(theme))
                if _ans.lower() in yes_ans:
                    copytree(_theme_r, _theme_l)
            except (KeyboardInterrupt, SystemExit):
                print()
