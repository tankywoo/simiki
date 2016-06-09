---
title: "Getting Started"
layout: page
date: 2099-06-02 00:00
---

[TOC]

# Simiki #

[![Latest Version](http://img.shields.io/pypi/v/simiki.svg)](https://pypi.python.org/pypi/simiki)
[![The MIT License](http://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/tankywoo/simiki/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/tankywoo/simiki.svg)](https://travis-ci.org/tankywoo/simiki)
[![Coverage Status](https://img.shields.io/coveralls/tankywoo/simiki.svg)](https://coveralls.io/r/tankywoo/simiki)

Simiki is a simple wiki framework, written in [Python](https://www.python.org/).

* Easy to use. Creating a wiki only needs a few steps
* Use [Markdown](http://daringfireball.net/projects/markdown/). Just open your editor and write
* Store source files by category
* Static HTML output
* A CLI tool to manage the wiki

Simiki is short for `Simple Wiki` :)

## Quick Start ##

### Install ###

	pip install simiki

### Update ###

	pip install -U simiki

### Init Site ###

	mkdir mywiki && cd mywiki
	simiki init

### Create a new wiki ###

	simiki new -t "Hello Simiki" -c first-catetory

### Generate ###

	simiki g

### Preview ###

	simiki p -w

For more information, `simiki -h` or have a look at [Simiki.org](http://simiki.org)

## Others ##

* [simiki.org](http://simiki.org)
* <https://github.com/tankywoo/simiki>
* Email: <me@tankywoo.com>
* [Simiki Users](https://github.com/tankywoo/simiki/wiki/Simiki-Users)

## License ##

The MIT License (MIT)

Copyright (c) 2013 Tanky Woo

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
