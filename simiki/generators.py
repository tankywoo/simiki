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
from jinja2 import (Environment, FileSystemLoader, TemplateError)

from simiki import utils

logger = logging.getLogger(__name__)

class BaseGenerator(object):
    """Base generator class"""

    def __init__(self, site_settings, base_path, file_path):
        self.site_settings = copy.deepcopy(site_settings)
        self.base_path = base_path
        self.file_path = file_path
        _template_path = osp.join(
            self.base_path,
            site_settings["themes_dir"],
            site_settings["theme"]
        )
        try:
            self.env = Environment(
                loader = FileSystemLoader(_template_path)
            )
        except TemplateError, e:
            logging.error(str(e))
            sys.exit(1)

    def get_category_and_file(self):
        """Get the name of category and file(with extension)"""
        source_dir = osp.join(self.base_path, self.site_settings["source"])
        relpath = osp.relpath(self.file_path, source_dir)
        category, filename = osp.split(relpath)

        return (category, filename)

    def __check_metadata(self, metadata):
        """Check if metadata is right"""
        is_metadata_right = True
        if "title" not in metadata:
            logging.error("No `title' in metadata")
            is_metadata_right = False
        return is_metadata_right

    def __get_metadata(self, metadata_yaml):
        """Get metadata and validate them

        :param metadata_yaml: metadata in yaml format
        """
        try:
            metadata = yaml.load(metadata_yaml)
        except yaml.YAMLError, e:
            msg = "Yaml format error in {}:\n{}".format(
                self.file_path,
                unicode(str(e), "utf-8")
            )
            logging.error(msg)
            sys.exit(1)

        if not self.__check_metadata(metadata):
            sys.exit(1)

        return metadata

    def __get_metadata_and_content_textlist(self):
        """Split the source file texts by triple-dashed lines
        #TODO#
        The metadata is yaml format text in the middle of triple-dashed lines
        The content is the other source texts
        """
        with codecs.open(self.file_path, "rb", "utf-8") as fd:
            textlist = fd.readlines()

        metadata_notation = "---\n"
        if textlist[0] != metadata_notation:
            logging.error(
                "{} first line must be triple-dashed!".format(self.file_path)
            )
            sys.exit(1)

        metadata_textlist = []
        metadata_end_flag = False
        idx = 1
        max_idx = len(textlist)
        while not metadata_end_flag:
            metadata_textlist.append(textlist[idx])
            idx += 1
            if idx >= max_idx:
                logging.error(
                    "{} doesn't have end triple-dashed!".format(self.file_path)
                )
                sys.exit(1)
            if textlist[idx] == metadata_notation:
                metadata_end_flag = True
        content_textlist = textlist[idx+1:]

        return (metadata_textlist, content_textlist)

    def get_metadata_and_content(self):
        metadata_textlist, content_textlist = \
            self.__get_metadata_and_content_textlist()
        metadata_yaml = "".join(metadata_textlist)
        metadata = self.__get_metadata(metadata_yaml)
        content = "".join(content_textlist)

        return (metadata, content)


