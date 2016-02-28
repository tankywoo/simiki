#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
import logging
from simiki.compat import raw_input
from simiki.utils import copytree

logger = logging.getLogger(__name__)
yes_answer = ('y', 'yes')


def _update_file(filename, local_path, original_path):
    '''
    :filename: file name to be updated, without directory
    :local_path: directory of local filename
    :original_path: directory of original filename
    '''
    original_fn = os.path.join(original_path, filename)
    local_fn = os.path.join(local_path, filename)

    try:
        if os.path.exists(local_fn):
            # py3 require md5 with bytes object, otherwise raise
            # TypeError: Unicode-objects must be encoded before hashing
            with open(original_fn, 'rb') as _fd:
                original_fn_md5 = hashlib.md5(_fd.read()).hexdigest()
            with open(local_fn, 'rb') as _fd:
                local_fn_md5 = hashlib.md5(_fd.read()).hexdigest()

            if local_fn_md5 != original_fn_md5:
                try:
                    _ans = raw_input('Overwrite {0}? (y/N) '.format(filename))
                    if _ans.lower() in yes_answer:
                        shutil.copy2(original_fn, local_fn)
                except (KeyboardInterrupt, SystemExit):
                    print()  # newline with Ctrl-C
        else:
            try:
                _ans = raw_input('New {0}? (y/N) '.format(filename))
                if _ans.lower() in yes_answer:
                    shutil.copy2(original_fn, local_fn)
            except (KeyboardInterrupt, SystemExit):
                print()
    except Exception as e:
        logger.error(e)


def _update_dir(dirname, local_dir, original_dir, tag='directory'):
    '''Update sth on a per-directory basis, such as theme
    :dirname: directory name to be updated, without parent path
    :local_path: full path of local dirname
    :original_path: full path of original dirname
    :tag: input help information
    '''
    try:
        if os.path.exists(local_dir):
            _need_update = False
            for root, dirs, files in os.walk(original_dir):
                files = [f for f in files if not f.startswith(".")]
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                rel_dir = os.path.relpath(root, original_dir)

                for fn in files:
                    with open(os.path.join(root, fn), 'rb') as _fd:
                        original_fn_md5 = hashlib.md5(_fd.read()).hexdigest()
                    local_fn = os.path.join(local_dir, rel_dir, fn)
                    if not os.path.exists(local_fn):
                        _need_update = True
                        break
                    with open(local_fn, 'rb') as _fd:
                        local_fn_md5 = hashlib.md5(_fd.read()).hexdigest()
                    if local_fn_md5 != original_fn_md5:
                        _need_update = True
                        break
                if _need_update:
                    break

            if _need_update:
                try:
                    _ans = raw_input('Overwrite {0} {1}? (y/N) '
                                     .format(tag, dirname))
                    if _ans.lower() in yes_answer:
                        shutil.rmtree(local_dir)
                        copytree(original_dir, local_dir)
                except (KeyboardInterrupt, SystemExit):
                    print()
        else:
            try:
                _ans = raw_input('New {0} {1}? (y/N) '.format(tag, dirname))
                if _ans.lower() in yes_answer:
                    copytree(original_dir, local_dir)
            except (KeyboardInterrupt, SystemExit):
                print()
    except Exception as e:
        logger.error(e)


def update_builtin(**kwargs):
    '''Update builtin scripts and themes under local site'''
    # for fabfile.py
    _update_file(
        'fabfile.py',
        os.getcwd(),
        os.path.join(os.path.dirname(__file__), 'conf_templates')
    )

    # for themes
    original_themes = os.path.join(os.path.dirname(__file__), 'themes')
    local_themes = os.path.join(os.getcwd(), kwargs['themes_dir'])
    for theme in os.listdir(original_themes):
        local_theme = os.path.join(local_themes, theme)
        original_theme = os.path.join(original_themes, theme)
        _update_dir(theme, local_theme, original_theme, 'theme')
