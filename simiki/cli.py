#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init [-p <path>]
  simiki new -t <title> -c <category> [-f <file>]
  simiki generate [--ignore-root] [--delete]
  simiki preview
  simiki -h | --help
  simiki -V | --version

Options:
  -h, --help          Help information.
  -V, --version       Show version.
  -c <category>       Specify the category.
  -t <title>          Specify the new post title.
  -f <file>           Specify the new post filename.
  -p <path>           Specify the target path.
  --ignore-root       Ignore root setting and replace with `/` as root.
  --delete            Empty the destination directory before generate.
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import os.path
import sys
import io
import datetime
import shutil
import logging
import traceback

from docopt import docopt
from yaml import YAMLError

from simiki.generators import (PageGenerator, CatalogGenerator,
                               CustomCatalogGenerator)
from simiki.initsite import InitSite
from simiki.config import parse_config
from simiki.log import logging_init
from simiki.server import preview
from simiki.utils import (copytree, emptytree, check_extension, mkdir_p)
from simiki import __version__

logger = logging.getLogger(__name__)


def param_of_create_wiki(title, category, filename, ext):
    """Get parameters of creating wiki page"""
    if not isinstance(title, unicode):
        title = unicode(title, "utf-8")
    if not filename:
        # `/` can't exists in filename
        title_ = title.replace(os.sep, " slash ")
        filename = "{0}.{1}".format("-".join(title_.split()).lower(), ext)
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if not isinstance(category, unicode):
        category = unicode(category, 'utf-8')
    return (category, filename, title, cur_date)


def write_file(content, ofile, ftype="page"):
    """Write content to output file.

    :param content: content to write to ofile
    :param ofile: output file
    :param ftype: file type, "page" or "index"
    """
    if ftype == "page":
        output_category, _ = os.path.split(ofile)
        if not os.path.exists(output_category):
            logging.info(
                "The output category %s not exists, create it", output_category)
            mkdir_p(output_category)
    with io.open(ofile, "wt", encoding="utf-8") as fd:
        fd.write(content)


def create_new_wiki(source, category, filename, title, date):
    meta = "\n".join([
        "---",
        "title: \"{0}\"".format(title),
        "date: {0}".format(date),
        "---",
    ]) + "\n\n"

    category_path = os.path.join(source, category)
    if not os.path.exists(category_path):
        os.mkdir(category_path)
        logger.info("Creating category {0}.".format(category))

    fn = os.path.join(category_path, filename)
    if os.path.exists(fn):
        logger.warning("wiki file exists: {0}".format(fn))
    else:
        logger.info("Creating wiki: {0}".format(fn))
        with io.open(fn, "wt", encoding="utf-8") as fd:
            fd.write(meta)


def install_theme(current_dir, theme_name):
    """Copy static directory under theme to destination directory"""
    src_theme = os.path.join(
        current_dir,
        "themes/{0}/static".format(theme_name)
    )
    dest_theme = os.path.join(current_dir, "output/static")
    if os.path.exists(dest_theme):
        shutil.rmtree(dest_theme)

    copytree(src_theme, dest_theme)
    logging.info("Installing theme: {0}".format(theme_name))


class Generator(object):

    def __init__(self, config):
        self.config = config
        self.target_path = os.getcwdu()

    def generate(self, empty_dest_dir=False):
        if empty_dest_dir:
            logger.info("Empty the destination directory")
            dest_dir = os.path.join(self.target_path,
                                    self.config["destination"])
            emptytree(dest_dir)

        pages = self.generate_all_pages()
        self.generate_catalog(pages)

        if empty_dest_dir:
            install_theme(self.target_path, self.config["themes_dir"],
                          self.config["theme"], self.config["destination"])

    def generate_all_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.config["source"]

        pcnt = 0
        pages = {}
        for root, dirs, files in os.walk(content_path):
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(self.config["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)
                pages[md_file] = self.generate_single_page(md_file)
                pcnt += 1
        logger.info("{0} files generated.".format(pcnt))
        return pages

    def generate_single_page(self, md_file):
        logger.debug("Generate {0}".format(md_file))
        page_generator = PageGenerator(
            self.config,
            self.target_path,
            os.path.realpath(md_file)
        )
        try:
            html = page_generator.to_html()
        except Exception as e:
            logger.exception('{0}: {1}'.format(md_file, unicode(e)))
            sys.exit(1)

        def get_ofile():
            scategory, fname = os.path.split(md_file)
            ofname = "{0}.html".format(os.path.splitext(fname)[0])
            category = os.path.relpath(scategory, self.config["source"])
            ocategory = os.path.join(
                self.target_path, self.config["destination"], category
            )
            ofile = os.path.join(ocategory, ofname)
            return ofile

        ofile = get_ofile()
        write_file(html, ofile)
        meta = page_generator.meta
        return meta

    def generate_catalog(self, pages):
        logger.info("Generate catalog page.")
        if self.config["index"]:
            catalog_generator = CustomCatalogGenerator(self.config,
                                                       self.target_path)
        else:
            catalog_generator = CatalogGenerator(self.config,
                                                 self.target_path,
                                                 pages)
        html = catalog_generator.generate_catalog_html()
        ofile = os.path.join(
            self.target_path,
            self.config["destination"],
            "index.html"
        )
        write_file(html, ofile, "index")


def execute(args):
    logging_init(logging.DEBUG)

    target_path = unicode(args['-p'], 'utf-8') if args['-p'] else os.getcwdu()

    if args["init"]:
        default_config_file = os.path.join(os.path.dirname(__file__),
                                           "conf_templates",
                                           "_config.yml.in")
        try:
            init_site = InitSite(default_config_file, target_path)
            init_site.init_site()
        except Exception as e:
            logging.exception("Init site: {0}\n{1}"
                              .format(unicode(e), traceback.format_exc()))
            sys.exit(1)
    else:
        config_file = os.path.join(target_path, "_config.yml")
        try:
            config = parse_config(config_file)
        except (Exception, YAMLError) as e:
            logging.exception("Parse config: {0}\n{1}"
                              .format(unicode(e), traceback.format_exc()))
            sys.exit(1)
        level = logging.DEBUG if config["debug"] else logging.INFO
        logging_init(level)   # reload logger

        if args["generate"]:
            if args["--ignore-root"]:
                config.update({u"root": u"/"})
            generator = Generator(config)
            generator.generate(args["--delete"])
        elif args["new"]:
            pocw = param_of_create_wiki(args["-t"], args["-c"], args["-f"],
                                        config["default_ext"])
            create_new_wiki(config["source"], *pocw)
        elif args["preview"]:
            preview(config["destination"])
        else:
            # docopt itself will display the help info.
            pass

    logger.info("Done.")

def main():
    args = docopt(__doc__, version="Simiki {0}".format(__version__))
    execute(args)

if __name__ == "__main__":
    main()
