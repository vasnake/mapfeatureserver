#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

""" Flask web app default settings for Map Feature Server

"""

#import os, ConfigParser

CP = 'utf-8'

# path to folder with service data files, like config/layer.0.config.json and so on
DATA_FILES_ROOTDIR = r'''c:/d/code/git/mapfeatureserver'''

# only one DB connection availible for now. Default is
#DSN = "host=vags101 port=5432 dbname=postgisdb user=mfs password=12345678 connect_timeout=10 client_encoding=utf8"
#DSN = INI.get('common', 'DSN')

# debug logfile
LOGFILENAME = r'''c:/d/code/git/mapfeatureserver/wsgi/mapfs_controller.log'''

# auth options
SECRET_KEY = "12345678"
SESSION_PROTECTION = 'strong'
