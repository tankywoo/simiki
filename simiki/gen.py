#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Markdown file to html, which is embeded in html template.
"""

from __future__ import print_function, with_statement, unicode_literals

import os
import sys
import codecs
from os import path as osp

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

from simiki import configs
from simiki import utils

class PageGenerator(object):

    def __init__(self, md_file):
        """
        :param md_file: The path of markdown file
        """
        self.md_file = osp.realpath(md_file)

    def get_catalog_and_md_name(self):
        """Get the subdir's name and markdown file's name."""
        catalog_name = self.md_file.split("/")[-2] # html subdir
        md_name = self.md_file.split("/")[-1].split(".")[0]
        return (catalog_name, md_name)

    def split_meta_and_content(self):
        """Split the markdown file texts by triple-dashed lines.

        The content in the middle of triple-dashed lines is meta datas, which 
            use Yaml format.
        The other content is the markdown texts.
        """
        with codecs.open(self.md_file, "rb", "utf-8") as fd:
            text_lists = fd.readlines()

        meta_notation = "---\n"
        if text_lists[0] != meta_notation:
            print(utils.color_msg("error", "First line must be triple-dashed!"))
            sys.exit(1)

        meta_lists = []
        meta_end_flag = False
        idx = 1
        while not meta_end_flag:
            meta_lists.append(text_lists[idx])
            idx += 1
            if text_lists[idx] == meta_notation:
                meta_end_flag = True
        content_lists = text_lists[idx+1:]
        meta_yaml = "".join(meta_lists)
        contents = "".join(content_lists)
        return (meta_yaml, contents)

    def get_meta_datas(self, meta_yaml):
        """Get meta datas and validate them

        :param meta_yaml: Meta info in yaml format
        """
        meta_datas = yaml.load(meta_yaml)
        for m in ("Title", "Date"):
            if m not in meta_datas:
                print(utils.color_msg("error", "No '%s' in meta data!" % m))
                sys.exit(1)
        return meta_datas

    def markdown2html(self, title, contents):
        """Generate the html from md file, and embed it in html template"""
        body_content = markdown.markdown(contents, \
                extensions=["fenced_code", "codehilite(guess_lang=False)"])

        env = Environment(loader = FileSystemLoader(configs.TPL_PATH))
        tpl_vars = {
            "wiki_name" : configs.WIKI_NAME,
            "wiki_keywords" : configs.WIKI_KEYWORDS,
            "wiki_description" : configs.WIKI_DESCRIPTION,
            "title" : title,
            "content" : body_content,
        }
        html = env.get_template('index.html').render(tpl_vars)

        return html

    def parse_markdown_file(self):
        """Parse wiki file and generate html"""
        meta_yaml, contents = self.split_meta_and_content()
        meta_datas = self.get_meta_datas(meta_yaml)
        title = meta_datas["Title"]
        html = self.markdown2html(title, contents)
        return html

    def output_to_file(self, html):
        """Write generated html to file"""
        catalog_name, md_name = self.get_catalog_and_md_name()
        output_catalog_path = osp.join(configs.OUTPUT_PATH, catalog_name)
        if not utils.check_path_exists(output_catalog_path):
            print(utils.color_msg(
                "info", 
                ("The output catalog %s not exists, " % output_catalog_path,
                 "create it")
                )
            )
            os.mkdir(output_catalog_path)
        output_file = osp.join(output_catalog_path, md_name+".html")
        with codecs.open(output_file, "wb", "utf-8") as fd:
            fd.write(html)
