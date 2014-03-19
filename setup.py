#!/usr/bin/env python

from setuptools import setup, find_packages


entry_points = {
    "console_scripts": [
        "simiki = simiki.cli:main",
    ]
}

requires = [
    "Markdown",
    "Pygments",
    "Jinja2",
    "PyYAML",
    "docopt",
]

setup(
    name = "simiki",
    version = "0.2.0",
    url = "https://github.com/tankywoo/simiki",
    author = "Tanky Woo",
    author_email = "me@tankywoo.com",
    description = "Simiki is a simple static site generator for wiki.",
    license = "MIT License",
    packages = find_packages(),
    include_package_data=True,
    install_requires = requires,
    entry_points = entry_points,
)
