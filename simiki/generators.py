#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Markdown file to html, which is embeded in html template.
"""

from __future__ import (print_function, with_statement, unicode_literals,
                        absolute_import)

import os
import os.path
import io
import copy
import traceback
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import markdown
import yaml
from jinja2 import (Environment, FileSystemLoader, TemplateError)

from simiki import jinja_exts
from simiki.compat import is_py2, is_py3

if is_py3:
    from functools import cmp_to_key

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
        if not os.path.exists(_template_path):
            raise Exception("Theme `{0}' not exists".format(_template_path))
        self.env = Environment(
            loader=FileSystemLoader(_template_path)
        )
        self._jinja_load_exts()

    def _jinja_load_exts(self):
        '''Load jinja custom filters and extensions'''
        for _filter in jinja_exts.filters:
            self.env.filters[_filter] = getattr(jinja_exts, _filter)


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
        if self.meta.get('draft', False):
            return None
        layout = self.get_layout(self.meta)
        template_file = "{0}.html".format(layout)
        template_vars = self.get_template_vars(self.meta, self.content)
        try:
            template = self.env.get_template(template_file)
            html = template.render(template_vars)
        except TemplateError:
            # jinja2.exceptions.TemplateNotFound will get blocked
            # in multiprocessing?
            exc_msg = "unable to load template '{0}'\n{1}" \
                      .format(template_file, traceback.format_exc())
            raise Exception(exc_msg)

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
                raise Exception("disallow anything except newline "
                                "before begin meta notation '---'")
            textlist = textlist[1:]

        try:
            second_meta_notation_index = textlist.index(meta_notation)
        except ValueError:
            raise Exception("can't find end meta notation '---'")
        meta_textlist = textlist[:second_meta_notation_index]
        markup_textlist = textlist[second_meta_notation_index+1:]

        meta = self._get_meta(PLAT_LINE_SEP.join(meta_textlist))
        markup_text = PLAT_LINE_SEP.join(markup_textlist)
        if meta.get('render', True):
            content = self._parse_markdown(markup_text)
        else:
            content = markup_text

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
        category, src_fname = self.get_category_and_file()
        dst_fname = src_fname.replace(
            ".{0}".format(self.site_config["default_ext"]), ".html")
        page = {
            "category": category,
            "content": content,
            "filename": dst_fname
        }
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
        src_file_relpath_to_source = \
            os.path.relpath(self.src_file_relpath, self.site_config['source'])
        category, filename = os.path.split(src_file_relpath_to_source)
        return (category, filename)

    def _get_meta(self, meta_yaml):
        """Get meta and validate them

        :param meta_yaml: meta in yaml format
        """
        try:
            meta = yaml.load(meta_yaml)
        except yaml.YAMLError as e:
            e.extra_msg = 'yaml format error'
            raise

        if not self._check_meta(meta):
            raise Exception("no 'title' in meta")

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

        return dct.get(self.site_config['source'], {})

    def sort_structure(self, structure):
        """Sort index structure in lower-case, alphabetical order

        Compare argument is a key/value structure, if the compare argument is a
        leaf node, which has `title` key in its value, use the title value,
        else use the key to compare.
        """

        def _cmp(arg1, arg2):
            arg1 = arg1[1]["title"] if "title" in arg1[1] else arg1[0]
            arg2 = arg2[1]["title"] if "title" in arg2[1] else arg2[0]
            # cmp not exists in py3
            # via <https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons>
            cmp = lambda x, y: (x > y) - (x < y)
            return cmp(arg1.lower(), arg2.lower())

        if is_py2:
            sorted_opts = {'cmp': _cmp}
        elif is_py3:
            sorted_opts = {'key': cmp_to_key(_cmp)}

        sorted_structure = copy.deepcopy(structure)
        for k, _ in sorted_structure.items():
            sorted_structure = OrderedDict(sorted(
                sorted_structure.items(),
                **sorted_opts
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


class FeedGenerator(BaseGenerator):
    def __init__(self, site_config, base_path, pages, feed_fn='atom.xml'):
        '''
        :pages: all pages' meta variables, dict type
        '''
        super(FeedGenerator, self).__init__(site_config, base_path)
        self.pages = pages
        self.feed_fn = feed_fn

    def get_template_vars(self):
        tpl_vars = {
            "site": self.site_config,
            "pages": self.pages
        }

        # if site.root endwith `\`, remote it.
        site_root = tpl_vars["site"]["root"]
        if site_root.endswith("/"):
            tpl_vars["site"]["root"] = site_root[:-1]

        return tpl_vars

    def generate_feed(self):
        tpl_vars = self.get_template_vars()
        with open(os.path.join(self.base_path, self.feed_fn), 'r') as fd:
            template = self.env.from_string(fd.read())
            feed_content = template.render(tpl_vars)
        return feed_content
