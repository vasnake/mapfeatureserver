#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r"""
Apache HTTPD mod_wsgi mapfeatureserver app

http://code.google.com/p/modwsgi/wiki/InstallationOnWindows
http://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines
http://flask.pocoo.org/docs/deploying/mod_wsgi/

httpd.conf
    WSGIScriptAlias "/mapfeatureserver" "c:/d/code/git/mapfeatureserver/mfs.wsgi"
    <Directory "c:/d/code/git/mapfeatureserver">
        Options None
        AllowOverride All
        Order allow,deny
        Allow from all
    </Directory>

.htaccess contents
    Options None
    Order allow,deny
    Allow from all
    RewriteEngine Off
    RemoveHandler .py
    <FilesMatch "\.(pyo|pyc|py|html|log)$">
        SetHandler None
        Order deny,allow
        Deny from all
    </FilesMatch>
    LimitRequestBody 10485760
    AddDefaultCharset utf-8
    WSGIScriptReloading On
    SetEnv map.fs.mailhost mail.algis.com

"""

# mod_wsgi env. setup

# virtualenv activation
activate_this = 'c:/d/code/git/mapfeatureserver/env/Scripts/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# for developer
# if mapfeatureserver package not installed but lay down along with mfs.wsgi file
import os, sys
pth = os.path.dirname(__file__)
if pth not in sys.path:
    sys.path.insert(0, pth)

# application

# get mod_wsgi application from Flask module
from mapfeatureserver.mfsapp import APP as application
