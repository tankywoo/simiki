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

> New in version 1.6.0 (2016-06-09)
> 
> - Fix issue #60, preview with 127.0.0.1
> - Add `page` variable, [doc](http://simiki.org/docs/variables.html#index-variables)
> - Add `category` settings in _config.yml
> - Add `collection` and `tag`, a three-tier structure, [doc](http://simiki.org/docs/collection_and_tag.html)
> - Add new theme simple2, with collection/tag support

## Installation ##

It is available for **Python 2.6, 2.7, 3.3, 3.4, 3.5**, with Linux, Mac OS X and Windows.

Install from [PyPI](https://pypi.python.org/pypi/simiki):

	pip install simiki

Update:

	pip install -U simiki


## Quick Start ##

### Init Site ###

	mkdir mywiki && cd mywiki
	simiki init

### Generate ###

	simiki g

### Preview ###

	simiki p

For more information, `simiki -h` or have a look at [Simiki.org](http://simiki.org)


## Others ##

* [simiki.org](http://simiki.org)
* <https://github.com/tankywoo/simiki>
* Email: <me@tankywoo.com>
* [Simiki Users](https://github.com/tankywoo/simiki/wiki/Simiki-Users)


## Contribution ##

Your contributions are always welcome!

Sending pull requests on [Pull Requests Page](https://github.com/tankywoo/simiki/pulls) is the preferred method for receiving contributions.

* Bug fixes can be based on **`master`** branch and I will also merge into `dev` branch.
* Feature can be based on **`dev`** branch.

Following links are the contribution guidelines you may need:

* [Fork A Repo](https://help.github.com/articles/fork-a-repo/)
* [Contributing to Processing with Pull Requests](https://github.com/processing/processing/wiki/Contributing-to-Processing-with-Pull-Requests)

Thanks to every [contributor](https://github.com/tankywoo/simiki/graphs/contributors).


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
