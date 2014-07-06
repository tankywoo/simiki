#!/usr/bin/env python
from __future__ import with_statement
import os
from setuptools import setup, find_packages
import simiki


entry_points = {
    "console_scripts": [
        "simiki = simiki.cli:main",
    ]
}

with open("requirements.txt") as f:
    requires = [l for l in f.read().splitlines() if l]

readme = "README.md"
if os.path.exists("README.rst"):
    readme = "README.rst"
with open(readme) as f:
    long_description = f.read()


setup(
    name="simiki",
    version=simiki.__version__,
    url="http://simiki.org/",
    author="Tanky Woo",
    author_email="me@tankywoo.com",
    description="Simiki is a simple wiki framework, written in Python.",
    long_description=long_description,
    keywords="simiki, wiki, generator",
    license="MIT License",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)
