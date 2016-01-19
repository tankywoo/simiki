#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init [-p <path>]
  simiki new | n -t <title> -c <category> [-f <file>]
  simiki generate | g
  simiki preview | p [--host <host>] [--port <port>] [-w]
  simiki update
  simiki -h | --help
  simiki -V | --version

Subcommands:
  init                Initial site
  new                 Create a new wiki page
  generate            Generate site
  preview             Preview site locally (develop mode)
  update              Update builtin scripts and themes under local site

Options:
  -h, --help          Help information.
  -V, --version       Show version.
  -p <path>           Specify the target path.
  -c <category>       Specify the category.
  -t <title>          Specify the new post title.
  -f <file>           Specify the new post filename.
  --host <host>       Bind host to preview [default: localhost]
  --port <port>       Bind port to preview [default: 8000]
  -w                  Auto regenerated when file changed
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import os.path
import sys
import io
import datetime
import shutil
import logging
import random
import multiprocessing
import time
import hashlib

from docopt import docopt
from yaml import YAMLError

from simiki.generators import (PageGenerator, CatalogGenerator, FeedGenerator)
from simiki.initiator import Initiator
from simiki.config import parse_config
from simiki.log import logging_init
from simiki.server import preview
from simiki.watcher import watch
from simiki.utils import (copytree, emptytree, mkdir_p, write_file)
from simiki import __version__
from simiki.compat import unicode, basestring, xrange, raw_input

try:
    from os import getcwdu
except ImportError:
    from os import getcwd as getcwdu

logger = logging.getLogger(__name__)
config = None


def init_site(target_path):
    default_config_file = os.path.join(os.path.dirname(__file__),
                                       "conf_templates",
                                       "_config.yml.in")
    try:
        initiator = Initiator(default_config_file, target_path)
        initiator.init()
    except Exception:
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


def preview_site(host, port, dest, root, do_watch):
    '''Preview site with watch content'''
    p_server = multiprocessing.Process(
        target=preview,
        args=(dest, root, host, port),
        name='ServerProcess'
    )
    p_server.start()

    if do_watch:
        base_path = getcwdu()
        p_watcher = multiprocessing.Process(
            target=watch,
            args=(config, base_path),
            name='WatcherProcess'
        )
        p_watcher.start()

    try:
        while p_server.is_alive():
            time.sleep(1)
        else:
            if do_watch:
                p_watcher.terminate()
    except (KeyboardInterrupt, SystemExit):
        # manually terminate process?
        pass


def update_builtin():
    '''Update builtin scripts and themes under local site'''
    # for fabfile.py
    yes_ans = ('y', 'yes')
    _fabfile_r = os.path.join(os.path.dirname(__file__), 'conf_templates',
                              'fabfile.py')
    _fabfile_l = os.path.join(os.getcwd(), 'fabfile.py')
    if os.path.exists(_fabfile_l):
        # py3 require md5 with bytes object, otherwise raise
        # TypeError: Unicode-objects must be encoded before hashing
        with open(_fabfile_r, 'rb') as _fd:
            _fabfile_r_md5 = hashlib.md5(_fd.read()).hexdigest()
        with open(_fabfile_l, 'rb') as _fd:
            _fabfile_l_md5 = hashlib.md5(_fd.read()).hexdigest()
        if _fabfile_l_md5 != _fabfile_r_md5:
            try:
                _ans = raw_input('Overwrite fabfile.py? (y/N) ')
                if _ans.lower() in yes_ans:
                    shutil.copy2(_fabfile_r, _fabfile_l)
            except (KeyboardInterrupt, SystemExit):
                print()  # newline with Ctrl-C
    else:
        try:
            _ans = raw_input('New fabfile.py? (y/N) ')
            if _ans.lower() in yes_ans:
                shutil.copy2(_fabfile_r, _fabfile_l)
        except (KeyboardInterrupt, SystemExit):
            print()

    # for themes
    _themes_r = os.path.join(os.path.dirname(__file__), 'themes')
    _themes_l = os.path.join(os.getcwd(), config['themes_dir'])
    for theme in os.listdir(_themes_r):
        _theme_r = os.path.join(_themes_r, theme)
        _theme_l = os.path.join(_themes_l, theme)
        if os.path.exists(_theme_l):
            _need_update = False
            for root, dirs, files in os.walk(_theme_r):
                files = [f for f in files if not f.startswith(".")]
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for filename in files:
                    with open(os.path.join(root, filename), 'rb') as _fd:
                        _theme_r_md5 = hashlib.md5(_fd.read()).hexdigest()
                    _dir = os.path.relpath(root, _theme_r)
                    with open(os.path.join(_theme_l, _dir, filename),
                              'rb') as _fd:
                        _theme_l_md5 = hashlib.md5(_fd.read()).hexdigest()
                    if _theme_l_md5 != _theme_r_md5:
                        _need_update = True
                        break
                if _need_update:
                    break
            if _need_update:
                try:
                    _ans = raw_input('Overwrite theme {0}? (y/N) '
                                     .format(theme))
                    if _ans.lower() in yes_ans:
                        shutil.rmtree(_theme_l)
                        copytree(_theme_r, _theme_l)
                except (KeyboardInterrupt, SystemExit):
                    print()
        else:
            try:
                _ans = raw_input('New theme {0}? (y/N) '.format(theme))
                if _ans.lower() in yes_ans:
                    copytree(_theme_r, _theme_l)
            except (KeyboardInterrupt, SystemExit):
                print()


