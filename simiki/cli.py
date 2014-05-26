#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init
  simiki new -t <title> -c <category> [-f <file>]
  simiki generate [--delete]
  simiki preview
  simiki -h | --help
  simiki -V | --version

Options:
  -h, --help             Help information.
  -V, --version          Show version.
  -c <category>          Specify the category.
  -t <title>             Specify the new post title.
  -f <file>              Specify the new post filename.
  --delete               Delete the contents of output directory before generate.

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

from simiki.generators import (PageGenerator, CatalogGenerator,
                            CustomCatalogGenerator)
from simiki.initsite import InitSite
from simiki.configs import parse_configs
from simiki.log import logging_init
from simiki.server import preview
from simiki.utils import (check_path_exists, copytree, emptytree,
                        check_extension, mkdir_p)
from simiki import __version__

logger = logging.getLogger(__name__)

def param_of_create_wiki(title, category, filename):
    """Get parameters of creating wiki page"""
    if not filename:
        # `/` can't exists in filename
        title_ = title.decode("utf-8").replace("/", " slash ")
        filename = "{}.md".format("-".join(title_.split()).lower())
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = title.decode("utf-8")
    category = category.decode("utf-8")
    return (category, filename, title, cur_date)

def write_file(content, ofile, ftype="page"):
    """Write content to output file.

    :param content: content to write to ofile
    :param ofile: output file
    :param ftype: file type, "page" or "index"
    """
    if ftype == "page":
        output_category,_ = osp.split(ofile)
        if not check_path_exists(output_category):
            logging.info(
                "The output category %s not exists, create it" \
                % output_category
            )
            mkdir_p(output_category)
    with codecs.open(ofile, "wb", "utf-8") as fd:
        fd.write(content)

def create_new_wiki(source, category, filename, title, date):
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

    category_path = osp.join(source, category)
    if not check_path_exists(category_path):
        os.mkdir(category_path)
        logger.info("Creating category {}.".format(category))

    fn = osp.join(category_path, filename)
    if check_path_exists(fn):
        logger.warning("wiki file exists: {}".format(fn))
    else:
        logger.info("Creating wiki: {}".format(fn))
        with codecs.open(fn, "wb", "utf-8") as fd:
            fd.write(meta)

def install_theme(current_dir, theme_name):
    """Copy static directory under theme to output directory"""
    src_theme = osp.join(current_dir, "themes/{}/static".format(theme_name))
    dst_theme = osp.join(current_dir, "output/static")
    if osp.exists(dst_theme):
        shutil.rmtree(dst_theme)

    copytree(src_theme, dst_theme)
    logging.info("Installing theme: {}".format(theme_name))

class Generator(object):

    def __init__(self, configs):
        self.configs = configs

    def generate(self, delete_output_dir=False):
        if delete_output_dir:
            logger.info("Delete all the files and dirs under output directory")
            output_dir = osp.join(os.getcwd(), self.configs["destination"])
            emptytree(output_dir)

        pages = self.generate_all_pages()
        self.generate_catalog(pages)
        install_theme(os.getcwd(), self.configs["theme"])

    def generate_all_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.configs["source"]

        pcnt = 0
        pages = {}
        for root, dirs, files in os.walk(content_path):
            files = [f for f in files if not f.decode("utf-8").startswith(".")]
            dirs[:] = [d for d in dirs if not d.decode("utf-8").startswith(".")]
            for filename in files:
                if not check_extension(filename):
                    continue
                md_file = osp.join(root, filename)
                pages[md_file] = self.generate_single_page(md_file)
                pcnt += 1
        logger.info("{} files generated.".format(pcnt))
        return pages

    def generate_single_page(self, md_file):
        md_file = md_file.decode('utf8')
        logger.debug("Generate {}".format(md_file))
        pgen = PageGenerator(self.configs, os.getcwd(), osp.realpath(md_file))
        html = pgen.markdown2html()

        def get_ofile():
            scategory, fname = osp.split(md_file)
            ofname = "{}.html".format(osp.splitext(fname)[0])
            category = osp.relpath(scategory, self.configs["source"])
            ocategory = osp.join(os.getcwd(), self.configs["destination"], category)
            ofile = osp.join(ocategory, ofname)
            return ofile

        ofile = get_ofile()
        write_file(html, ofile)
        meta_data, _ = pgen.get_metadata_and_content()
        return meta_data

    def generate_catalog(self, pages):
        logger.info("Generate catalog page.")
        if self.configs["index"]:
            cgen = CustomCatalogGenerator(self.configs, os.getcwd(), None)
        else:
            cgen = CatalogGenerator(self.configs, os.getcwd(), pages)
        html = cgen.generate_catalog_html()
        ofile = osp.join(os.getcwd(), self.configs["destination"], "index.html")
        write_file(html, ofile, "index")



def main():
    args = docopt(__doc__, version="Simiki {}".format(__version__))

    if args["init"]:
        logging_init(logging.DEBUG)
        default_config_file = osp.join(os.path.dirname(__file__),
                                        "conf_templates/_config.yml.in")
        isite = InitSite(default_config_file)
        isite.init_site()
        return

    config_file = osp.join(os.getcwd(), "_config.yml")
    configs = parse_configs(config_file)
    level = logging.DEBUG if configs["debug"] else logging.INFO
    logging_init(level)

    if args["generate"]:
        gen = Generator(configs)
        gen.generate(args["--delete"])
    elif args["new"] and args["-t"]:
        pocw = param_of_create_wiki(args["-t"], args["-c"], args["-f"])
        create_new_wiki(configs["source"], *pocw)
    elif args["preview"]:
        preview(configs["destination"])
    else:
        # docopt itself will display the help info.
        pass

    logger.info("Done.")


if __name__ == "__main__":
    main()
