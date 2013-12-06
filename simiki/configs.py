#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path as osp
from pprint import pprint

import yaml

def parse_configs(config_file):
    base_dir = osp.dirname(osp.dirname(osp.realpath(__file__)))
    try:
        with open(config_file, "rb") as fd:
            configs = yaml.load(fd)
    except IOError, e:
        print(str(e))
    configs.update(
        base_dir = base_dir,
        # The directory to store markdown files
        source = osp.join(base_dir, configs["source"]),
        # The directory to store the generated html files
        destination = osp.join(base_dir,  configs["destination"]),
        # The path of html template file
        tpl_path = osp.join(base_dir, "simiki/themes", configs["theme"]),
    )

    return configs

if __name__ == "__main__":
    BASE_DIR = osp.dirname(osp.dirname(osp.realpath(__file__)))
    config_file = osp.join(BASE_DIR, "_config.yml")
    pprint(parse_configs(config_file))
