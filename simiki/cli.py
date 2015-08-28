#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init [-p <path>]
  simiki new -t <title> -c <category> [-f <file>]
  simiki generate
  simiki preview [--host <host>] [--port <port>]
  simiki -h | --help
  simiki -V | --version

Options:
  -h, --help          Help information.
  -V, --version       Show version.
  -p <path>           Specify the target path.
  -c <category>       Specify the category.
  -t <title>          Specify the new post title.
  -f <file>           Specify the new post filename.
  --host <host>       bind host to preview [default: localhost]
  --port <port>       bind port to preview [default: 8000]
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

from simiki.generators import (PageGenerator, CatalogGenerator)
from simiki.initiator import Initiator
from simiki.config import parse_config
from simiki.log import logging_init
from simiki.server import preview
from simiki.utils import (copytree, emptytree, mkdir_p)
from simiki import __version__

logger = logging.getLogger(__name__)
config = None


def init_site(target_path):
    default_config_file = os.path.join(os.path.dirname(__file__),
                                       "conf_templates",
                                       "_config.yml.in")
    try:
        initiator = Initiator(default_config_file, target_path)
        initiator.init()
    except Exception as e:
        # always in debug mode when init site
        logging.exception("Initialize site with error:")
        sys.exit(1)


def create_new_wiki(category, title, filename):
    if not filename:
        # `/` can't exists in filename
        _title = title.replace(os.sep, " slash ").lower()
        filename = "{0}.{1}".format(_title.replace(' ', '-'),
                                    config["default_ext"])
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    meta = "\n".join([
        "---",
        "title: \"{0}\"".format(title),
        "date: {0}".format(now),
        "---",
    ]) + "\n\n"

    category_path = os.path.join(config["source"], category)
    if not os.path.exists(category_path):
        mkdir_p(category_path)
        logger.info("Creating category: {0}.".format(category))

    fn = os.path.join(category_path, filename)
    if os.path.exists(fn):
        logger.warning("File exists: {0}".format(fn))
    else:
        logger.info("Creating wiki: {0}".format(fn))
        with io.open(fn, "wt", encoding="utf-8") as fd:
            fd.write(meta)


class Generator(object):

    def __init__(self, target_path):
        self.config = config
        self.target_path = target_path
        self.pages = {}

    def generate(self):
        logger.debug("Empty the destination directory")
        dest_dir = os.path.join(self.target_path,
                                self.config["destination"])
        if os.path.exists(dest_dir):
            # for github pages
            exclude_list = ['.git', 'CNAME']
            emptytree(dest_dir, exclude_list)

        self.generate_pages()

        if not os.path.exists(os.path.join(self.config['source'], 'index.md')):
            self.generate_catalog(self.pages)

        self.install_theme()

        self.copy_attach()

    def generate_catalog(self, pages):
        logger.info("Generate catalog page.")
        catalog_generator = CatalogGenerator(self.config, self.target_path,
                                             pages)
        html = catalog_generator.generate_catalog_html()
        ofile = os.path.join(
            self.target_path,
            self.config["destination"],
            "index.html"
        )
        self.write_file(html, ofile)

    def generate_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.config["source"]

        page_count = 0
        for root, dirs, files in os.walk(content_path):
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(self.config["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)
                try:
                    page_meta = self.generate_single_page(md_file)
                except Exception as e:
                    log_msg = ''
                    if 'extra_msg' in dir(e):
                        log_msg = e.extra_msg
                    if config.get('debug', False):
                        logger.exception('{0}: {1}'.format(md_file, log_msg))
                    else:
                        if log_msg:
                            log_msg = ', '.join((log_msg, unicode(e)))
                        else:
                            log_msg = unicode(e)
                        logger.error('{0}: {1}'.format(md_file, log_msg))
                    continue
                if page_meta:
                    self.pages[md_file] = page_meta
                    page_count += 1
        logger.info("{0} files generated.".format(page_count))

    def generate_single_page(self, md_file):
        logger.debug("Generate: {0}".format(md_file))
        page_generator = PageGenerator(self.config, self.target_path,
                                       os.path.realpath(md_file))
        html = page_generator.to_html()

        # ignore draft
        if not html:
            return None

        category, filename = os.path.split(md_file)
        category = os.path.relpath(category, self.config['source'])
        output_file = os.path.join(
            self.target_path,
            self.config['destination'],
            category,
            '{0}.html'.format(os.path.splitext(filename)[0])
        )

        self.write_file(html, output_file)
        meta = page_generator.meta
        return meta

    def install_theme(self):
        """Copy static directory under theme to destination directory"""
        src_theme = os.path.join(self.target_path, self.config["themes_dir"],
                                 self.config["theme"], "static")
        dest_theme = os.path.join(self.target_path, self.config["destination"],
                                  "static")
        if os.path.exists(dest_theme):
            shutil.rmtree(dest_theme)

        copytree(src_theme, dest_theme)
        logging.debug("Installing theme: {0}".format(self.config["theme"]))

    def copy_attach(self):
        """Copy attach directory under root path to destination directory"""
        src_p = os.path.join(self.target_path, self.config['attach'])
        dest_p = os.path.join(self.target_path, self.config["destination"],
                              self.config['attach'])
        if os.path.exists(src_p):
            copytree(src_p, dest_p)

    @staticmethod
    def write_file(content, output_fname):
        """Write content to output file."""
        output_dir, _ = os.path.split(output_fname)
        if not os.path.exists(output_dir):
            logging.debug("The output directory %s not exists, create it",
                          output_dir)
            mkdir_p(output_dir)
        with io.open(output_fname, "wt", encoding="utf-8") as fd:
            fd.write(content)


def unicode_docopt(args):
    for k in args:
        if isinstance(args[k], basestring) and \
           not isinstance(args[k], unicode):
            args[k] = args[k].decode('utf-8')


def execute(args):
    global config

    logging_init(logging.DEBUG)

    target_path = args['-p'] if args['-p'] else os.getcwdu()

    if args["init"]:
        init_site(target_path)
        return

    config_file = os.path.join(target_path, "_config.yml")
    try:
        config = parse_config(config_file)
    except (Exception, YAMLError) as e:
        # always in debug mode when parse config
        logging.exception("Parse config with error:")
        sys.exit(1)
    level = logging.DEBUG if config["debug"] else logging.INFO
    logging_init(level)   # reload logger

    if args["generate"]:
        generator = Generator(target_path)
        generator.generate()
    elif args["new"]:
        create_new_wiki(args["-c"], args["-t"], args["-f"])
    elif args["preview"]:
        args['--port'] = int(args['--port'])
        preview(config["destination"], config['root'],
                args["--host"], args["--port"])
    else:
        # docopt itself will display the help info.
        pass


def main():
    args = docopt(__doc__, version="Simiki {0}".format(__version__))
    unicode_docopt(args)

    execute(args)

    logger.info("Done.")


if __name__ == "__main__":
    main()
