#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import sys
import shutil
import logging
from os import path as osp
from pprint import pprint

from simiki.configs import parse_configs
from simiki.log import logging_init
from simiki.utils import (check_path_exists, copytree, mkdir_p, listdir_nohidden)

class InitSite(object):

    def __init__(self, config_file):
        self.config_file = config_file
        if not check_path_exists(self.config_file):
            logging.error("{} not exists".format(self.config_file))
            sys.exit(1)
        try:
            self.configs = parse_configs(self.config_file)
        except Exception as e:
            logging.error(str(e))
        self.current_dir = os.getcwd()

    def get_file(self, src, dst):
        if check_path_exists(dst):
            logging.warning("{} exists".format(dst))
            return

        # Create parent directory
        dst_directory = osp.dirname(dst)
        if not check_path_exists(dst_directory):
            mkdir_p(dst_directory)
            logging.info("Creating directory: {}".format(dst_directory))

        try:
            shutil.copyfile(src, dst)
            logging.info("Creating config file: {}".format(dst))
        except (shutil.Error, IOError), e:
            logging.error(str(e))

    def get_config_file(self):
        dst_config_file = osp.join(self.current_dir, "_config.yml")
        self.get_file(self.config_file, dst_config_file)

    def get_fabfile(self):
        src_fabfile = osp.join(
            osp.dirname(__file__),
            "conf_templates/fabfile.py"
        )
        dst_fabfile = osp.join(self.current_dir, "fabfile.py")
        self.get_file(src_fabfile, dst_fabfile)

    def get_first_page(self):
        nohidden_dir = listdir_nohidden(osp.join(self.current_dir, "content/"))
        # If there is directory under content, do not create first page
        if next(nohidden_dir, False):
            return

        src_fabfile = osp.join(
            osp.dirname(__file__),
            "conf_templates/gettingstarted.md"
        )
        dst_fabfile = osp.join(
            self.current_dir, 
            "content/intro/gettingstarted.md"
        )
        self.get_file(src_fabfile, dst_fabfile)

    def get_default_theme(self, theme_path):
        src_theme = osp.join(os.path.dirname(__file__), "themes")
        if osp.exists(theme_path):
            shutil.rmtree(theme_path)

        copytree(src_theme, theme_path)
        logging.info("Copying default theme to: {}".format(theme_path))

    def init_site(self):
        content_path = osp.join(self.current_dir, self.configs["source"])
        output_path = osp.join(self.current_dir, self.configs["destination"])
        theme_path = osp.join(self.current_dir, "themes")
        for path in (content_path, output_path, theme_path):
            if osp.exists(path):
                logging.warning("{} exists".format(path))
            else:
                os.mkdir(path)
                logging.info("Creating directory: {}".format(path))

        self.get_config_file()
        self.get_fabfile()
        self.get_first_page()
        self.get_default_theme(theme_path)

if __name__ == "__main__":
    logging_init(logging.DEBUG)
    BASE_DIR = os.getcwd()
    if len(sys.argv) == 1:
        config_file = osp.join(BASE_DIR, "_config.yml")
    elif len(sys.argv) == 2:
        config_file = osp.join(BASE_DIR, sys.argv[1])
    else:
        logging.error("Usage: `python -m simiki.configs [config.yml]'")
        sys.exit(1)

    i = InitSite(config_file)
    i.init_site()
