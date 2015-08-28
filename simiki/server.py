#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import os
import os.path
import sys
import logging
import SimpleHTTPServer
import SocketServer
import urllib2


URL_ROOT = None
PUBLIC_DIRECTORY = None


class Reuse_TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True


class YARequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        if URL_ROOT and self.path.startswith(URL_ROOT):
            if self.path == URL_ROOT or self.path == URL_ROOT + '/':
                return PUBLIC_DIRECTORY + '/index.html'
            else:
                return PUBLIC_DIRECTORY + path[len(URL_ROOT):]
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler \
                                   .translate_path(self, path)

    def do_GET(self):
        # redirect url
        if URL_ROOT and not self.path.startswith(URL_ROOT):
            self.send_response(301)
            self.send_header('Location', URL_ROOT + self.path)
            self.end_headers()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


def preview(path, url_root, host='localhost', port=8000):
    '''
    :param path: directory path relative to current path
    :param url_root: `root` setted in _config.yml
    '''
    global URL_ROOT, PUBLIC_DIRECTORY

    if not host:
        host = 'localhost'
    if not port:
        port = 8000

    if url_root.endswith('/'):
        url_root = url_root[:-1]

    URL_ROOT = urllib2.quote(url_root.encode('utf-8'))
    PUBLIC_DIRECTORY = os.path.join(os.getcwdu(), path)

    if os.path.exists(path):
        os.chdir(path)
    else:
        logging.error("Path {} not exists".format(path))
    try:
        Handler = YARequestHandler
        httpd = Reuse_TCPServer((host, port), Handler)
    except OSError as e:
        logging.error("Could not listen on port {0}".format(port))
        sys.exit(getattr(e, 'exitcode', 1))

    logging.info("Serving at: http://{0}:{1}{2}/".format(host, port, url_root))
    logging.info("Serving running... (Press CTRL-C to quit)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server")
        httpd.socket.close()
