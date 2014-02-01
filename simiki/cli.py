#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki build_site [-s <config_file>]
  simiki new_wiki -c <catalog> -t <title> [-f <file>] [-s <config_file>]
  simiki generate [-s <config_file>]
  simiki preview [-s <config_file>]
  simiki -h | --help
  simiki -V | --version

Options:
  -h, --help             Help information.
  -V, --version          Show version.
  -c <catalog>           Specify the catalog.
  -t <title>             Specify the new post title.
  -f <file>              Specify the new post filename.
  -s <config_file>       Specify the config file.

"""

import os
import sys
import codecs
import datetime
import shutil
import logging
from os import path as osp
from pprint import pprint

from docopt import docopt

import simiki.utils
from simiki.generators import (PageGenerator, CatalogGenerator)
from simiki.configs import parse_configs
from simiki.log import logging_init
from simiki.server import preview
from simiki import __version__

logger = logging.getLogger(__name__)

class Simiki(object):

    def __init__(self, configs):
        self.configs = configs

    def update_css(self):
        logger.info("Update theme [{}] css.".format(self.configs["theme"]))

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
                logger.info("[%s] exists." % path)
            else:
                os.mkdir(path)
                logger.info("create directory [%s]." % path)

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
            logger.info("create catalog [{}].".format(catalog))

        fn = osp.join(catalog_path, filename)
        if simiki.utils.check_path_exists(fn):
            logger.warning("wiki file exists: {}".format(fn))
        else:
            logger.info("create new wiki: {}".format(fn))
            with codecs.open(fn, "wb", "utf-8") as fd:
                fd.write(meta)

    def generate_single_page(self, md_file):
        logger.debug("Generate [{}]".format(md_file))
        pgen = PageGenerator(self.configs, md_file)
        html = pgen.mdown2html()
        pgen.output_to_file(html)

    def generate_all_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.configs["source"]

        for root, dirs, files in os.walk(content_path):
            for filename in files:
                if not simiki.utils.check_extension(filename):
                    continue
                md_file = osp.join(root, filename)
                self.generate_single_page(md_file)

    def generate_catalog(self):
        logger.info("Generate catalog page.")
        cgen = CatalogGenerator(self.configs)
        cgen.update_catalog_page()

    def generate(self):
        self.generate_all_pages()
        self.generate_catalog()

    def preview(self):
        default_path = self.configs["destination"]
        preview(default_path)


def main():
    args = docopt(__doc__, version="Simiki {}".format(__version__))

    if args["-s"] is None:
        config_file = osp.join(os.getcwd(), "_config.yml")
    else:
        config_file = osp.realpath(args["-s"])

    configs = parse_configs(config_file)
    simiki = Simiki(configs)

    if configs["debug"]:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging_init(level)

    if args["build_site"]:
        simiki.build_site()
    elif args["generate"]:
        simiki.generate()
    elif args["new_wiki"] and args["-c"] and args["-t"]:
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
    elif args["preview"]:
        simiki.preview()
    else:
        # docopt itself will display the help info.
        pass

    logger.info("Done.")


if __name__ == "__main__":
    main()
