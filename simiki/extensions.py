#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import fnmatch

from jinja2 import nodes
from jinja2.ext import Extension

from simiki.configs import parse_configs


class PageUrlExtension(Extension):
    """"""

    # a set of names that trigger the extension.
    tags = set(["page_url"])

    def __init__(self, environment):
        super(PageUrlExtension, self).__init__(environment)

    def parse(self, parser):
        # get the line number, so that we can give that line number to the
        # nodes we create by hand.
        lineno = next(parser.stream).lineno
        # now we parse a single expression that is used as page url.
        args = [parser.parse_expression()]

        # return self.call_method('_search_page_url', args).set_lineno(lineno)
        return nodes.CallBlock(self.call_method("_search_page_url", args),
                                                [], [], []).set_lineno(lineno)

    def _search_page_url(self, page_url, caller):
        """Get the path relative path from page name"""
        cwd_path = os.getcwd()
        configs = parse_configs(os.path.join(cwd_path, "_config.yml"))
        content_path = os.path.join(cwd_path, "content")
        _filter = "{0}.{1}".format(page_url, configs["default_ext"])
        rel_url = ""
        for root, dirnames, filenames in os.walk(content_path):
            for filename in fnmatch.filter(filenames, _filter):
                abs_fn = os.path.join(root, filename)
                rel_fn = os.path.join("/",
                                      os.path.relpath(abs_fn, content_path))
                rel_url = "{0}.html".format(os.path.splitext(rel_fn)[0])
                break
        return rel_url
