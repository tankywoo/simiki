#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki_cli build_site
  simiki_cli new_wiki -c <catalog> -t <title> [-f <file>]
  simiki_cli generate
  simiki_cli preview
  simiki_cli -h | --help
  simiki_cli -V | --version

Options:
  -h --help        Show this screen.
  -V --version     Show version.
  -c <catalog>     Specify the catalog.
  -t <title>       Specify the new post title.
  -f <file>        Specify the new post filename.

"""


import os
import sys
import codecs
import datetime
import shutil
import errno
from os import path as osp

from docopt import docopt

BASE_DIR = osp.dirname(osp.realpath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import simiki.utils
import simiki.configs
import simiki.generators


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def build_site():
    content_path = simiki.configs.CONTENT_PATH
    output_path = simiki.configs.OUTPUT_PATH
    for path in (content_path, output_path):
        if osp.exists(path):
            print(simiki.utils.color_msg("info", "[%s] exists." % path))
        else:
            os.mkdir(path)
            print(simiki.utils.color_msg(
                "info", "create directory [%s]." % path))
    # TODO cp css
    #copyanything(osp.join(simiki.configs.TPL_PATH, "style.css"), simiki.configs.OUTPUT_PATH)

def create_new_wiki(catalog, filename, title, date, layout="post"):
    meta = "\n".join([
        "---",
        "layout: {}".format(layout),
        "title: \"{}\"".format(title),
        "date: {}".format(date),
        "---",
    ])
    meta += "\n\n\n"

    catalog_path = osp.join(simiki.configs.CONTENT_PATH, catalog)
    if not simiki.utils.check_path_exists(catalog_path):
        os.mkdir(catalog_path)
        print(simiki.utils.color_msg(
            "info", "create catalog [%s]." % catalog))

    fn = osp.join(catalog_path, filename)
    if simiki.utils.check_path_exists(fn):
        print(simiki.utils.color_msg(
            "warning", "wiki file exists: {}".format(fn)
        ))
    else:
        print(simiki.utils.color_msg(
            "info", "create new wiki: {}".format(fn)
        ))
        with codecs.open(fn, "wb", "utf-8") as fd:
            fd.write(meta)

def generate_single_page(md_file):
    pgen = simiki.generators.PageGenerator(md_file)
    html = pgen.mdown2html()
    pgen.output_to_file(html)

def generate_all_pages():
    content_path = simiki.configs.CONTENT_PATH

    for root, dirs, files in os.walk(content_path):
        for filename in files:
            if not simiki.utils.check_extension(filename):
                continue
            md_file = osp.join(root, filename)
            generate_single_page(md_file)

def generate_catalog():
    cgen = simiki.generators.CatalogGenerator(
            simiki.configs.BASE_DIR,
            simiki.configs.CONTENT_PATH, 
            simiki.configs.OUTPUT_PATH)
    cgen.update_catalog_page()

def generate():
    generate_all_pages()
    generate_catalog()

def main():
    args = docopt(__doc__, version='Simiki 0.1')
    if args["build_site"]:
        build_site()
    elif args["generate"]:
        generate()
    elif args["preview"]:
        pass
    elif args["-c"] and args["-t"]:
        if not args["-f"]:
            args["-f"] = "{}.md".format("-".join(args["-t"].split()).lower())
        cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        create_new_wiki(
            args["-c"], 
            args["-f"], 
            args["-t"], 
            cur_date, 
            layout="post"
        )
    else:
        pass


if __name__ == "__main__":
    main()
