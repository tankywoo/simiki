#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init [-p <path>]
  simiki new -t <title> -c <category> [-f <file>]
  simiki generate [--delete]
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
  --delete            Delete the contents of output directory before generate.
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
from simiki.configs import parse_configs
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
    category = category.decode("utf-8")
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
                "The output category %s not exists, create it"
                % output_category
            )
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
    """Copy static directory under theme to output directory"""
    src_theme = os.path.join(
        current_dir,
        "themes/{0}/static".format(theme_name)
    )
    dst_theme = os.path.join(current_dir, "output/static")
    if os.path.exists(dst_theme):
        shutil.rmtree(dst_theme)

    copytree(src_theme, dst_theme)
    logging.info("Installing theme: {0}".format(theme_name))


class Generator(object):

    def __init__(self, configs):
        self.configs = configs
        self.target_path = unicode(os.getcwd(), "utf-8")

    def generate(self, delete_output_dir=False):
        if delete_output_dir:
            logger.info("Delete all the files and dirs under output directory")
            output_dir = os.path.join(self.target_path,
                                      self.configs["destination"])
            emptytree(output_dir)

        pages = self.generate_all_pages()
        self.generate_catalog(pages)
        install_theme(self.target_path, self.configs["theme"])

    def generate_all_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.configs["source"]

        pcnt = 0
        pages = {}
        for root, dirs, files in os.walk(content_path):
            files = [f for f in files if not f.decode("utf-8").startswith(".")]
            dirs[:] = [
                d for d in dirs if not d.decode("utf-8").startswith(".")
            ]
            for filename in files:
                if not filename.endswith(self.configs["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)
                pages[md_file] = self.generate_single_page(md_file)
                pcnt += 1
        logger.info("{0} files generated.".format(pcnt))
        return pages

    def generate_single_page(self, md_file):
        md_file = md_file.decode('utf8')
        logger.debug("Generate {0}".format(md_file))
        pgen = PageGenerator(
            self.configs,
            self.target_path,
            os.path.realpath(md_file)
        )
        try:
            html = pgen.markdown2html()
        except Exception as e:
            logger.exception("{0}\n{1}".format(str(e), traceback.format_exc()))
            sys.exit(1)

        def get_ofile():
            scategory, fname = os.path.split(md_file)
            ofname = "{0}.html".format(os.path.splitext(fname)[0])
            category = os.path.relpath(scategory, self.configs["source"])
            ocategory = os.path.join(
                self.target_path, self.configs["destination"], category
            )
            ofile = os.path.join(ocategory, ofname)
            return ofile

        ofile = get_ofile()
        write_file(html, ofile)
        meta_data, _ = pgen.get_metadata_and_content()
        return meta_data

    def generate_catalog(self, pages):
        logger.info("Generate catalog page.")
        if self.configs["index"]:
            cgen = CustomCatalogGenerator(self.configs, self.target_path, None)
        else:
            cgen = CatalogGenerator(self.configs, self.target_path, pages)
        html = cgen.generate_catalog_html()
        ofile = os.path.join(
            self.target_path,
            self.configs["destination"],
            "index.html"
        )
        write_file(html, ofile, "index")


def execute(args):
    logging_init(logging.DEBUG)

    target_path = os.getcwd()
    if args["-p"]:
        target_path = args["-p"]
    if not isinstance(target_path, unicode):
        target_path = unicode(target_path, "utf-8")

    if args["init"]:
        default_config_file = os.path.join(os.path.dirname(__file__),
                                           "conf_templates",
                                           "_config.yml.in")
        try:
            isite = InitSite(default_config_file, target_path)
            isite.init_site()
        except Exception as e:
            logging.exception("{0}\n{1}"
                              .format(str(e), traceback.format_exc()))
        return

    config_file = os.path.join(target_path, "_config.yml")
    try:
        configs = parse_configs(config_file)
    except (Exception, YAMLError) as e:
        logging.exception("{0}\n{1}".format(str(e), traceback.format_exc()))
        return
    level = logging.DEBUG if configs["debug"] else logging.INFO
    logging_init(level)

    if args["generate"]:
        gen = Generator(configs)
        gen.generate(args["--delete"])
    elif args["new"] and args["-t"]:
        pocw = param_of_create_wiki(args["-t"], args["-c"], args["-f"],
                                    configs["default_ext"])
        create_new_wiki(configs["source"], *pocw)
    elif args["preview"]:
        preview(configs["destination"])
    else:
        # docopt itself will display the help info.
        pass

    logger.info("Done.")

def main():
    args = docopt(__doc__, version="Simiki {0}".format(__version__))
    execute(args)

if __name__ == "__main__":
    main()
