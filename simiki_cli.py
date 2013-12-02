#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

from os import path as osp

BASE_DIR = osp.dirname(osp.realpath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import simiki.utils
import simiki.configs
import simiki.gen

def build_dirs():
    content_path = simiki.configs.CONTENT_PATH
    output_path = simiki.configs.OUTPUT_PATH
    for path in (content_path, output_path):
        if osp.exists(path):
            print(simiki.utils.color_msg("warning", "[%s] exists." % path))
        else:
            os.mkdir(path)

def create_new_wiki():
    pass

def generate_single_page(md_file):
    pgen = simiki.gen.PageGenerator(md_file)
    #html = pgen.parse_markdown_file()
    html = pgen.markdown2html()
    pgen.output_to_file(html)
    #generate_catalog()

def generate_all_pages():
    content_path = simiki.configs.CONTENT_PATH

    for root, dirs, files in os.walk(content_path):
        for filename in files:
            if not simiki.utils.check_extension(filename):
                continue
            md_file = osp.join(root, filename)
            generate_single_page(md_file)
    #generate_catalog()

def generate_catalog():
    cgen = simiki.gen.CatalogGenerator(
            simiki.configs.BASE_DIR,
            simiki.configs.CONTENT_PATH, 
            simiki.configs.OUTPUT_PATH)
    cgen.update_catalog_page()

def generate():
    generate_all_pages()
    generate_catalog()

def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--build_dirs", action="store_true", dest="build_dirs", help="")
    parser.add_argument("-f", "--file", dest="md_file", help="")
    parser.add_argument("--all", action="store_true", dest="all_files", help="")
    parser.add_argument("--generate_catalog", action="store_true", dest="generate_catalog", help="")
    parser.add_argument("--generate", action="store_true", dest="generate", help="")
    parser.add_argument("--debug", action="store_true", dest="debug_mode", help="")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    md_file = args.md_file
    all_files = args.all_files

    if args.build_dirs:
        build_dirs()
        sys.exit(1)

    if args.generate_catalog:
        generate_catalog()
        sys.exit(1)

    if md_file:
        md_file = osp.realpath(args.md_file)
        generate_single_page(md_file)
    else:
        generate_all_pages()

    if args.generate:
        generate()
