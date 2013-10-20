#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Markdown file to html, which is embeded in html template.
"""

from __future__ import print_function, with_statement, unicode_literals

import sys

import markdown
from jinja2 import Environment, FileSystemLoader

from simiki import configs


class Generator(object):
    def __init__(self, md_resource, md_type="file"):
        """
        :param md_resource: markdown resource, can be markdown file name or 
            markdown text
        :param md_type: md_resource type, `file` or `text`
        """
        if md_type == "file":
            with open(md_resource, "rb") as fd:
                texts = [unicode(_, "utf-8") for _ in fd.readlines()]
                self.md_text = "".join(texts)
        elif md_type == "text":
            self.md_text = md_resource
        else:
            print("`md_type` error, should be `file` or `text`.")
            sys.exit(1)

    def _get_title(self):
        """Get the wiki's title.

        Established:
            The first line of wiki is the title, written in html comment syntax.
            such as:
                <!-- title : The wiki title -->
        """
        notations = {"left" : "<!--", "right" : "-->"}

        first_line = self.md_text.split("\n")[0].strip()

        for notation in notations.values():
            first_line = first_line.replace(notation, "")
        first_line = first_line.strip()

        # strip the space between `title` and `:`
        first_line = first_line.split(":", 1)
        first_line[0] = first_line[0].strip().lower()
        first_line = ":".join(first_line)

        title = first_line.lstrip("title:").strip()

        return title

    def _md2html(self, title):
        """Generate the html from md file, and embed it in html template.

        **Note** returned html is unicode.
        """
        body_content = markdown.markdown(self.md_text, \
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

    def generate(self):
        title = self._get_title()
        html = self._md2html(title)

        return html
