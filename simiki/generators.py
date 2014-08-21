#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Markdown file to html, which is embeded in html template.
"""

from __future__ import (print_function, with_statement, unicode_literals,
                        absolute_import)

import os
import os.path
import io
import datetime
import logging
import copy
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import markdown
import yaml
from jinja2 import (Environment, FileSystemLoader, TemplateError)


logger = logging.getLogger(__name__)


class BaseGenerator(object):
    """Base generator class"""

    def __init__(self, site_settings, base_path):
        self.site_settings = copy.deepcopy(site_settings)
        self.base_path = base_path
        _template_path = os.path.join(
            self.base_path,
            site_settings["themes_dir"],
            site_settings["theme"]
        )
        self.env = Environment(
            loader=FileSystemLoader(_template_path)
        )


class PageGenerator(BaseGenerator):

    def __init__(self, site_settings, base_path, sfile_path):
        super(PageGenerator, self).__init__(site_settings, base_path)
        self.sfile_path = sfile_path

    def markdown2html(self):
        """Load template, and generate html"""
        layout = self.get_layout()
        template_file = "{0}.html".format(layout)
        template_vars = self.get_template_vars()
        try:
            template = self.env.get_template(template_file)
            html = template.render(template_vars)
        except TemplateError as e:
            raise Exception("Unable to load template {0}: {1}"
                            .format(template_file, str(e)))

        return html

    def get_template_vars(self):
        """Get template variables, include site settings and page settings"""
        category, _ = self.get_category_and_file()
        meta_data, markdown_content = self.get_metadata_and_content()
        body_html_content = self.parse_markdown(markdown_content)
        page = {"category": category, "content": body_html_content}
        page.update(meta_data)
        template_vars = {
            "site": self.site_settings,
            "page": page,
        }

        # if site.root endswith `/`, remove it.
        site_root = template_vars["site"]["root"]
        if site_root.endswith("/"):
            template_vars["site"]["root"] = site_root[:-1]

        return template_vars

    def get_category_and_file(self):
        """Get the name of category and file(with extension)"""
        source_dir = os.path.join(self.base_path, self.site_settings["source"])
        relpath = os.path.relpath(self.sfile_path, source_dir)
        category, filename = os.path.split(relpath)

        return (category, filename)

    def get_metadata_and_content(self):
        metadata_textlist, content_textlist = \
            self.get_metadata_and_content_textlist()
        metadata_yaml = "".join(metadata_textlist)
        metadata = self.get_metadata(metadata_yaml)
        content = "".join(content_textlist)

        return (metadata, content)

    def get_metadata_and_content_textlist(self):
        """Split the source file texts by triple-dashed lines
        #TODO#
        The metadata is yaml format text in the middle of triple-dashed lines
        The content is the other source texts
        """
        with io.open(self.sfile_path, "rt", encoding="utf-8") as fd:
            textlist = fd.readlines()

        metadata_notation = "---\n"
        if textlist[0] != metadata_notation:
            raise Exception("{0} first line must be triple-dashed!"
                            .format(self.sfile_path))

        metadata_textlist = []
        metadata_end_flag = False
        idx = 1
        max_idx = len(textlist)
        while not metadata_end_flag:
            metadata_textlist.append(textlist[idx])
            idx += 1
            if idx >= max_idx:
                raise Exception("{0} doesn't have end triple-dashed!"
                                .format(self.sfile_path))
            if textlist[idx] == metadata_notation:
                metadata_end_flag = True
        content_textlist = textlist[idx + 1:]

        return (metadata_textlist, content_textlist)

    def check_metadata(self, metadata):
        """Check if metadata is right"""
        is_metadata_right = True
        if "title" not in metadata:
            logger.error("No `title' in metadata")
            is_metadata_right = False
        return is_metadata_right

    def get_metadata(self, metadata_yaml):
        """Get metadata and validate them

        :param metadata_yaml: metadata in yaml format
        """
        try:
            metadata = yaml.load(metadata_yaml)
        except yaml.YAMLError as e:
            raise Exception("Yaml format error in {0}:\n{1}".format(
                self.sfile_path,
                unicode(str(e), "utf-8")
            ))

        if not self.check_metadata(metadata):
            raise Exception

        return metadata

    def parse_markdown(self, markdown_content):
        """Parse markdown text to html.

        :param markdown_content: Markdown text lists #TODO#
        """
        markdown_extensions = self.set_markdown_extensions()

        html_content = markdown.markdown(
            markdown_content,
            extensions=markdown_extensions,
        )

        return html_content

    def set_markdown_extensions(self):
        """Set the extensions for markdown parser"""
        # Base markdown extensions support "fenced_code".
        markdown_extensions = ["fenced_code"]
        if self.site_settings["pygments"]:
            markdown_extensions.extend([
                "extra",
                "codehilite(css_class=hlcode)",
                "toc(title=Table of Contents)"
            ])

        return markdown_extensions

    def get_layout(self):
        """Get layout setting in metadata, default is 'page'"""
        metadata, markdown_content = self.get_metadata_and_content()
        if "layout" in metadata:
            # Compatible with previous version, which default layout is "post"
            # XXX Will remove this checker in v2.0
            if metadata["layout"] == "post":
                layout = "page"
            else:
                layout = metadata["layout"]
        else:
            layout = "page"

        return layout


class CatalogGenerator(BaseGenerator):

    def __init__(self, site_settings, base_path, pages):
        super(CatalogGenerator, self).__init__(site_settings, base_path)
        self.pages = pages

    def get_content_structure_and_metadata(self):
        """Ref: http://stackoverflow.com/a/9619101/1276501"""
        dct = {}
        ext = self.site_settings["default_ext"]
        for path, meta in self.pages.items():
            # Ignore other files
            if not path.endswith(ext):
                continue
            p = dct
            for x in path.split(os.sep):
                if ext in x:
                    meta["name"] = os.path.splitext(x)[0]
                    p = p.setdefault(x, meta)
                else:
                    p = p.setdefault(x, {})

        return dct["content"]

    def sort_structure(self, structure):
        """Sort index structure in lower-case, alphabetical order

        Compare argument is a key/value structure, if the compare argument is a
        leaf node, which has `title` key in its value, use the title value,
        else use the key to compare.
        """

        def _cmp(arg1, arg2):
            arg1 = arg1[1]["title"] if "title" in arg1[1] else arg1[0]
            arg2 = arg2[1]["title"] if "title" in arg2[1] else arg2[0]
            return cmp(arg1.lower(), arg2.lower())

        sorted_structure = copy.deepcopy(structure)
        for k, v in sorted_structure.items():
            sorted_structure = OrderedDict(sorted(
                sorted_structure.items(),
                _cmp
            ))
            if k.endswith(".{0}".format(self.site_settings["default_ext"])):
                continue
            sorted_structure[k] = self.sort_structure(sorted_structure[k])
        return sorted_structure

    def get_template_vars(self):
        self.site_settings["structure"] = \
            self.sort_structure(self.get_content_structure_and_metadata())
        tpl_vars = {
            "site": self.site_settings,
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


class CustomCatalogGenerator(CatalogGenerator):

    def __init__(self, site_settings, base_path):
        super(CustomCatalogGenerator, self).__init__(site_settings, base_path)

    def get_template_vars(self):
        if self.site_settings["index"] is True:
            fn = "index.md"
        else:
            fn = self.site_settings["index"]
        idx_mfile = os.path.join(
            os.path.abspath(self.site_settings["source"]),
            fn
        )
        pg = PageGenerator(self.site_settings, self.base_path, idx_mfile)
        _, raw_idx_content = pg.get_metadata_and_content()
        idx_content = pg.parse_markdown(raw_idx_content)
        page = {"content": idx_content}

        tpl_vars = {
            "site": self.site_settings,
            "page": page,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars
