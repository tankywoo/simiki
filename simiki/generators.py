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
import re
import traceback
import warnings
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
        self._templates = {}  # templates cache
        self._template_vars = self._get_template_vars()
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

    def get_template(self, name):
        '''Return the template by layout name'''
        if name not in self._templates:
            try:
                self._templates[name] = self.env.get_template(name + '.html')
            except TemplateError:
                # jinja2.exceptions.TemplateNotFound will get blocked
                # in multiprocessing?
                exc_msg = "unable to load template '{0}.html'\n{1}" \
                          .format(name, traceback.format_exc())
                raise Exception(exc_msg)

        return self._templates[name]

    def _get_template_vars(self):
        '''Return the common template variables'''
        template_vars = {
            'site': self.site_config,
        }

        # if site.root endswith '/`, remove it.
        site_root = template_vars['site']['root']
        if site_root.endswith('/'):
            template_vars['site']['root'] = site_root[:-1]

        return template_vars


class PageGenerator(BaseGenerator):

    def __init__(self, site_config, base_path, tags=None):
        super(PageGenerator, self).__init__(site_config, base_path)
        self._tags = tags
        self._reset()

    def _reset(self):
        """Reset the global self variables"""
        self._src_file = None  # source file path relative to base_path
        self.meta = None
        self.content = None

    def to_html(self, src_file, include_draft=False):
        """Load template, and generate html

        :src_file: the filename of the source file. This can either be an
                   absolute filename or a filename relative to the base path.
        :include_draft: True/False, include draft pages or not to generate
        """
        self._reset()
        self._src_file = os.path.relpath(src_file, self.base_path)
        self.meta, self.content = self.get_meta_and_content()
        # Page set `draft: True' mark current page as draft, and will
        # be ignored if not forced generate include draft pages
        if not include_draft and self.meta.get('draft', False):
            return None
        layout = self.get_layout(self.meta)
        template_vars = self.get_template_vars(self.meta, self.content)
        template = self.get_template(layout)
        html = template.render(template_vars)

        return html

    @property
    def src_file(self):
        return self._src_file

    @src_file.setter
    def src_file(self, filename):
        self._src_file = os.path.relpath(filename, self.base_path)

    def get_meta_and_content(self, do_render=True):
        meta_str, content_str = self.extract_page(self._src_file)
        meta = self.parse_meta(meta_str)
        # This is the most time consuming part
        if do_render and meta.get('render', True):
            content = self._parse_markup(content_str)
        else:
            content = content_str

        return meta, content

    def get_layout(self, meta):
        """Get layout config in meta, default is `page'"""
        if "layout" in meta:
            # Compatible with previous version, which default layout is "post"
            # XXX Will remove this checker in v2.0
            if meta["layout"] == "post":
                warn_msg = "{0}: layout `post' is deprecated, use `page'" \
                           .format(self._src_file)
                if is_py2:
                    # XXX: warnings message require str, no matter whether
                    # py2 or py3; but in py3, bytes message is ok in simple
                    # test, but failed in unittest with py3.3, ok with py3.4?
                    warn_msg = warn_msg.encode('utf-8')
                warnings.warn(warn_msg, DeprecationWarning)
                layout = "page"
            else:
                layout = meta["layout"]
        else:
            layout = "page"

        return layout

    def get_template_vars(self, meta, content):
        """Get template variables, include site config and page config"""
        template_vars = copy.deepcopy(self._template_vars)
        page = {"content": content}
        page.update(meta)
        page.update({'relation': self.get_relation()})

        template_vars.update({'page': page})

        return template_vars

    def get_category_and_file(self):
        """Get the name of category and file(with extension)"""
        src_file_relpath_to_source = \
            os.path.relpath(self._src_file, self.site_config['source'])
        category, filename = os.path.split(src_file_relpath_to_source)
        return (category, filename)

    @staticmethod
    def extract_page(filename):
        """Split the page file texts by triple-dashed lines, return the mata
        and content.

        :param filename: the filename of markup page

        returns:
          meta_str (str): page's meta string
          content_str (str): html parsed from markdown or other markup text.
        """
        regex = re.compile('(?sm)^---(?P<meta>.*?)^---(?P<body>.*)')
        with io.open(filename, "rt", encoding="utf-8") as fd:
            match_obj = re.match(regex, fd.read())
            if match_obj:
                meta_str = match_obj.group('meta')
                content_str = match_obj.group('body')
            else:
                raise Exception('extracting page with format error, '
                                'see <http://simiki.org/docs/metadata.html>')

        return meta_str, content_str

    def parse_meta(self, yaml_str):
        """Parse meta from yaml string, and validate yaml filed, return dict"""
        try:
            meta = yaml.load(yaml_str)
        except yaml.YAMLError as e:
            e.extra_msg = 'yaml format error'
            raise

        category, src_fname = self.get_category_and_file()
        dst_fname = src_fname.replace(
            ".{0}".format(self.site_config['default_ext']), '.html')
        meta.update({'category': category, 'filename': dst_fname})

        if 'tag' in meta:
            if isinstance(meta['tag'], basestring):
                _tags = [t.strip() for t in meta['tag'].split(',')]
                meta.update({'tag': _tags})

        if "title" not in meta:
            raise Exception("no 'title' in meta")

        return meta

    def _parse_markup(self, markup_text):
        """Parse markup text to html

        Only support Markdown for now.
        """
        markdown_extensions = self._set_markdown_extensions()

        html_content = markdown.markdown(
            markup_text,
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

    def get_relation(self):
        rn = []
        if self._tags and 'tag' in self.meta:
            for t in self.meta['tag']:
                rn.extend(self._tags[t])
        # remove itself
        rn = [r for r in rn if self.meta['title'] != r['title']]
        # remove the duplicate items
        # note this will change the items order
        rn = [r for n, r in enumerate(rn) if r not in rn[n+1:]]
        return rn


class CatalogGenerator(BaseGenerator):

    def __init__(self, site_config, base_path, pages):
        '''
        :pages: all pages' meta variables, dict type
        '''
        super(CatalogGenerator, self).__init__(site_config, base_path)
        self._pages = pages
        self.pages = None
        self.structure = None

    def get_structure(self):
        """Ref: http://stackoverflow.com/a/9619101/1276501"""
        dct = {}
        ext = self.site_config["default_ext"]
        for path, meta in self._pages.items():
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

        self.structure = dct.get(self.site_config['source'], {})

        self.sort_structure()

    def sort_structure(self):
        """Sort index structure in lower-case, alphabetical order

        Compare argument is a key/value structure, if the compare argument is a
        leaf node, which has `title` key in its value, use the title value,
        else use the key to compare.
        """

        def _cmp(arg1, arg2):
            arg1 = arg1[1]["title"] if "title" in arg1[1] else arg1[0]
            arg2 = arg2[1]["title"] if "title" in arg2[1] else arg2[0]
            # cmp not exists in py3
            # via <https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons> # noqa
            cmp = lambda x, y: (x > y) - (x < y)
            return cmp(arg1.lower(), arg2.lower())

        if is_py2:
            sorted_opts = {'cmp': _cmp}
        elif is_py3:
            sorted_opts = {'key': cmp_to_key(_cmp)}

        def _sort(structure):
            sorted_structure = copy.deepcopy(structure)
            for k, _ in sorted_structure.items():
                sorted_structure = OrderedDict(sorted(
                    sorted_structure.items(),
                    **sorted_opts
                ))
                if k.endswith(".{0}".format(self.site_config["default_ext"])):
                    continue
                sorted_structure[k] = _sort(sorted_structure[k])
            return sorted_structure

        self.structure = _sort(self.structure)

    def get_pages(self):
        # for custom category settings in _config.yml
        _category = {}
        for c in self.site_config.get('category', []):
            c_name = c.pop('name')
            _category[c_name] = c

        def convert(d, prefix=''):
            pages = []
            for k, v in d.items():
                if 'name' in v:  # page
                    v.update({'fname': k})
                    pages.append(v)
                else:
                    k_with_prefix = os.path.join(prefix, k)
                    _pages = convert(v, prefix=k_with_prefix)
                    _s_category = {'name': k, 'pages': _pages}
                    if k_with_prefix in _category:
                        _s_category.update(_category[k_with_prefix])
                    pages.append(_s_category)

            return pages

        # get pages from structure
        self.pages = convert(self.structure)

        self.update_pages_collection()

    def update_pages_collection(self):
        pages = copy.deepcopy(self.pages)
        self.pages = []
        # for two-level, first level is category
        for category in pages:
            if 'fname' in category:
                # for first level pages
                continue
            _c_pages = []
            _colls = {}
            for page in category.pop('pages'):
                if 'collection' in page:
                    coll_name = page['collection']
                    _colls.setdefault(coll_name, []).append(page)
                else:
                    _c_pages.append(page)
            colls = []
            for _coll_n, _coll_p in _colls.items():
                colls.append({'name': _coll_n, 'pages': _coll_p})
            _c_pages.extend(colls)
            category.update({'pages': _c_pages})
            self.pages.append(category)

    def get_template_vars(self):
        template_vars = copy.deepcopy(self._template_vars)

        self.get_structure()
        # `structure' is deprecated and will be removed later
        # use `pages' instead
        template_vars['site'].update({'structure': self.structure})

        self.get_pages()
        template_vars.update({'pages': self.pages})

        return template_vars

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
