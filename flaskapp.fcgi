#!/usr/home/civfrd/virtualenvs/example_com/bin/python

import sys
from flup.server.fcgi import WSGIServer
sys.path.append('/usr/home/civfrd/public_html/civfrdata')
from main import app

class ScriptNameStripper(object):
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    environ['SCRIPT_NAME'] = ''
    return self.app(environ, start_response)

app = ScriptNameStripper(app)

WSGIServer(app).run()
