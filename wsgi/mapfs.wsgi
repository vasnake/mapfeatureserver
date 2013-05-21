#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r"""
Apache HTTPD mod_wsgi app

http://code.google.com/p/modwsgi/wiki/InstallationOnWindows
http://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines
http://flask.pocoo.org/docs/deploying/mod_wsgi/

httpd.conf
	WSGIScriptAlias "/mapfeatureserver" "c:/Inetpub/wwwroot/mapfeatureserver/wsgi/mapfs.wsgi"
	<Directory "c:/Inetpub/wwwroot/mapfeatureserver">
		Options Indexes FollowSymLinks
		AllowOverride All
		Order allow,deny
		Allow from all
	</Directory>
	Alias "/mapfeatureserver.container" "c:/Inetpub/wwwroot/mapfeatureserver"
	# skip proxy for IIS
	RewriteRule ^/mapfeatureserver(.*)$ /mapfeatureserver$1 [L,PT]

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

import os, sys

#~ pth = r'c:/Inetpub/wwwroot/mapfeatureserver/wsgi'
pth = os.path.dirname(__file__)
if pth not in sys.path:
	sys.path.insert(0, pth)

# get modwsgi application from Flask module
#~ from test import app as application
from mapfs_controller import APP as application
