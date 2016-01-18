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


# Specifics

if is_py2:
    unicode = unicode
    basestring = basestring
    xrange = xrange

if is_py3:
    unicode = str
    basestring = (str, bytes)
    xrange = range


