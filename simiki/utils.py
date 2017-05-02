#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
import sys
import os.path
import shutil
import errno
import logging
import io
import hashlib
import simiki
from simiki.compat import unicode

logger = logging.getLogger(__name__)

COLOR_CODES = {
    "reset": "\033[0m",
    "black": "\033[1;30m",
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[1;34m",
    "magenta": "\033[1;35m",
    "cyan": "\033[1;36m",
    "white": "\033[1;37m",
    "bgred": "\033[1;41m",
    "bggrey": "\033[1;100m",
}


def color_msg(color, msg):
    return COLOR_CODES[color] + msg + COLOR_CODES["reset"]


def check_extension(filename):
    """Check if the file extension is in the allowed extensions

    The `fnmatch` module can also get the suffix:
        patterns = ["*.md", "*.mkd", "*.markdown"]
        fnmatch.filter(files, pattern)
    """
    exts = ['.{0}'.format(e) for e in simiki.allowed_extensions]
    return os.path.splitext(filename)[1] in exts


def copytree(src, dst, symlinks=False, ignore=None):
    """Copy from source directory to destination"""

    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def emptytree(directory, exclude_list=None):
    """Delete all the files and dirs under specified directory"""

    if not isinstance(directory, unicode):
        directory = unicode(directory, 'utf-8')
    if not exclude_list:
        exclude_list = []
    for p in os.listdir(directory):
        if p in exclude_list:
            continue
        fp = os.path.join(directory, p)
        if os.path.isdir(fp):
            try:
                shutil.rmtree(fp)
                logger.debug("Delete directory %s", fp)
            except OSError as e:
                logger.error("Unable to delete directory %s: %s",
                             fp, unicode(e))
        elif os.path.isfile(fp):
            try:
                logging.debug("Delete file %s", fp)
                os.remove(fp)
            except OSError as e:
                logger.error("Unable to delete file %s: %s", fp, unicode(e))
        else:
            logger.error("Unable to delete %s, unknown filetype", fp)


def mkdir_p(path):
    """Make parent directories as needed, like `mkdir -p`"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        # if dir exists, not error
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def listdir_nohidden(path):
    """List not hidden files or directories under path"""
    for f in os.listdir(path):
        if isinstance(f, str):
            f = unicode(f)
        if not f.startswith('.'):
            yield f


def write_file(filename, content):
    """Write content to file."""
    _dir, _ = os.path.split(filename)
    if not os.path.exists(_dir):
        logging.debug("The directory %s not exists, create it", _dir)
        mkdir_p(_dir)
    with io.open(filename, "wt", encoding="utf-8") as fd:
        fd.write(content)


def get_md5(filename):
    # py3 require md5 with bytes object, otherwise raise
    # TypeError: Unicode-objects must be encoded before hashing
    with open(filename, 'rb') as fd:
        md5_hash = hashlib.md5(fd.read()).hexdigest()
    return md5_hash


def get_dir_md5(dirname):
    """Get md5 sum of directory"""
    md5_hash = hashlib.md5()
    for root, dirs, files in os.walk(dirname):
        # os.walk use os.listdir and return arbitrary order list
        # sort list make it get same md5 hash value
        dirs[:] = sorted(dirs)
        for f in sorted(files):
            with open(os.path.join(root, f), 'rb') as fd:
                md5_hash.update(fd.read())
    md5_hash = md5_hash.hexdigest()
    return md5_hash


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).
    If `silent` is True the return value will be `None` if the import fails.
    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # ref: https://github.com/pallets/werkzeug/blob/master/werkzeug/utils.py

    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        if not silent:
            raise ImportError(e)


if __name__ == "__main__":
    print(color_msg("black", "Black"))
    print(color_msg("red", "Red"))
    print(color_msg("green", "Green"))
    print(color_msg("yellow", "Yellow"))
    print(color_msg("blue", "Blue"))
    print(color_msg("magenta", "Magenta"))
    print(color_msg("cyan", "Cyan"))
    print(color_msg("white", "White"))
    print(color_msg("bgred", "Background Red"))
    print(color_msg("bggrey", "Background Grey"))
