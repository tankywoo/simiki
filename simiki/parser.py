#!/usr/bin/env python
# -*- coding: utf-8 -*-
import markdown
import mistune
from mistune_contrib import highlight


class MarkupParser(object):
    """Markup Parser

    Currently only support Markdown
    """
    def __init__(self, site_config):
        self.site_config = site_config

    def parse(self, text):
        parser = PythonMarkdownParser(self.site_config)
        return parser.parse(text)


class PythonMarkdownParser(object):
    """Markdown Parser

    Use [waylan/Python-Markdown](https://github.com/waylan/Python-Markdown)

    Ref:
      * [PyPI](https://pypi.python.org/pypi/Markdown)
      * [Docs](https://pythonhosted.org/Markdown/)
    """
    def __init__(self, site_config):
        self.site_config = site_config

    def parse(self, text):
        """Parse markup text to html"""
        # TODO every parse action will do _set_markdown_extensions
        markdown_extensions = self._set_markdown_extensions()

        html = markdown.markdown(
            text,
            extensions=markdown_extensions,
        )

        return html

    def _set_markdown_extensions(self):
        """Set the extensions for markdown parser"""
        if self.site_config.get('markdown'):
            # if markdown options defined in _config.yml, such as:
            # markdown:
            #   - fenced_code
            #   - extra
            #   - codehilite(css_class=hlcode)
            #   - toc(title=Table of Contents)
            markdown_extensions = self.site_config['markdown']
        else:
            # Base markdown extensions support "fenced_code".
            # codehilite is the most time consuming part
            markdown_extensions = ["fenced_code"]
            if self.site_config["pygments"]:
                markdown_extensions.extend([
                    "extra",
                    "codehilite(css_class=hlcode)",
                    "toc(title=Table of Contents)"
                ])

        return markdown_extensions


class MistuneRenderer(highlight.HighlightMixin, mistune.Renderer):
    pass


class MistuneParser(object):
    """Markdown Parser

    Use [lepture/mistune](https://github.com/lepture/mistune)
    """
    def __init__(self, site_config):
        self.site_config = site_config

    def parse(self, text):
        """Parse markup text to html"""

        renderer = MistuneRenderer(linenos=False, inlinestyles=True)

        html = mistune.markdown(text, renderer=renderer)

        return html
