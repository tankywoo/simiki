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


PLAT_LINE_SEP = '\n'

class BaseGenerator(object):
    """Base generator class"""

    def __init__(self, site_config, base_path):
        '''
        :site_config: site global configuration parsed from _config.yml
        :base_path: root path of wiki directory
        '''
        self.site_config = copy.deepcopy(site_config)
        self.base_path = base_path
        _template_path = os.path.join(
            self.base_path,
            site_config["themes_dir"],
            site_config["theme"]
        )
        self.env = Environment(
            loader=FileSystemLoader(_template_path)
        )


class PageGenerator(BaseGenerator):

    def __init__(self, site_config, base_path, src_file_path):
        '''
        :src_file_path: path of a source file
        '''
        super(PageGenerator, self).__init__(site_config, base_path)
        self.src_file_path = src_file_path
        # source file path relative to base_path
        self.src_file_relpath = os.path.relpath(src_file_path, self.base_path)
        self.meta = None
        self.content = None

    def to_html(self):
        """Load template, and generate html"""
        self.meta, self.content = self.get_meta_and_content()
        layout = self.get_layout(self.meta)
        template_file = "{0}.html".format(layout)
        template_vars = self.get_template_vars(self.meta, self.content)
        try:
            template = self.env.get_template(template_file)
            html = template.render(template_vars)
        except TemplateError as e:
            raise Exception("Unable to load template {0}: {1}"
                            .format(template_file, unicode(e)))

        return html

    def get_meta_and_content(self):
        """Split the source file texts by triple-dashed lines, return the mata
        and content.
        meta is page's meta data, dict type.
        content is html parsed from markdown or other markup text.
        """
        meta_notation = "---"
        with io.open(self.src_file_path, "rt", encoding="utf-8") as fd:
            textlist = fd.read().lstrip().splitlines()
            if textlist[0] != meta_notation:
                raise Exception("Disallow anything except newline "
                                "before begin meta notation: '---'")
            textlist = textlist[1:]

        try:
            second_meta_notation_index = textlist.index(meta_notation)
        except ValueError:
            raise Exception("Can't find end meta notation: '---'")
        meta_textlist = textlist[:second_meta_notation_index]
        markup_textlist = textlist[second_meta_notation_index+1:]

        meta = self._get_meta(PLAT_LINE_SEP.join(meta_textlist))
        markup_text = PLAT_LINE_SEP.join(markup_textlist)
        content = self._parse_markdown(markup_text)

        return (meta, content)

    @staticmethod
    def get_layout(meta):
        """Get layout config in meta, default is 'page'"""
        if "layout" in meta:
            # Compatible with previous version, which default layout is "post"
            # XXX Will remove this checker in v2.0
            if meta["layout"] == "post":
                layout = "page"
            else:
                layout = meta["layout"]
        else:
            layout = "page"

        return layout

    def get_template_vars(self, meta, content):
        """Get template variables, include site config and page config"""
        category, _ = self.get_category_and_file()
        page = {"category": category, "content": content}
        page.update(meta)
        template_vars = {
            "site": self.site_config,
            "page": page,
        }

        # if site.root endswith `/`, remove it.
        site_root = template_vars["site"]["root"]
        if site_root.endswith("/"):
            template_vars["site"]["root"] = site_root[:-1]

        return template_vars

    def get_category_and_file(self):
        """Get the name of category and file(with extension)"""
        src_file_relpath_to_source = os.path.relpath(self.src_file_relpath,
                                                     self.site_config['source'])
        category, filename = os.path.split(src_file_relpath_to_source)
        return (category, filename)

    def _get_meta(self, meta_yaml):
        """Get meta and validate them

        :param meta_yaml: meta in yaml format
        """
        try:
            meta = yaml.load(meta_yaml)
        except yaml.YAMLError as e:
            raise Exception("Yaml format error in {0}:\n{1}".format(
                self.src_file_path,
                unicode(e)
            ))

        if not self._check_meta(meta):
            raise Exception("{0}: no 'title' in meta"
                            .format(self.src_file_relpath))

        return meta

    def _check_meta(self, meta):
        """Check if meta is right"""
        is_meta_right = True
        if "title" not in meta:
            is_meta_right = False
        return is_meta_right

    def _parse_markdown(self, markdown_content):
        """Parse markdown text to html"""
        markdown_extensions = self._set_markdown_extensions()

        html_content = markdown.markdown(
            markdown_content,
            extensions=markdown_extensions,
        )

        return html_content

    def _set_markdown_extensions(self):
        """Set the extensions for markdown parser"""
        # TODO: custom markdown extension in _config.yml
        # Base markdown extensions support "fenced_code".
        markdown_extensions = ["fenced_code"]
        if self.site_config["pygments"]:
            markdown_extensions.extend([
                "extra",
                "codehilite(css_class=hlcode)",
                "toc(title=Table of Contents)"
            ])

        return markdown_extensions


class CatalogGenerator(BaseGenerator):

    def __init__(self, site_config, base_path, pages):
        '''
        :pages: all pages' meta variables, dict type
        '''
        super(CatalogGenerator, self).__init__(site_config, base_path)
        self.pages = pages

    def get_content_structure_and_meta(self):
        """Ref: http://stackoverflow.com/a/9619101/1276501"""
        dct = {}
        ext = self.site_config["default_ext"]
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

        return dct[self.site_config['source']]

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
        for k, _ in sorted_structure.items():
            sorted_structure = OrderedDict(sorted(
                sorted_structure.items(),
                _cmp
            ))
            if k.endswith(".{0}".format(self.site_config["default_ext"])):
                continue
            sorted_structure[k] = self.sort_structure(sorted_structure[k])
        return sorted_structure

    def get_template_vars(self):
        self.site_config["structure"] = \
            self.sort_structure(self.get_content_structure_and_meta())
        tpl_vars = {
            "site": self.site_config,
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

    def __init__(self, site_config, base_path):
        super(CustomCatalogGenerator, self).__init__(site_config,
                                                     base_path,
                                                     None)

    def get_template_vars(self):
        if self.site_config["index"] is True:
            fn = "index.md"
        else:
            fn = self.site_config["index"]
        idx_mfile = os.path.join(
            os.path.abspath(self.site_config["source"]),
            fn
        )
        page_generator = PageGenerator(self.site_config, self.base_path,
                                       idx_mfile)
        _, raw_idx_content = page_generator.get_meta_and_content()
        idx_content = page_generator.parse_markdown(raw_idx_content)
        page = {"content": idx_content}

        tpl_vars = {
            "site": self.site_config,
            "page": page,
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars
