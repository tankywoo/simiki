# Simiki #

[![Latest Version](http://img.shields.io/pypi/v/simiki.svg)](https://pypi.python.org/pypi/simiki)
[![The MIT License](http://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/tankywoo/simiki/blob/master/LICENSE)

Simiki 是一个用[Python](https://www.python.org/)写的简单的 wiki 框架, 适合分类记录一些技术文档.

* 简单，适合做个人维基
* 使用 Markdown 撰写
* 以分类目录为导向，分类存放源文件
* 生成静态 HTML 页面
* 命令行管理工具

## Quick Start ##

### 安装 ###

	pip install simiki

### 升级 ###

	pip install -U simiki

### 构建站点 ###

	mkdir mywiki && cd mywiki
	simiki init

编辑wiki配置文件`_config.yml` 进行相应配置

### 新建一篇 wiki ###

	simiki new -t "Hello Simiki" -c base

### 生成/更新静态页面 ###

	simiki generate

### 预览 ###

	simiki preview

更多可以查看帮助:

	simiki -h

或访问网站 [simiki.org](http://simiki.org/)


## 为什么叫Simiki? ##

`Simple Wiki`，取了前后各三个字母组成

## 其它 ##

* [simiki.org](http://simiki.org/)
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
