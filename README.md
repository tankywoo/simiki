# Simiki #

[![Latest Version](http://img.shields.io/pypi/v/simiki.svg)](https://pypi.python.org/pypi/simiki)
[![The MIT License](http://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/tankywoo/simiki/blob/master/LICENSE)

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

	simiki generate

### Preview ###

	simiki preview

For more information, `simiki -h` or have a look at [Simiki.org](http://simiki.org)

## Syntax Highlighter ##

[Pygments](http://pygments.org/) is employed here to provide syntax highlighter working with Markdown.

    ~~~~{.c}
    #include <pmmintrin.h> //SSE3

    void matrix_gen(int size, float *matrix1, float *matrix2)
    {
        int i;
        for (i = 0; i < size * size; i++) {
            matrix1[i] = i * 1.2f + 1;
            matrix2[i] = i * 1.3f + 1;
        }
    }
    ~~~~

## Others ##

* [simiki.org](http://simiki.org)
* <https://github.com/tankywoo/simiki>
* Email: <me@tankywoo.com>


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