def method_proxy(cls_instance, method_name, *args, **kwargs):
    '''ref: http://stackoverflow.com/a/10217089/1276501'''
    return getattr(cls_instance, method_name)(*args, **kwargs)


class Generator(object):

    def __init__(self, target_path):
        self.config = config
        self.config.update({'version': __version__})
        self.target_path = target_path
        self.pages = {}
        self.page_count = 0

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

        feed_fn = 'atom.xml'
        if os.path.exists(os.path.join(getcwdu(), feed_fn)):
            self.generate_feed(self.pages, feed_fn)

        self.install_theme()

        self.copy_attach()

        # for github pages with custom domain
        cname_file = os.path.join(getcwdu(), 'CNAME')
        if os.path.exists(cname_file):
            shutil.copy2(cname_file,
                         os.path.join(self.config['destination'], 'CNAME'))

    def generate_feed(self, pages, feed_fn):
        logger.info("Generate feed.")
        feed_generator = FeedGenerator(self.config, self.target_path, pages,
                                       feed_fn)
        feed = feed_generator.generate_feed()
        ofile = os.path.join(
            self.target_path,
            self.config["destination"],
            feed_fn
        )
        write_file(ofile, feed)

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
        write_file(ofile, html)

    def generate_pages(self):
        logger.info("Start generating markdown files.")
        content_path = self.config["source"]
        _pages_l = []

        for root, dirs, files in os.walk(content_path):
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(self.config["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)
                _pages_l.append(md_file)

        npage = len(_pages_l)
        if npage:
            nproc = min(multiprocessing.cpu_count(), npage)

            split_pages = [[] for n in xrange(0, nproc)]
            random.shuffle(_pages_l)

            for i in xrange(npage):
                split_pages[i % nproc].append(_pages_l[i])

            pool = multiprocessing.Pool(processes=nproc)
            results = []
            for n in xrange(nproc):
                r = pool.apply_async(
                    method_proxy,
                    (self, 'generate_multiple_pages', split_pages[n]),
                    callback=self._generate_callback
                )
                results.append(r)

            pool.close()
            for r in results:
                r.get()

        generate_result = "{0} files generated.".format(self.page_count)
        # for failed pages
        _err_npage = npage - self.page_count
        if _err_npage:
            generate_result += " {0} files failed.".format(_err_npage)
        logger.info(generate_result)

    def generate_multiple_pages(self, md_files):
        _pages = {}
        _page_count = 0
        for _f in md_files:
            try:
                page_meta = self.generate_single_page(_f)
            except Exception:
                page_meta = None
                logger.exception('{0} failed to generate:'.format(_f))
            if page_meta:
                _pages[_f] = page_meta
                _page_count += 1
        return _pages, _page_count

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

        write_file(output_file, html)
        meta = page_generator.meta
        return meta

    def _generate_callback(self, result):
        _pages, _count = result
        self.pages.update(_pages)
        self.page_count += _count

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


def unicode_docopt(args):
    for k in args:
        if isinstance(args[k], basestring) and \
           not isinstance(args[k], unicode):
            args[k] = args[k].decode('utf-8')


def main(args=None):
    global config

    if not args:
        args = docopt(__doc__, version="Simiki {0}".format(__version__))
    unicode_docopt(args)

    logging_init(logging.DEBUG)

    target_path = args['-p'] if args['-p'] else getcwdu()

    if args["init"]:
        init_site(target_path)
    else:
        config_file = os.path.join(target_path, "_config.yml")
        try:
            config = parse_config(config_file)
        except (Exception, YAMLError):
            # always in debug mode when parse config
            logging.exception("Parse config with error:")
            sys.exit(1)
        level = logging.DEBUG if config["debug"] else logging.INFO
        logging_init(level)   # reload logger

        if args["generate"] or args["g"]:
            generator = Generator(target_path)
            generator.generate()
        elif args["new"] or args["n"]:
            create_new_wiki(args["-c"], args["-t"], args["-f"])
        elif args["preview"] or args["p"]:
            args['--port'] = int(args['--port'])
            preview_site(args['--host'], args['--port'], config['destination'],
                         config['root'], args['-w'])
        elif args["update"]:
            update_builtin()
        else:
            # docopt itself will display the help info.
            pass

    logger.info("Done.")


if __name__ == "__main__":
    main()
