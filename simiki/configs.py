#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from os import path as osp
from pprint import pprint

import yaml

from simiki.utils import check_path_exists

def parse_configs(config_file):
    base_dir = osp.dirname(osp.dirname(osp.realpath(__file__)))

    if not check_path_exists(config_file):
        logging.error("{} not exists".format(config_file))
        sys.exit(1)

    try:
        with open(config_file, "rb") as fd:
            configs = yaml.load(fd)
    except yaml.YAMLError, e:
        msg = "Yaml format error in {}:\n{}".format(
                config_file,
                unicode(str(e), "utf-8")
            )
        logging.error(msg)
        sys.exit(1)

    if configs["base_dir"] is None:
        configs["base_dir"] = osp.dirname(osp.realpath(config_file))

    configs.update(
        # The directory to store markdown files
        source = osp.join(configs["base_dir"], configs["source"]),
        # The directory to store the generated html files
        destination = osp.join(configs["base_dir"],  configs["destination"]),
        # The path of html template file
        tpl_path = osp.join(base_dir, "simiki/themes", configs["theme"]),
    )

    if not configs.get("url", ""):
        configs["url"] = ""
    elif configs["url"].endswith("/"):
        configs["url"] = configs["url"][:-1]
    else:
        pass

    if not configs.get("keywords", ""):
        configs["keywords"] = ""

    if not configs.get("description", ""):
        configs["description"] = ""

    return configs

if __name__ == "__main__":
    BASE_DIR = osp.realpath(".")
    if len(sys.argv) == 1:
        config_file = osp.join(BASE_DIR, "_config.yml")
    elif len(sys.argv) == 2:
        config_file = osp.join(BASE_DIR, sys.argv[1])
    else:
        logging.error("Usage: `python -m simiki.configs [config.yml]'")
        sys.exit(1)
        
    pprint(parse_configs(config_file))
