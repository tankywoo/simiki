#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki build_site [-s <config_file>]
  simiki new_wiki -c <catalog> -t <title> [-f <file>]
  simiki generate [-s <config_file>]
  simiki -h | --help
  simiki -V | --version

Options:
  -h --help        Show this screen.
  -V --version     Show version.
  -c <catalog>     Specify the catalog.
  -t <title>       Specify the new post title.
  -f <file>        Specify the new post filename.
  -s <config_file>        Specify the config file.

"""

import os
import sys
import codecs
import datetime
import shutil
from os import path as osp

import yaml
from docopt import docopt

BASE_DIR = osp.dirname(osp.realpath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import simiki.utils
from simiki.configs import parse_configs
import simiki.generators
from simiki import __version__


class Simiki(object):

    def __init__(self, configs):
        self.configs = configs

    def update_css(self):
        print(simiki.utils.color_msg(
            "info", "Update theme [{0}] css.".format(self.configs["theme"])))

        css_src = osp.join(self.configs["tpl_path"], "css")
        css_dst = osp.join(self.configs["destination"], "css")
        if osp.exists(css_dst):
            shutil.rmtree(css_dst)

        simiki.utils.copytree(css_src, css_dst)

    def build_site(self):
        content_path = self.configs["source"]
        output_path = self.configs["destination"]
        for path in (content_path, output_path):
            if osp.exists(path):
                print(simiki.utils.color_msg("info", "[%s] exists." % path))
            else:
                os.mkdir(path)
                print(simiki.utils.color_msg(
                    "info", "create directory [%s]." % path))

        self.update_css()

    def create_new_wiki(self, catalog, filename, title, date, layout="post"):
        meta = "\n".join([
            "---",
            "layout: {}".format(layout),
            "title: \"{}\"".format(title),
            "date: {}".format(date),
            "---",
        ])
        meta += "\n\n\n"

        catalog_path = osp.join(self.configs["source"], catalog)
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

    def generate_single_page(self, md_file):
        pgen = simiki.generators.PageGenerator(self.configs, md_file)
        html = pgen.mdown2html()
        pgen.output_to_file(html)

    def generate_all_pages(self):
        content_path = self.configs["source"]

        for root, dirs, files in os.walk(content_path):
            for filename in files:
                if not simiki.utils.check_extension(filename):
                    continue
                md_file = osp.join(root, filename)
                self.generate_single_page(md_file)

    def generate_catalog(self):
        cgen = simiki.generators.CatalogGenerator(self.configs)
        cgen.update_catalog_page()

    def generate(self):
        self.generate_all_pages()
        self.generate_catalog()

def main():
    args = docopt(__doc__, version="Simiki {}".format(__version__))

    if args["-s"] is None:
        config_file = osp.join(os.getcwd(), "_config.yml")
    else:
        config_file = osp.realpath(args["-s"])

    configs = parse_configs(config_file)
    simiki = Simiki(configs)
    if args["build_site"]:
        simiki.build_site()
    elif args["generate"]:
        simiki.generate()
    elif args["-c"] and args["-t"]:
        if not args["-f"]:
            args["-f"] = "{}.md".format("-".join(args["-t"].split()).lower())
        cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        simiki.create_new_wiki(
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
