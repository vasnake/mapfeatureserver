#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Map Feature Server lib module.

Copyright 2012-2013 Valentin Fedulov

This file is part of Mapfeatureserver.

Mapfeatureserver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mapfeatureserver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Mapfeatureserver.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import ConfigParser, io
import decimal
import datetime

EPOCH = datetime.datetime.utcfromtimestamp(0)


class IDataSource(object):
    """ DataSource interface
    """
    def __init__(self):
        pass
# class IDataSource():


def getIniData(app):
    """ Return ConfigParser.ConfigParser() with data from ini file

    Args:
        app: Flask app with config data.
    """
    ini = ConfigParser.ConfigParser()
    ini.read(os.path.join(app.config['DATA_FILES_ROOTDIR'], 'config', 'layers.config.ini'))
    return ini
# def getIniData():


def getLyrsList(ini):
    """ Returns list of layers ID from ini.
    Layer ID is string but can|must be cast to int.

    Args:
        ini: ConfigParser.ConfigParser() with configuration data.
    """
    lyrs = ini.get('common', 'layer.ID.list')
    return splitAndStrip(lyrs, ',')
#def getLyrsList(ini):


def splitAndStrip(datastr, separator):
    """ Split datastr and return list of stripped nonempty items
    """
    res = []
    lyrs = datastr.split(separator)
    for lyrid in lyrs:
        lyrid = lyrid.strip()
        if not lyrid:
            continue
        res.append(lyrid)
    return res
#def splitAndStrip(datastr, separator):


def unix_time_millisec(dt):
    r''' Returns float(milliseconds) from Unix epoch
    http://stackoverflow.com/questions/6999726/python-getting-millis-since-epoch-from-datetime
    '''
    delta = dt - EPOCH
    return delta.total_seconds() * 1000.0
#def unix_time_millisec(dt)


def jsonify(obj):
    """ Helper function for using in simplejson.dumps

    text = simplejson.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, default=jsonify, use_decimal=False)

    Note that date values are encoded as numbers.
    The number represents the number of milliseconds since epoch (January 1, 1970) in UTC.
    http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000n8000000
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.datetime):
        return long(unix_time_millisec(obj))
    raise TypeError(repr(obj) + " is not JSON serializable")
#def jsonify(obj):


def getPGConnection(app):
    """ Obsolete.
    Return Psycopg2 object with db connection prorperty.
    Obj. must be created before first request served.

    Args:
        app: Flask app with config data.
    """
    raise NameError("mfslib.getPGConnection is obsolete")

    ini = getIniData(app)
    dsn = ini.get('common', 'PG.DSN')
#    print "getPGConnection, PG DSN '%s'" % dsn
    return createPsycopg2(app, dsn)
#def getPGConnection():


def createPsycopg2(app, dsn):
    """ Obsolete.
    Return new flask.ext.Psycopg2 object inited from dsn.
    Obj. must be created before first request served.

    Args:
        app: Flask app with config data;
        dsn: PostgreSQL DSN string.
    """
    raise NameError("mfslib.createPsycopg2 is obsolete")

    from flask_psycopg2 import Psycopg2
#     always unicode output from psycopg2
    import psycopg2.extensions
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

    ini = ('[dsn] ' + dsn).replace(' ', '\n')
    cfg = ConfigParser.ConfigParser()
    cfg.readfp(io.BytesIO(ini))
    opt = lambda x: cfg.get('dsn', x)

    return Psycopg2(app, host=opt('host'), port=opt('port'), dbname=opt('dbname'),
        user=opt('user'), password=opt('password'),
        connect_timeout=opt('connect_timeout'), client_encoding=opt('client_encoding'))
#def createPsycopg2(app, dsn):
