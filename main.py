#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       main.py
#       
#       Copyright 2011 Di SONG <di@di-debian>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


import os
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options

os.environ['PYTHON_EGG_CACHE'] = '/tmp'
from tornadobb.settings import *

handlers = []
handlers = handlers + tornadobb_handlers

settings = dict(
            cookie_secret = "43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            xsrf_cookies = True,
            autoescape = "xhtml_escape",

        )

settings = dict(settings, **tornadobb_settings)


define("port", default=8000, help="run on the given port", type=int)
define('debug',default=False,help='run in debug mode with autoreload (default: false)',type=bool)


if __name__ == "__main__":
	
	tornado.options.parse_command_line()
	application = tornado.web.Application(handlers,**settings)
	http_server = tornado.httpserver.HTTPServer(application,xheaders=True)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

