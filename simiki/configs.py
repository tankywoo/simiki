#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This is the configuration file of wiki.
The `CONTENT` can be set to any, and should rename the directory of markdown 
files.

"""

import sys
from os import path as osp

# This is the base directory of the wiki project
BASE_DIR = osp.dirname(osp.dirname(osp.realpath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Custom
WIKI_NAME = ""

WIKI_KEYWORDS = ""

WIKI_DESCRIPTION = ""

AUTHOR = ""

THEME = "simple"

################################

# The directory to store markdown files
CONTENT_PATH = osp.join(BASE_DIR, "content")

# The directory to store the generated html files
OUTPUT_PATH = osp.join(BASE_DIR, "html")

# The path of html template file
#TPL_PATH = osp.join(BASE_DIR, "simiki/themes", THEME, "base.html")
TPL_PATH = osp.join(BASE_DIR, "simiki/themes", THEME)

# Allowed suffixes ( aka "extensions" )
SUFFIXES = {".md", ".mkd", ".markdown"}
