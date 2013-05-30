#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Flask web app for Map Feature Server.
Free featureserver realization for Esri REST API
http://resources.arcgis.com/en/help/rest/apiref/index.html?featureserver.html

f=json by default

For now MFS opens only one DB connection and only to PostGIS DB.

http://flask.pocoo.org/docs/quickstart/#quickstart

$ set path=%path%;c:\d\Python27;c:\d\Python27\Scripts
$ pip install Flask flask-login blinker psycopg2 simplejson

psycopg2 for Windows http://www.stickpeople.com/projects/python/win-psycopg/

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

import os, sys
import logging
import simplejson
import traceback

from flask import (Flask, url_for, render_template, make_response, request,
    flash, send_from_directory)
# from flask import (redirect, session, abort, request_started)

# pylint warning on this: from flask.ext.login import (LoginManager, current_user, login_required,
#from flask_login import (LoginManager, current_user, login_required, login_user,
#   logout_user, confirm_login, fresh_login_required)

import layermeta, layerdata, mfslib, esri
import postgis
import flask_gs

################################################################################

# app setup

CP = 'utf-8'
APP = Flask(__name__)
APP.config.from_object('default_settings')
LOG = APP.logger
#PGCONN = mfslib.getPGConnection(APP)
GS = flask_gs.VGlobalStorage(APP)

################################################################################

# pages


@APP.route('/')
def mainPage():
    """ List of all MFS servlets, for demo purposes only
    """
    lst = []
    for x in ('mainPage', 'helpPage', 'favicon', 'clientaccesspolicy'):
        lst.append(url_for(x))

    ini = mfslib.getIniData(APP)
    lyrs = mfslib.getLyrsList(ini)
    for lyrid in lyrs:
        tabname = ini.get(lyrid, 'layer.table')
        fldname = ini.get(lyrid, 'layer.geomfield')
        oidname = ini.get(lyrid, 'layer.oidfield')

        lst.append(url_for('layerController', layerid=lyrid))
        lst.append(url_for('layerOperations', layerid=lyrid, operation='query',
            geometry='{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}',
            outSR='102100',
#             returnGeometry='true',
#             geometryType='esriGeometryEnvelope',
#             inSR='102100',
#             spatialRel='esriSpatialRelIntersects',
#             outFields='*',
#             f='pjson'
        ))
        lst.append(url_for('dbTableInfo', table=tabname, geomfield=fldname, oidfield=oidname))

    return render_template('servlets.html', lst=lst)
#def mainPage():


@APP.route('/help')
def helpPage():
    """ Show info page about service
    """
    return render_template("help.html")


@APP.route('/<int:layerid>')
def layerController(layerid=0):
    """ Esri API, process requests to layer by Layer ID
    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html

    Known requests example
    .../FeatureServer/0?f=pjson

    f=json by default
    """
    # layer metadata .../FeatureServer/0?f=pjson
    stordir = APP.config['DATA_FILES_ROOTDIR']
    text = layermeta.layerMeta(layerid, stordir)
    resp = make_response(text)
    resp.headers['Content-Type'] = 'text/plain;charset=utf-8'
    return resp
    #return layermeta.layerMeta(layerid)
#def layerController(layerid=0):


@APP.route('/<int:layerid>/<operation>')
def layerOperations(layerid=0, operation=''):
    """ Esri API, process all operations for layer by Layer ID and operation name
    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    Known request example
    .../FeatureServer/0/query?returnGeometry=true
        &geometryType=esriGeometryEnvelope
        &geometry={"xmin":-7182265.21424325,"ymin":-1567516.84684806,"xmax":17864620.2142433,"ymax":14321601.0968481,"spatialReference":{"wkid":102100}}
        &inSR=102100
        &spatialRel=esriSpatialRelIntersects
        &outSR=102100
        &outFields=*
        &f=pjson

    f=pjson by default
    """
    ini = mfslib.getIniData(APP)
    lyrs = mfslib.getLyrsList(ini)

    if not (str(layerid) in lyrs and operation == 'query'):
        resp = esri.errorObject(
            details=u"Unsupported query parameters: layerid not in %s or operation != 'query'" % lyrs)
        return makeResponce(resp)

    lyrconf = getLayerConfig(str(layerid))
    if not lyrconf.isValid():
        resp = esri.errorObject(details=u"Layer config not found.")
        return makeResponce(resp)

    ds = getDataSource()

    op = esri.getLyrOperation(operation, request.values)

    try:
        resp = layerdata.layerData(lyrconf, ds, op)
    except Exception, e:
        traceback.print_exc(file=sys.stderr)
