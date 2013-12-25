#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import logging
import SimpleHTTPServer
import SocketServer

PORT = len(sys.argv) == 2 and int(sys.argv[1]) or 8000

try:
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
except OSError as e:
    logging.error("Could not listen on port %s" % PORT)
    sys.exit(getattr(e, 'exitcode', 1))


logging.info("serving at port %s" % PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt as e:
    logging.info("shutting down server")
    httpd.socket.close()
