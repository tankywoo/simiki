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


def _set_default_configs():
    configs = {
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
    return configs


def _post_process(configs):
    for k, v in configs.items():
        if v is None:
            configs[k] = ""

    if configs["url"].endswith("/"):
        configs["url"] = configs["url"][:-1]

    return configs


def parse_configs(config_file):
    if not os.path.exists(config_file):
        raise Exception("{0} not exists".format(config_file))

    default_configs = _set_default_configs()

    with io.open(config_file, "rt", encoding="utf-8") as fd:
        configs = yaml.load(fd)

    default_configs.update(configs)
    configs = _post_process(deepcopy(default_configs))

    return configs

if __name__ == "__main__":
    """
    Usage:
        python -m simiki.configs : to test config template
        python -m simiki.configs _config.yml : to test _config.yml file in \
                                                curren dir
    """
    if len(sys.argv) == 1:
        base_dir = os.path.dirname(__file__)
        config_file = os.path.join(base_dir, "conf_templates/_config.yml.in")
    elif len(sys.argv) == 2:
        base_dir = os.getcwd()
        config_file = os.path.join(base_dir, sys.argv[1])
    else:
        logging.error("Use the template config file by default, "
                      "you can specify the config file to parse. \n"
                      "Usage: `python -m simiki.configs [_config.yml]'")
        sys.exit(1)

    pprint(parse_configs(config_file))
