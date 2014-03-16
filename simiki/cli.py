#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init
  simiki new -t <title> [-c <category>] [-f <file>]
  simiki generate
  simiki preview
  simiki -h | --help
  simiki -V | --version

Options:
  -h, --help             Help information.
  -V, --version          Show version.
  -c <category>          Specify the category.
  -t <title>             Specify the new post title.
  -f <file>              Specify the new post filename.

"""

from __future__ import print_function, unicode_literals

import os
import sys
import codecs
import datetime
import shutil
import logging
from os import path as osp
from pprint import pprint

from docopt import docopt

from simiki.generators import (PageGenerator, CatalogGenerator)
from simiki.initsite import InitSite
from simiki.configs import parse_configs
from simiki.log import logging_init
from simiki.server import preview
from simiki.utils import check_path_exists, copytree, check_extension
from simiki import __version__

logger = logging.getLogger(__name__)

#def create_wiki(title):
#    """
#    @todo: support 'Chinese' in title.
#    """
#    if not args["-f"]:
#        # `/` can't exists in filename
#        title_ = args["-t"].decode("utf-8").replace("/", " slash ")
#        args["-f"] = "{}.md".format("-".join(title_.split()).lower())
#    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#    simiki.create_new_wiki(
#        args["-c"], 
#        args["-f"], 
#        args["-t"].decode("utf-8"), 
#        cur_date.decode("utf-8"), 
#        layout="post"
#    )

class Simiki(object):

    def __init__(self, configs):
        self.configs = configs

    def create_new_wiki(self, category, filename, title, date):
        # TODO 判断arguments 的 type
        try:
            meta = "\n".join([
                "---",
                "title: \"{}\"".format(title),
                "date: {}".format(date),
                "---",
            ]) + "\n\n"
        except Exception, e:
            logger.error(str(e))
            sys.exit(1)

        category_path = osp.join(self.configs["source"], category)
        if not check_path_exists(category_path):
            os.mkdir(category_path)
            logger.info("create category {}.".format(category))

        fn = osp.join(category_path, filename)
        if check_path_exists(fn):
            logger.warning("wiki file exists: {}".format(fn))
        else:
            logger.info("create new wiki: {}".format(fn))
            with codecs.open(fn, "wb", "utf-8") as fd:
                fd.write(meta)

    def generate_single_page(self, md_file):
        logger.debug("Generate {}".format(md_file))
        pgen = PageGenerator(self.configs, md_file)
        html = pgen.mdown2html()
        pgen.output_to_file(html)

    def generate_all_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.configs["source"]

        for root, dirs, files in os.walk(content_path):
            for filename in files:
                if not check_extension(filename):
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

    if args["init"]:
        logging_init(logging.DEBUG)
        default_config_file = osp.join(os.path.dirname(__file__), 
                                        "conf_templates/_config.yml.in")
        isite = InitSite(default_config_file)
        isite.init_site()
        sys.exit(1)

    config_file = osp.join(os.getcwd(), "_config.yml")
    configs = parse_configs(config_file)
    level = logging.DEBUG if configs["debug"] else logging.INFO
    logging_init(level)
    simiki = Simiki(configs)

    if args["generate"]:
        simiki.generate()
    elif args["new"] and args["-t"]:
        pass
    elif args["preview"]:
        simiki.preview()
    else:
        # docopt itself will display the help info.
        pass

    logger.info("Done.")


if __name__ == "__main__":
    main()
