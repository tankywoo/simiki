#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

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

if __name__ == "__main__":
    print(color_msg("debug", "DEBUG"))
    print(color_msg("info", "DEBUG"))
    print(color_msg("warning", "WARNING"))
    print(color_msg("error", "ERROR"))
    print(color_msg("critical", "CRITICAL"))