#        trb = traceback.format_exc()
        resp = esri.errorObject(details=u"Data processing error: %s" % e)
    return makeResponce(resp)
#def layerOperations(layerid=0, operation=''):


@APP.route('/admin/dsn/<table>')
def dbTableInfo(table):
    """ Admin page, info from DB.
    Extract from DB all availible metadata
    """
    flds = ext = u"n/a"

    oidfield = request.args.get('oidfield', 'OBJECTID')
    geomfield = request.args.get('geomfield', 'Shape')
    ds = getDataSource()  # pg connection.cursor
    try:
        ext = layermeta.getExtent(ds, table, geomfield)
        flds = layermeta.getFields(ds, table, oidfield)
    except Exception, e:
        traceback.print_exc(file=sys.stderr)
        msg = u"SQL error: %s" % e
        flash(msg)

    return render_template("dbTableInfo.html", extent=ext, fields=flds)
#def dbTableInfo(dsn, table, geomfield):


@APP.route('/favicon.ico')
def favicon():
    """ In debug mode, send favicon
    """
    return sendStatic('favicon.ico', 'image/vnd.microsoft.icon')


@APP.route('/clientaccesspolicy.xml')
def clientaccesspolicy():
    """ In debug mode, send clientaccesspolicy.xml
    """
    return sendStatic('clientaccesspolicy.xml', 'text/xml')

################################################################################


def sendStatic(filename, mimetype):
    """ send file from app 'static' folder
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'),
       filename, mimetype=mimetype)


def makeResponce(data, frmt='pjson'):
    """ Return Flask responce with data formatted as frmt specified.

    Args:
        data: dictionary with responce data;
        frmt: string, format spec like 'json', 'pjson';
    """
    if not frmt in('pjson', 'json'):
        raise ValueError('format must be json or pjson')

#    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    text = simplejson.dumps(data, ensure_ascii=False, sort_keys=True, indent=2,
        default=mfslib.jsonify, use_decimal=False)

    resp = make_response(text)
    resp.headers['Content-Type'] = 'text/plain;charset=utf-8'
    return resp
#def makeResponce(data, frmt):


def getLayerConfig(lyrid):
    """ Return layermeta.LayerInfo readed from ini file and layer metadata file
    Args:
        lyrid: string, ini section name
    """
    ini = mfslib.getIniData(APP)
    tabname = ini.get(lyrid, 'layer.table')
    geomfield = ini.get(lyrid, 'layer.geomfield')
    oidfield = ini.get(lyrid, 'layer.oidfield')
    res = layermeta.LayerInfo(tabname, geomfield, oidfield)

    stordir = APP.config['DATA_FILES_ROOTDIR']
    text = layermeta.layerMeta(lyrid, stordir)
    res.setAGInfo(text)

    return res
#def getLayerConfig(layerid):


def getDataSource():
    """ Return IDataSource

    TODO: must return actual DataSource
    """
    conn = GS.getData('PGCONN')  # http://initd.org/psycopg/docs/usage.html#thread-safety
#    assert isinstance(conn, postgis.PGConnection)
    if not conn:
        ini = mfslib.getIniData(APP)
        dsn = ini.get('common', 'PG.DSN')
        conn = postgis.PGConnection(dsn, APP)
        GS.setData('PGCONN', conn)

    return postgis.DataSource(conn.conn)
#    return postgis.DataSource(PGCONN.connection)
#def getDataSource():


def setLogger(log):
    ''' debug logger, http://docs.python.org/howto/logging-cookbook.html

    logrotate
    http://stackoverflow.com/questions/8467978/python-want-logging-with-log-rotation-and-compression
    http://docs.python.org/library/logging.handlers.html#rotatingfilehandler
    '''
    logFilename = APP.config['LOGFILENAME']
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not hasattr(log, 'vFHandle'):
        #~ import logging.handlers as handlers
        # 5 files up to 1 megabyte each
        #~ fh = handlers.RotatingFileHandler(logFilename, maxBytes=1000000, backupCount=5, encoding='utf-8')
        #~ fh = handlers.TimedRotatingFileHandler(logFilename, backupCount=3, when='M', interval=3, encoding='utf-8',)
        fh = logging.FileHandler(logFilename)
        #~ fh = logging.NullHandler()
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        log.vFHandle = fh
#def setLogger(log):


if __name__ == '__main__':
    setLogger(LOG)
    APP.logger.debug('app started')
    APP.run(host='0.0.0.0', debug=True, threaded=True)
