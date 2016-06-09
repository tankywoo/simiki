#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import logging
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import simiki
from simiki.generators import PageGenerator, CatalogGenerator
from simiki.utils import write_file

_site_config = None
_base_path = None


class YAPatternMatchingEventHandler(PatternMatchingEventHandler):
    '''Observe .md files under content directory.
    Temporary only regenerate, not delete unused files'''
    patterns = ['*.{0}'.format(e) for e in simiki.allowed_extensions]

    @staticmethod
    def generate_page(_file):
        pg = PageGenerator(_site_config, _base_path)
        html = pg.to_html(_file)
        # ignore draft
        if not html:
            return None

        category, filename = os.path.split(_file)
        category = os.path.relpath(category, _site_config['source'])
        output_fname = os.path.join(
            _base_path,
            _site_config['destination'],
            category,
            '{0}.html'.format(os.path.splitext(filename)[0])
        )
        write_file(output_fname, html)
        logging.debug('Regenerating: {0}'.format(_file))

    @staticmethod
    def generate_catalog():
        pg = PageGenerator(_site_config, _base_path)
        pages = {}

        for root, dirs, files in os.walk(_site_config["source"]):
            files = [f for f in files if not f.startswith(".")]
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                if not filename.endswith(_site_config["default_ext"]):
                    continue
                md_file = os.path.join(root, filename)
                pg.src_file = md_file
                meta, _ = pg.get_meta_and_content(do_render=False)
                pages[md_file] = meta

        cg = CatalogGenerator(_site_config, _base_path, pages)
        html = cg.generate_catalog_html()
        ofile = os.path.join(
            _base_path,
            _site_config['destination'],
            "index.html"
        )
        write_file(ofile, html)
        logging.debug('Regenerating catalog')

    def process(self, event):
        if event.event_type in ('moved',):
            _file = event.dest_path
        else:
            _file = event.src_path

        if event.event_type not in ('deleted',):
            self.generate_page(_file)

        self.generate_catalog()

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

    def on_moved(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)


def watch(site_config, base_path):
    global _site_config, _base_path
    _site_config = site_config
    _base_path = base_path

    observe_path = os.path.join(_base_path, _site_config['source'])
    event_handler = YAPatternMatchingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, observe_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down watcher")
        observer.stop()
    observer.join()
