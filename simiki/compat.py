#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Python compat for python version and os system
'''
import sys

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)


_platform = sys.platform

# Windows
is_windows = _platform.startswith('win32')

# Linux
is_linux = _platform.startswith('linux')

# Mac OS X
is_osx = _platform.startswith('darwin')

# TODO Windows/Cygwin for 'cygwin'?


# Specifics

if is_py2:
    unicode = unicode
    basestring = basestring
    xrange = xrange
    raw_input = raw_input

if is_py3:
    unicode = str
    basestring = (str, bytes)
    xrange = range
    raw_input = input
