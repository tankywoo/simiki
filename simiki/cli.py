#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simiki CLI

Usage:
  simiki init [-p <path>]
  simiki new | n -t <title> -c <category> [-f <file>]
  simiki generate | g [--draft]
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
  -h, --help          Help information
  -V, --version       Show version
  -p <path>           Specify the target path
  -c <category>       Specify the category
  -t <title>          Specify the new post title
  -f <file>           Specify the new post filename
  --host <host>       Bind host to preview [default: 127.0.0.1]
  --port <port>       Bind port to preview [default: 8000]
  -w                  Auto regenerated when file changed
  --draft             Include draft pages to generate
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
import warnings

from docopt import docopt
from yaml import YAMLError

from simiki.generators import (PageGenerator, CatalogGenerator, FeedGenerator)
from simiki.initiator import Initiator
from simiki.config import parse_config
from simiki.log import logging_init
from simiki.server import preview
from simiki.watcher import watch
from simiki.updater import update_builtin
from simiki.utils import (copytree, emptytree, mkdir_p, write_file)
from simiki.compat import unicode, basestring, xrange
from simiki import __version__

try:
    from os import getcwdu
except ImportError:
    from os import getcwd as getcwdu

# Enable DeprecationWarning, etc.
warnings.simplefilter('default')

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


def method_proxy(cls_instance, method_name, *args, **kwargs):
    '''ref: http://stackoverflow.com/a/10217089/1276501'''
    return getattr(cls_instance, method_name)(*args, **kwargs)


class Generator(object):

    def __init__(self, target_path):
        self.config = config
        self.config.update({'version': __version__})
        self.target_path = target_path
        self.tags = {}
        self.pages = {}
        self.page_count = 0
        self.draft_count = 0
        self.include_draft = False

    def generate(self, include_draft=False):
        '''
        :include_draft: True/False, include draft pages or not to generate.
        '''
        self.include_draft = include_draft

        logger.debug("Empty the destination directory")
        dest_dir = os.path.join(self.target_path,
                                self.config["destination"])
        if os.path.exists(dest_dir):
            # for github pages and favicon.ico
            exclude_list = ['.git', 'CNAME', 'favicon.ico']
            emptytree(dest_dir, exclude_list)

        self.generate_tags()

        self.generate_pages()

        if not os.path.exists(os.path.join(self.config['source'], 'index.md')):
            self.generate_catalog(self.pages)

        feed_fn = 'atom.xml'
        if os.path.exists(os.path.join(getcwdu(), feed_fn)):
            self.generate_feed(self.pages, feed_fn)

        self.install_theme()

        self.copy_attach()

        # for default supported files to be copied to output/
        # CNAME for github pages with custom domain
        # TODO favicon can be other formats, such as .png, use glob match?
        for _fn in ('CNAME', 'favicon.ico'):
            _file = os.path.join(getcwdu(), _fn)
            if os.path.exists(_file):
                shutil.copy2(_file,
                             os.path.join(self.config['destination'], _fn))

    def generate_tags(self):
        g = PageGenerator(self.config, self.target_path)

        for root, dirs, files in os.walk(self.config["source"]):
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(self.config["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)

                g.src_file = md_file
                meta, _ = g.get_meta_and_content(do_render=False)
                _tags = meta.get('tag') or []  # if None
                for t in _tags:
                    self.tags.setdefault(t, []).append(meta)

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

        generate_result = ["Generate {0} pages".format(self.page_count)]
        # for draft pages and failed pages
        _err_npage = npage - self.page_count
        if self.include_draft:
            generate_result.append("include {0} drafts"
                                   .format(self.draft_count))
        else:
            _err_npage -= self.draft_count
            generate_result.append("ignore {0} drafts"
                                   .format(self.draft_count))
        if _err_npage:
            generate_result.append(" {0} pages failed".format(_err_npage))
        logger.info(', '.join(generate_result) + '.')

    def generate_multiple_pages(self, md_files):
        _pages = {}
        _page_count = 0
        _draft_count = 0
        page_generator = PageGenerator(self.config, self.target_path,
                                       self.tags)
        for _f in md_files:
            try:
                page_meta = self.generate_single_page(page_generator, _f)
                if page_meta:
                    _pages[_f] = page_meta
                    _page_count += 1
                    if page_meta.get('draft'):
                        _draft_count += 1
                else:
                    # XXX suppose page as draft if page_meta is None, this may
                    # cause error in the future
                    _draft_count += 1
            except Exception:
                page_meta = None
                logger.exception('{0} failed to generate:'.format(_f))
        return _pages, _page_count, _draft_count

    def generate_single_page(self, generator, md_file):
        logger.debug("Generate: {0}".format(md_file))
        html = generator.to_html(os.path.realpath(md_file),
                                 self.include_draft)

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
        meta = generator.meta
        meta['content'] = generator.content  # TODO
        return meta

    def _generate_callback(self, result):
        _pages, _page_count, _draft_count = result
        self.pages.update(_pages)
        self.page_count += _page_count
        self.draft_count += _draft_count

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
            generator.generate(include_draft=args['--draft'])
        elif args["new"] or args["n"]:
            create_new_wiki(args["-c"], args["-t"], args["-f"])
        elif args["preview"] or args["p"]:
            args['--port'] = int(args['--port'])
            preview_site(args['--host'], args['--port'], config['destination'],
                         config['root'], args['-w'])
        elif args["update"]:
            update_builtin(themes_dir=config['themes_dir'])
        else:
            # docopt itself will display the help info.
            pass

    logger.info("Done.")


if __name__ == "__main__":
    main()
