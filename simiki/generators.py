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
import copy
from os import path as osp
from pprint import pprint

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

from simiki import utils

logger = logging.getLogger(__name__)

class BaseGenerator(object):
    def __init__(self, site_settings):
        self.site_settings = copy.deepcopy(site_settings)
        self.env = Environment(
            loader = FileSystemLoader(osp.join(
                os.getcwd(),
                site_settings["themes_dir"],
                site_settings["theme"]
            ))
        )

    def get_category_and_mdown(self, mdown_file):
        """Get the category's and markdown's(with extension) name.

        :param mdown_file: TODO

        e.g: 
            mdown_file is /home/user/simiki/content/python/test.md
            category = python
            mdown = test.md
        """
        # @todo, if path with `/`?
        split_path = mdown_file.split("/")
        mdown, category = split_path[-1], split_path[-2]

        return (category, mdown)

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
            logging.error("{} First line must be triple-dashed!".format(mdown_file))
            sys.exit(1)

        meta_lists = []
        meta_end_flag = False
        idx = 1
        max_idx = len(text_lists)
        while not meta_end_flag:
            meta_lists.append(text_lists[idx])
            idx += 1
            if idx >= max_idx:
                logging.error("{} doesn't have end triple-dashed!".format(mdown_file))
                sys.exit(1)
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
            logging.error(msg)
            sys.exit(1)

        for m in ("title", "date"):
            if m not in meta_datas:
                logging.error("No '%s' in meta data!" % m)
                sys.exit(1)

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
            #mdown_extensions.append("codehilite(linenums=inline)")
            mdown_extensions.append("codehilite(guess_lang=False)")
            mdown_extensions.append("toc(title=Table of Contents)")
            #mdown_extensions.append("codehilite(guess_lang=False, linenums=inline)")

        body_content = markdown.markdown(
            contents,
            extensions=mdown_extensions,
        )

        return body_content

    def get_raw_html(self):
        _, contents = self.get_meta_and_content(self.mdown_file)
        body_content = self.parse_mdown(contents)
        return body_content

    def get_tpl_vars(self):
        category, _ = self.get_category_and_mdown(self.mdown_file)
        meta_yaml, contents = self.get_meta_and_content(self.mdown_file)
        meta_datas = self.get_meta_datas(meta_yaml, self.mdown_file)
        body_content = self.parse_mdown(contents)
        tpl_vars = {
            "site" : self.site_settings,
            "category" : category,
            "content" : body_content,
        }
        tpl_vars.update(meta_datas)

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

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
        category, mdown = self.get_category_and_mdown(self.mdown_file)
        output_category_path = osp.join(self.site_settings["destination"], category)
        if not utils.check_path_exists(output_category_path):
            logging.info(
                "The output category %s not exists, create it" \
                % output_category_path
            )
            os.mkdir(output_category_path)
        mdown_name = osp.splitext(mdown)[0]
        output_file = osp.join(output_category_path, mdown_name+".html")
        with codecs.open(output_file, "wb", "utf-8") as fd:
            fd.write(html)

class CatalogGenerator(BaseGenerator):

    def __init__(self, site_settings):
        super(CatalogGenerator, self).__init__(site_settings)

    @staticmethod
    def listdir_nohidden(path):
        for f in os.listdir(path):
            if not f.startswith('.'):
                yield f

    def get_tpl_vars(self):
        """
        XXX: Only for one level dir.
        """
        catalog_page_list = {}

        sub_dirs = [unicode(_, "utf-8") for _ in \
                CatalogGenerator.listdir_nohidden(self.site_settings["source"])]
        for sub_dir in sub_dirs:
            abs_sub_dir = osp.join(self.site_settings["source"], sub_dir)
            if not osp.isdir(abs_sub_dir):
                continue
            catalog_page_list[sub_dir] = []
            for f in CatalogGenerator.listdir_nohidden(abs_sub_dir):
                if not utils.check_extension(f):
                    continue
                fn = osp.join(abs_sub_dir, f)
                meta_yaml, contents = self.get_meta_and_content(fn)
                meta_datas = self.get_meta_datas(meta_yaml, fn)
                r, e = osp.splitext(f)
                meta_datas.update(name = r)
                catalog_page_list[sub_dir].append(meta_datas)
            catalog_page_list[sub_dir].sort(
                key = lambda p: p["title"].lower()
            )

        tpl_vars = {
            "site" : self.site_settings,
            "category" : catalog_page_list,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

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

class CustomCatalogGenerator(CatalogGenerator):

    def __init__(self, site_settings):
        super(CustomCatalogGenerator, self).__init__(site_settings)

    def get_tpl_vars(self):
        if self.site_settings["index"] is True:
            fn = "index.md"
        else:
            fn = self.site_settings["index"]
        idx_mfile = osp.join(os.path.abspath(self.site_settings["source"]), fn)
        pg = PageGenerator(self.site_settings, idx_mfile)
        idx_content = pg.get_raw_html()

        tpl_vars = {
            "site" : self.site_settings,
            "index_content" : idx_content,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars
