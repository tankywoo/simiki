# Simiki #

Simiki 是一个简单的 wiki 框架, 适合分类记录一些技术文档.

* 支持 [Markdown](http://daringfireball.net/projects/markdown/)
* 生成静态 HTML 页面
* 有一个命令行管理程序
* 支持代码高亮


## "Simiki" 名称的由来 ##

Simki 是取 Simple Wiki 的前三个字母和后三个字母拼起来的.

## 安装 ##

如果直接在默认系统环境下运行，需要 `root` 权限；也可以使用 [virtualenv](http://www.virtualenv.org/) 等Python虚拟环境，这样则不需要 root 权限。

	pip install simiki

或者

	python setup.py install

## 依赖 ##

* [Markdown](https://github.com/waylan/Python-Markdown): Python 实现的 Markdown 引擎, 用于解析 Markdown 文件.
* [Pygments](http://pygments.org/): Python 实现的语法高亮着色器.
* [Jinja2](http://jinja.pocoo.org/): 功能强大的 Python 模版引擎.
* [PyYAML](http://pyyaml.org/): Python 的 YAML 解析器.
* [docopt](http://docopt.org/): 比 `argparse` 更优美的命令行工具.

## 使用方法 ##

详见 [Simiki.org](http://simiki.org/).

## License ##

MIT License
