#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import os.path
import sys
import io
import logging
from copy import deepcopy
from pprint import pprint
import yaml


class ConfigFileNotFound(Exception):
    pass

def _set_default_config():
    config = {
        "url": "",
        "title": "",
        "keywords": "",
        "description": "",
        "author": "",
        "root": "/",
        "source": "content",
        "destination": "output",
        "themes_dir": "themes",
        "theme": "simple",
        "default_ext": "md",
        "pygments": True,
        "debug": False,
        "index": False
    }
    return config


def _post_process(config):
    for k, v in config.items():
        if v is None:
            config[k] = ""

    if config["url"].endswith("/"):
        config["url"] = config["url"][:-1]

    return config


def parse_config(config_file):
    if not os.path.exists(config_file):
        raise ConfigFileNotFound("{0} not exists".format(config_file))

    default_config = _set_default_config()

    with io.open(config_file, "rt", encoding="utf-8") as fd:
        config = yaml.load(fd)

    default_config.update(config)
    config = _post_process(deepcopy(default_config))

    return config

if __name__ == "__main__":
    """
    Usage:
        python -m simiki.config : to test config template
        python -m simiki.config _config.yml : to test _config.yml file in \
                                                curren dir
    """
    if len(sys.argv) == 1:
        base_dir = os.path.dirname(__file__)
        config_file = os.path.join(base_dir, "conf_templates", "_config.yml.in")
    elif len(sys.argv) == 2:
        base_dir = os.getcwd()
        config_file = os.path.join(base_dir, sys.argv[1])
    else:
        logging.error("Use the template config file by default, "
                      "you can specify the config file to parse. \n"
                      "Usage: `python -m simiki.config [_config.yml]'")
        sys.exit(1)

    pprint(parse_config(config_file))
