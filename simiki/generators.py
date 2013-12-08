#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Markdown file to html, which is embeded in html template.
"""

from __future__ import print_function, with_statement, unicode_literals

import os
import sys
import codecs
import datetime
import logging
from os import path as osp
from pprint import pprint

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

from simiki import utils

# python No handlers could be found for logger
logger = logging.getLogger(__name__)

class BaseGenerator(object):
    def __init__(self, site_settings):
        self.site_settings = site_settings
        self.env = Environment(
            loader = FileSystemLoader(site_settings["tpl_path"])
        )

    def get_catalog_and_mdown(self, mdown_file):
        """Get the catalog's and markdown's(with extension) name.

        :param mdown_file: TODO

        e.g: 
            mdown_file is /home/user/simiki/content/python/test.md
            catalog = python
            mdown = test.md
        """
        # @todo, if path with `/`?
        split_path = mdown_file.split("/")
        mdown, catalog = split_path[-1], split_path[-2]

        return (catalog, mdown)

    def get_meta_and_content(self, mdown_file):
        """Split the markdown file texts by triple-dashed lines.

        The content in the middle of triple-dashed lines is meta datas, which 
            use Yaml format.
        The other content is the markdown texts.
        """
        with codecs.open(mdown_file, "rb", "utf-8") as fd:
            text_lists = fd.readlines()

        meta_notation = "---\n"
        if text_lists[0] != meta_notation:
            msg = utils.color_msg(
                "error", 
                "[{0}] First line must be triple-dashed!".format(mdown_file),
            )
            sys.exit(msg)

        meta_lists = []
        meta_end_flag = False
        idx = 1
        max_idx = len(text_lists)
        while not meta_end_flag:
            meta_lists.append(text_lists[idx])
            idx += 1
            if idx >= max_idx:
                sys.exit(utils.color_msg(
                    "error",
                    "[{0}] doesn't have end triple-dashed!".format(mdown_file),
                ))
            if text_lists[idx] == meta_notation:
                meta_end_flag = True
        content_lists = text_lists[idx+1:]
        meta_yaml = "".join(meta_lists)
        contents = "".join(content_lists)

        return (meta_yaml, contents)

    def get_meta_datas(self, meta_yaml, mdown_file):
        """Get meta datas and validate them

        :param meta_yaml: Meta info in yaml format
        """
        try:
            meta_datas = yaml.load(meta_yaml)
        except yaml.YAMLError, e:
            msg = "Yaml format error in {}:\n{}".format(
                    mdown_file, 
                    unicode(str(e), "utf-8")
                    )
            sys.exit(utils.color_msg("error", msg))

        for m in ("title", "date"):
            if m not in meta_datas:
                sys.exit(utils.color_msg("error", "No '%s' in meta data!" % m))

        return meta_datas

class PageGenerator(BaseGenerator):

    def __init__(self, site_settings, mdown_file):
        """
        :param mdown_file: The path of markdown file
        """
        super(PageGenerator, self).__init__(site_settings)
        self.mdown_file = osp.realpath(mdown_file)

    def parse_mdown(self, contents):
        """Parse markdown text to html.

        :param contents: Markdown text lists
        """

        # Base markdown extensions support "fenced_code".
        mdown_extensions = ["fenced_code"]
        if self.site_settings["pygments"]:
            mdown_extensions.append("codehilite(guess_lang=False)")

        body_content = markdown.markdown(
            contents,
            extensions=mdown_extensions,
        )

        return body_content

    def get_tpl_vars(self):
        catalog, _ = self.get_catalog_and_mdown(self.mdown_file)
        meta_yaml, contents = self.get_meta_and_content(self.mdown_file)
        meta_datas = self.get_meta_datas(meta_yaml, self.mdown_file)
        body_content = self.parse_mdown(contents)
        tpl_vars = {
            "site" : self.site_settings,
            "catalog" : catalog,
            "content" : body_content,
        }
        tpl_vars.update(meta_datas)

        return tpl_vars

    def mdown2html(self):
        """Load template, and generate html.

        XXX: The post template must named `post.html`
        """
        tpl_vars = self.get_tpl_vars()
        html = self.env.get_template("post.html").render(tpl_vars)

        return html

    def output_to_file(self, html):
        """Write generated html to file"""
        catalog, mdown = self.get_catalog_and_mdown(self.mdown_file)
        output_catalog_path = osp.join(self.site_settings["destination"], catalog)
        if not utils.check_path_exists(output_catalog_path):
            print(utils.color_msg(
                "info", 
                "The output catalog %s not exists, create it" \
                % output_catalog_path)
            )
            os.mkdir(output_catalog_path)
        mdown_name = osp.splitext(mdown)[0]
        output_file = osp.join(output_catalog_path, mdown_name+".html")
        with codecs.open(output_file, "wb", "utf-8") as fd:
            fd.write(html)

class CatalogGenerator(BaseGenerator):

    def __init__(self, site_settings):
        super(CatalogGenerator, self).__init__(site_settings)

    def get_tpl_vars(self):
        """
        XXX: Only for one level dir.
        """
        catalog_page_list = {}

        sub_dirs = [ _ for _ in os.listdir(self.site_settings["source"])]
        for sub_dir in sub_dirs:
            abs_sub_dir = osp.join(self.site_settings["source"], sub_dir)
            if not osp.isdir(abs_sub_dir):
                continue
            catalog_page_list[sub_dir] = []
            for f in os.listdir(abs_sub_dir):
                if not utils.check_extension(f):
                    continue
                fn = osp.join(abs_sub_dir, f)
                meta_yaml, contents = self.get_meta_and_content(fn)
                meta_datas = self.get_meta_datas(meta_yaml, fn)
                r, e = osp.splitext(f)
                meta_datas.update(name = r)
                catalog_page_list[sub_dir].append(meta_datas)
            catalog_page_list[sub_dir].sort(
                key=lambda d: datetime.datetime.strptime(
                    d["date"], "%Y-%m-%d %H:%M"
                ),
                reverse=True,
            )

        tpl_vars = {
            "site" : self.site_settings,
            "catalog" : catalog_page_list,
        }

        return tpl_vars

    def generate_catalog_html(self):
        tpl_vars = self.get_tpl_vars()
        html = self.env.get_template("index.html").render(tpl_vars)
        return html

    def update_catalog_page(self):
        catalog_html = self.generate_catalog_html()
        catalog_file = osp.join(self.site_settings["destination"], "index.html")
        with codecs.open(catalog_file, "wb", "utf-8") as fd:
            fd.write(catalog_html)