class PageGenerator(BaseGenerator):

    def __init__(self, site_settings, base_path, file_path):
        super(PageGenerator, self).__init__(site_settings, base_path, file_path)
        self.file_path = osp.realpath(file_path)

    def __set_markdown_extensions(self):
        """Set the extensions for markdown parser"""
        # Base markdown extensions support "fenced_code".
        markdown_extensions = ["fenced_code"]
        if self.site_settings["pygments"]:
            markdown_extensions.extend([
                "codehilite(css_class=hlcode)",
                "toc(title=Table of Contents)"
            ])

        return markdown_extensions

    def parse_markdown(self, markdown_content):
        """Parse markdown text to html.

        :param markdown_content: Markdown text lists #TODO#
        """
        markdown_extensions = self.__set_markdown_extensions()

        html_content = markdown.markdown(
            markdown_content,
            extensions=markdown_extensions,
        )

        return html_content

    def get_template_vars(self):
        """Get template variables, include site settings and page settings"""
        category, _ = self.get_category_and_file()
        meta_data, markdown_content = self.get_metadata_and_content()
        body_html_content = self.parse_markdown(markdown_content)
        page = {"category" : category, "content" : body_html_content}
        page.update(meta_data)
        template_vars = {
            "site" : self.site_settings,
            "page" : page,
        }

        # if site.root endswith `/`, remove it.
        site_root = template_vars["site"]["root"]
        if site_root.endswith("/"):
            template_vars["site"]["root"] = site_root[:-1]

        return template_vars

    def __get_layout(self):
        """Get layout setting in metadata, default is 'page'"""
        metadata, markdown_content = self.get_metadata_and_content()
        if "layout" in metadata:
            layout = metadata["layout"]
        else:
            layout = "page"

        return layout

    def markdown2html(self):
        """Load template, and generate html"""
        layout = self.__get_layout()
        template_html_file = "{}.html".format(layout)
        template_vars = self.get_template_vars()
        try:
            html = self.env.get_template(template_html_file).render(template_vars)
        except TemplateError, e:
            logging.error("Unable to load template {}; error: {}"\
                    .format(template_html_file, str(e)))
            sys.exit(1)

        return html

    def output_to_file(self, html):
        """Write generated html to file"""
        category, markdown = self.get_category_and_file()
        output_category_path = osp.join(
            self.site_settings["destination"], 
            category
        )
        if not utils.check_path_exists(output_category_path):
            logging.info(
                "The output category %s not exists, create it" \
                % output_category_path
            )
            utils.mkdir_p(output_category_path)
        markdown_name = osp.splitext(markdown)[0]
        output_file = osp.join(output_category_path, markdown_name+".html")
        with codecs.open(output_file, "wb", "utf-8") as fd:
            fd.write(html)

class CatalogGenerator(BaseGenerator):

    def __init__(self, site_settings, base_path):
        super(CatalogGenerator, self).__init__(site_settings, base_path, None)

    def __get_catalog_page_list(self, d):
        """
        XXX: Only for root and one level dir.
        """
        catalog_page_list = {}
        sub_dirs = [unicode(_, "utf-8") for _ in \
                utils.listdir_nohidden(d)]
        for sub_dir in sub_dirs:
            abs_sub_dir = osp.join(self.site_settings["source"], sub_dir)
            # If file under the root of content directory, ignore it.
            # TODO: support root level.
            if not osp.isdir(abs_sub_dir):
                continue
            catalog_page_list[sub_dir] = []
            for f in utils.listdir_nohidden(abs_sub_dir):
                if osp.isdir(f):
                    catalog_page_list[sub_dir][f] = {}
                if not utils.check_extension(f):
                    continue
                fn = osp.join(abs_sub_dir, f)
                pg = PageGenerator(self.site_settings, self.base_path, fn)
                metadata, _ = pg.get_metadata_and_content()
                r, e = osp.splitext(f)
                metadata.update(name = r)
                catalog_page_list[sub_dir].append(metadata)
            catalog_page_list[sub_dir].sort(
                key = lambda p: p["title"].lower()
            )

        return catalog_page_list

    def get_template_vars(self):
        self.site_settings["categories"] = \
            self.__get_catalog_page_list(self.site_settings["source"])
        tpl_vars = {
            "site" : self.site_settings,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars

    def generate_catalog_html(self):
        tpl_vars = self.get_template_vars()
        html = self.env.get_template("index.html").render(tpl_vars)
        return html

    def update_catalog_page(self):
        catalog_html = self.generate_catalog_html()
        catalog_file = osp.join(self.site_settings["destination"], "index.html")
        with codecs.open(catalog_file, "wb", "utf-8") as fd:
            fd.write(catalog_html)

class CustomCatalogGenerator(CatalogGenerator):

    def __init__(self, site_settings, base_path):
        super(CustomCatalogGenerator, self).__init__(site_settings, base_path)

    def get_template_vars(self):
        if self.site_settings["index"] is True:
            fn = "index.md"
        else:
            fn = self.site_settings["index"]
        idx_mfile = osp.join(os.path.abspath(self.site_settings["source"]), fn)
        pg = PageGenerator(self.site_settings, self.base_path, idx_mfile)
        _, raw_idx_content = pg.get_metadata_and_content()
        idx_content = pg.parse_markdown(raw_idx_content)
        page = {"content" : idx_content}

        tpl_vars = {
            "site" : self.site_settings,
            "page" : page,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars
