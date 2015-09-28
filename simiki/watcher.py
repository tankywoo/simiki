#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import logging
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import simiki
from simiki.generators import PageGenerator
from simiki.utils import write_file

_site_config = None
_base_path = None

class YAPatternMatchingEventHandler(PatternMatchingEventHandler):
    '''Observe .md files under content directory'''
    patterns = ['*.{0}'.format(e) for e in simiki.allowed_extensions]

    def process(self, event):
        pg = PageGenerator(_site_config, _base_path, event.src_path)
        html = pg.to_html()
        category, filename = os.path.split(event.src_path)
        category = os.path.relpath(category, _site_config['source'])
        output_fname = os.path.join(
            _base_path,
            _site_config['destination'],
            category,
            '{0}.html'.format(os.path.splitext(filename)[0])
        )
        write_file(output_fname, html)

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
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
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
