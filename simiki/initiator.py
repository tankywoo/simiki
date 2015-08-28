#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
import os.path
import shutil
import logging

from simiki.config import parse_config
from simiki.utils import (copytree, mkdir_p, listdir_nohidden)


class Initiator(object):
    conf_template_dn = "conf_templates"
    config_fn = "_config.yml"
    fabfile_fn = "fabfile.py"
    demo_fn = "gettingstarted.md"

    def __init__(self, config_file, target_path):
        self.config_file = config_file
        self.config = parse_config(self.config_file)
        self.source_path = os.path.dirname(__file__)
        self.target_path = target_path

    @staticmethod
    def get_file(src, dst):
        if os.path.exists(dst):
            logging.warning("{0} exists".format(dst))
            return

        # Create parent directory
        dst_directory = os.path.dirname(dst)
        if not os.path.exists(dst_directory):
            mkdir_p(dst_directory)
            logging.info("Creating directory: {0}".format(dst_directory))

        shutil.copyfile(src, dst)
        logging.info("Creating file: {0}".format(dst))

    def get_config_file(self):
        dst_config_file = os.path.join(self.target_path, self.config_fn)
        self.get_file(self.config_file, dst_config_file)

    def get_fabfile(self):
        src_fabfile = os.path.join(
            self.source_path,
            self.conf_template_dn,
            self.fabfile_fn
        )
        dst_fabfile = os.path.join(self.target_path, self.fabfile_fn)
        self.get_file(src_fabfile, dst_fabfile)

    def get_demo_page(self):
        nohidden_dir = listdir_nohidden(
            os.path.join(self.target_path, self.config['source']))
        # If there is file/directory under content, do not create first page
        if next(nohidden_dir, False):
            return

        src_demo = os.path.join(self.source_path, self.conf_template_dn,
                                self.demo_fn)
        dst_demo = os.path.join(self.target_path, "content", "intro",
                                self.demo_fn)
        self.get_file(src_demo, dst_demo)

    def get_default_theme(self, theme_path):
        default_theme_name = self.config['theme']
        src_theme = os.path.join(self.source_path, self.config['themes_dir'],
                                 default_theme_name)
        dst_theme = os.path.join(theme_path, default_theme_name)
        if os.path.exists(dst_theme):
            logging.warning('{0} exists'.format(dst_theme))
        else:
            copytree(src_theme, dst_theme)
            logging.info("Copying default theme '{0}' to: {1}"
                         .format(default_theme_name, theme_path))

    def init(self):
        content_path = os.path.join(self.target_path, self.config["source"])
        output_path = os.path.join(self.target_path,
                                   self.config["destination"])
        theme_path = os.path.join(self.target_path, self.config['themes_dir'])
        for path in (content_path, output_path, theme_path):
            if os.path.exists(path):
                logging.warning("{0} exists".format(path))
            else:
                mkdir_p(path)
                logging.info("Creating directory: {0}".format(path))

        self.get_config_file()
        self.get_fabfile()
        self.get_demo_page()
        self.get_default_theme(theme_path)
