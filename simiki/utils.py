#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import shutil
import errno
from os import path as osp

COLOR_CODES = {
    "reset" : "\033[0m",
    "black" : "\033[1;30m",
    "red" : "\033[1;31m",
    "green" : "\033[1;32m",
    "yellow" : "\033[1;33m",
    "blue" : "\033[1;34m",
    "magenta" : "\033[1;35m",
    "cyan" : "\033[1;36m",
    "white" : "\033[1;37m",
    "bgred" : "\033[1;41m",
    "bggrey" : "\033[1;100m",
}

def color_msg(color, msg):
    return COLOR_CODES[color] + msg + COLOR_CODES["reset"]

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
    print(color_msg("black", "Black"))
    print(color_msg("red", "Red"))
    print(color_msg("green", "Green"))
    print(color_msg("yellow", "Yellow"))
    print(color_msg("blue", "Blue"))
    print(color_msg("magenta", "Magenta"))
    print(color_msg("cyan", "Cyan"))
    print(color_msg("white", "White"))
    print(color_msg("bgred", "Background Red"))
    print(color_msg("bggrey", "Background Grey"))
