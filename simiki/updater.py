#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import logging
from simiki.compat import raw_input
from simiki.utils import copytree, get_md5

logger = logging.getLogger(__name__)
yes_answer = ('y', 'yes')


def get_input(text):
    return raw_input(text)


def _update_file(filename, local_path, original_path):
    '''
    :filename: file name to be updated, without directory
    :local_path: directory of local filename
    :original_path: directory of original filename
    '''
    up_to_date = True

    original_fn = os.path.join(original_path, filename)
    local_fn = os.path.join(local_path, filename)

    try:
        if os.path.exists(local_fn):
            original_fn_md5 = get_md5(original_fn)
            local_fn_md5 = get_md5(local_fn)

            if local_fn_md5 != original_fn_md5:
                up_to_date = False
                try:
                    _ans = get_input('Overwrite {0}? (y/N) '.format(filename))
                    if _ans.lower() in yes_answer:
                        shutil.copy2(original_fn, local_fn)
                except (KeyboardInterrupt, SystemExit):
                    print()  # newline with Ctrl-C
        else:
            up_to_date = False
            try:
                _ans = get_input('New {0}? (y/N) '.format(filename))
                if _ans.lower() in yes_answer:
                    shutil.copy2(original_fn, local_fn)
            except (KeyboardInterrupt, SystemExit):
                print()
    except Exception as e:
        logger.error(e)

    if up_to_date:
        logger.info('{0} is already up to date.'.format(filename))


def _update_dir(dirname, local_dir, original_dir, tag='directory'):
    '''Update sth on a per-directory basis, such as theme
    :dirname: directory name to be updated, without parent path
    :local_path: full path of local dirname
    :original_path: full path of original dirname
    :tag: input help information
    '''

    up_to_date = True

    try:
        if os.path.exists(local_dir):
            _need_update = False
            for root, dirs, files in os.walk(original_dir):
                files = [f for f in files if not f.startswith(".")]
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                rel_dir = os.path.relpath(root, original_dir)

                for fn in files:
                    original_fn_md5 = get_md5(os.path.join(root, fn))

                    local_fn = os.path.join(local_dir, rel_dir, fn)
                    if not os.path.exists(local_fn):
                        _need_update = True
                        break
                    local_fn_md5 = get_md5(local_fn)
                    if local_fn_md5 != original_fn_md5:
                        _need_update = True
                        break
                if _need_update:
                    break

            if _need_update:
                up_to_date = False
                try:
                    _ans = get_input('Overwrite {0} {1}? (y/N) '
                                     .format(tag, dirname))
                    if _ans.lower() in yes_answer:
                        shutil.rmtree(local_dir)
                        copytree(original_dir, local_dir)
                except (KeyboardInterrupt, SystemExit):
                    print()
        else:
            up_to_date = False
            try:
                _ans = get_input('New {0} {1}? (y/N) '.format(tag, dirname))
                if _ans.lower() in yes_answer:
                    copytree(original_dir, local_dir)
            except (KeyboardInterrupt, SystemExit):
                print()
    except Exception as e:
        logger.error(e)

    if up_to_date:
        logger.info('{0} {1} is already up to date.'.format(tag, dirname))


def update_builtin(**kwargs):
    '''Update builtin scripts and themes under local site'''
    logger.info('Start updating builin files.')
    logger.warning('Update is risky, please make sure you have backups')

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
        if theme in ('simple',):  # disabled/deprecated theme list
            continue
        local_theme = os.path.join(local_themes, theme)
        original_theme = os.path.join(original_themes, theme)
        _update_dir(theme, local_theme, original_theme, 'theme')
