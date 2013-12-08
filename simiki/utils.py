#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import shutil
import errno
from os import path as osp

RESET_COLOR = "\033[0m"

COLOR_CODES = {
    "debug" : "\033[1;34m", # blue
    "info" : "\033[1;32m", # green
    "warning" : "\033[1;33m", # yellow
    "error" : "\033[1;31m", # red
    "critical" : "\033[1;41m", # background red
}

def color_msg(level, msg):
    return COLOR_CODES[level] + msg + RESET_COLOR

def check_path_exists(path):
    """Check if the path(include file and directory) exists"""
    if osp.exists(path):
        return True
    return False

def check_extension(filename):
    """Filter file by suffix
    If the file suffix not in the allowed suffixes, the return true and filter.
    The `fnmatch` module can also get the suffix:
        patterns = ["*.md", "*.mkd", "*.markdown"]
        fnmatch.filter(files, pattern)
    """

    # Allowed suffixes ( aka "extensions" )
    exts = {".md", ".mkd", ".mdown", ".markdown"}
    return osp.splitext(filename)[1] in exts

#def copytree(src, dst):
#    try:
#        shutil.copytree(src, dst)
#    except OSError as exc: # python >2.5
#        if exc.errno == errno.ENOTDIR:
#            shutil.copy(src, dst)
#        else: raise

def copytree(src, dst, symlinks=False, ignore=None):

    # OSError: [Errno 17] File exists: '/home/tankywoo/simiki/html/css'
    if not osp.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = osp.join(src, item)
        d = osp.join(dst, item)
        if osp.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    print(color_msg("debug", "DEBUG"))
    print(color_msg("info", "DEBUG"))
    print(color_msg("warning", "WARNING"))
    print(color_msg("error", "ERROR"))
    print(color_msg("critical", "CRITICAL"))
