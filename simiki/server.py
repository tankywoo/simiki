#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import os
import os.path
import sys
import logging
import traceback

try:
    import SimpleHTTPServer as http_server
except ImportError:
    # py3
    import http.server as http_server

try:
    import SocketServer as socket_server
except ImportError:
    # py3
    import socketserver as socket_server

try:
    import urllib2 as urllib_request
except ImportError:
    # py3
    import urllib.request as urllib_request

try:
    from os import getcwdu
except ImportError:
    # py3
    from os import getcwd as getcwdu

URL_ROOT = None
PUBLIC_DIRECTORY = None


class Reuse_TCPServer(socket_server.TCPServer):
    allow_reuse_address = True


class YARequestHandler(http_server.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        if URL_ROOT and self.path.startswith(URL_ROOT):
            if self.path == URL_ROOT or self.path == URL_ROOT + '/':
                return PUBLIC_DIRECTORY + '/index.html'
            else:
                return PUBLIC_DIRECTORY + path[len(URL_ROOT):]
        else:
            return http_server.SimpleHTTPRequestHandler \
                .translate_path(self, path)

    def do_GET(self):
        # redirect url
        if URL_ROOT and not self.path.startswith(URL_ROOT):
            self.send_response(301)
            self.send_header('Location', URL_ROOT + self.path)
            self.end_headers()
        http_server.SimpleHTTPRequestHandler.do_GET(self)


def preview(path, url_root, host='127.0.0.1', port=8000):
    '''
    :param path: directory path relative to current path
    :param url_root: `root` setted in _config.yml
    '''
    global URL_ROOT, PUBLIC_DIRECTORY

    if not host:
        host = '127.0.0.1'
    if not port:
        port = 8000

    if url_root.endswith('/'):
        url_root = url_root[:-1]

    URL_ROOT = urllib_request.quote(url_root.encode('utf-8'))
    PUBLIC_DIRECTORY = os.path.join(getcwdu(), path)

    if os.path.exists(path):
        os.chdir(path)
    else:
        logging.error("Path {} not exists".format(path))
    try:
        Handler = YARequestHandler
        httpd = Reuse_TCPServer((host, port), Handler)
    except (OSError, IOError) as e:
        logging.error("Could not listen on port {0}\n{1}"
                      .format(port, traceback.format_exc()))
        sys.exit(getattr(e, 'exitcode', 1))

    logging.info("Serving at: http://{0}:{1}{2}/".format(host, port, url_root))
    logging.info("Serving running... (Press CTRL-C to quit)")
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down server")
        httpd.socket.close()
